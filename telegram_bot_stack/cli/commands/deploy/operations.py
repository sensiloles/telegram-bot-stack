"""Deployment operations (up, update, down)."""

import shutil
from pathlib import Path
from typing import Any, Optional

import click
from rich.console import Console

from telegram_bot_stack.cli.utils.backup import BackupManager
from telegram_bot_stack.cli.utils.deployment import (
    DeploymentConfig,
    DockerTemplateRenderer,
    SystemdTemplateRenderer,
    create_env_file,
)
from telegram_bot_stack.cli.utils.secrets import SecretsManager
from telegram_bot_stack.cli.utils.version_tracking import VersionTracker
from telegram_bot_stack.cli.utils.vps import VPSConnection

console = Console()


@click.command()
@click.option("--config", default="deploy.yaml", help="Deployment config file")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def up(config: str, verbose: bool) -> None:
    """Deploy bot to VPS."""
    console.print("🚀 [bold cyan]Deploying bot to VPS...[/bold cyan]\n")

    # Load configuration
    if not Path(config).exists():
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        console.print("\n[yellow]Run 'telegram-bot-stack deploy init' first[/yellow]")
        return

    deploy_config = DeploymentConfig(config)

    if not deploy_config.validate():
        console.print("[red]❌ Invalid configuration[/red]")
        return

    # Connect to VPS
    console.print("[cyan]🔧 Connecting to VPS...[/cyan]")
    vps = VPSConnection(
        host=deploy_config.get("vps.host"),
        user=deploy_config.get("vps.user"),
        ssh_key=deploy_config.get("vps.ssh_key"),
        port=deploy_config.get("vps.port", 22),
    )

    try:
        if not vps.test_connection():
            console.print("[red]❌ Failed to connect to VPS[/red]")
            return

        console.print("[green]✓ Connected to VPS[/green]\n")

        # Get deployment method from config
        deployment_method = deploy_config.get("deployment.method", "docker")
        console.print(f"[cyan]📋 Deployment method: {deployment_method}[/cyan]\n")

        # Get minimum Python version from config or use default
        min_python_version = deploy_config.get("bot.python_version", "3.9")
        if isinstance(min_python_version, str) and min_python_version.startswith("3."):
            # Extract major.minor (e.g., "3.11" from "3.11.0")
            min_python_version = ".".join(min_python_version.split(".")[:2])

        # Validate VPS requirements and install dependencies
        if not vps.validate_vps_requirements(deployment_method, min_python_version):
            console.print("[red]❌ VPS validation failed[/red]")
            return

        # Prepare deployment directory
        bot_name = deploy_config.get("bot.name")
        remote_dir = f"/opt/{bot_name}"

        console.print(f"[cyan]📦 Preparing deployment directory: {remote_dir}[/cyan]")
        vps.run_command(f"mkdir -p {remote_dir}")

        # Generate deployment files from templates based on method
        if deployment_method == "docker":
            console.print("[cyan]📝 Generating Docker configuration...[/cyan]")
        elif deployment_method == "systemd":
            console.print("[cyan]📝 Generating systemd configuration...[/cyan]")
        else:
            console.print(
                f"[red]❌ Unknown deployment method: {deployment_method}[/red]"
            )
            console.print("[yellow]Supported methods: docker, systemd[/yellow]")
            return

        temp_dir = Path(".deploy-temp")
        temp_dir.mkdir(exist_ok=True)

        try:
            # Check if secrets exist before rendering templates
            # This determines whether .secrets.env should be included in docker-compose.yml
            encryption_key = deploy_config.get("secrets.encryption_key")
            has_secrets = False
            secrets_manager = None

            if encryption_key:
                secrets_manager = SecretsManager(bot_name, remote_dir, encryption_key)
                # Check if secrets exist (without decrypting)
                encrypted_secrets = secrets_manager.list_secrets(
                    vps, return_values=False
                )
                has_secrets = len(encrypted_secrets) > 0

            # Render templates based on deployment method
            if deployment_method == "docker":
                docker_renderer = DockerTemplateRenderer(
                    deploy_config, has_secrets=has_secrets
                )
                docker_renderer.render_all(temp_dir)
                console.print("[green]✓ Docker configuration generated[/green]\n")
            elif deployment_method == "systemd":
                systemd_renderer = SystemdTemplateRenderer(
                    deploy_config, has_secrets=has_secrets
                )
                systemd_renderer.render_all(temp_dir)
                console.print("[green]✓ systemd configuration generated[/green]\n")

            # Create .env file (secrets will be loaded from .secrets.env on VPS)
            env_file = temp_dir / ".env"
            create_env_file(deploy_config, env_file, secrets_manager, vps)

            # Transfer files to VPS
            console.print("[cyan]📤 Transferring files to VPS...[/cyan]")

            # Copy current directory files to temp
            for item in Path.cwd().iterdir():
                if item.name not in [
                    ".git",
                    ".venv",
                    "venv",
                    "__pycache__",
                    ".deploy-temp",
                    "logs",
                    ".pytest_cache",
                    "htmlcov",
                    ".secrets.env",  # Exclude - encrypted version exists on VPS
                ]:
                    if item.is_file():
                        shutil.copy2(item, temp_dir)
                    elif item.is_dir():
                        shutil.copytree(item, temp_dir / item.name, dirs_exist_ok=True)

            # Transfer to VPS
            if not vps.transfer_files(temp_dir, remote_dir):
                console.print("[red]❌ Failed to transfer files[/red]")
                return

            console.print("[green]✓ Files transferred[/green]\n")

            # Deploy based on method
            if deployment_method == "docker":
                success = _deploy_docker(
                    vps,
                    deploy_config,
                    bot_name,
                    remote_dir,
                    has_secrets,
                    encryption_key,
                )
            elif deployment_method == "systemd":
                success = _deploy_systemd(
                    vps,
                    deploy_config,
                    bot_name,
                    remote_dir,
                    has_secrets,
                    encryption_key,
                )
            else:
                console.print(
                    f"[red]❌ Unknown deployment method: {deployment_method}[/red]"
                )
                return

            if not success:
                return

            # Show status
            console.print("[cyan]📊 Checking bot status...[/cyan]")
            if deployment_method == "docker":
                vps.run_command(f"cd {remote_dir} && make status")
            elif deployment_method == "systemd":
                vps.run_command(f"systemctl status {bot_name} --no-pager -l")

            console.print("\n[green]🎉 Deployment successful![/green]\n")
            console.print("[bold]Bot Information:[/bold]")
            console.print(f"  Name: {bot_name}")
            console.print(f"  Host: {deploy_config.get('vps.host')}")
            console.print(f"  Directory: {remote_dir}")
            console.print(f"  Method: {deployment_method}")
            console.print("\n[bold]Useful commands:[/bold]")
            console.print("  View logs:   [cyan]telegram-bot-stack deploy logs[/cyan]")
            console.print(
                "  Check status: [cyan]telegram-bot-stack deploy status[/cyan]"
            )
            console.print("  Stop bot:    [cyan]telegram-bot-stack deploy down[/cyan]")

        finally:
            # Cleanup temp directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    finally:
        # Always close VPS connection
        vps.close()


def _deploy_docker(
    vps: Any,
    deploy_config: DeploymentConfig,
    bot_name: str,
    remote_dir: str,
    has_secrets: bool,
    encryption_key: Optional[str],
) -> bool:
    """Deploy bot using Docker.

    Args:
        vps: VPSConnection instance
        deploy_config: Deployment configuration
        bot_name: Bot name
        remote_dir: Remote directory path
        has_secrets: Whether secrets are configured
        encryption_key: Encryption key for secrets

    Returns:
        True if successful, False otherwise
    """
    # Create decryption script that decrypts secrets in-memory during container startup
    # This ensures secrets remain encrypted at rest on VPS filesystem
    encryption_key_str = encryption_key if encryption_key else ""
    encryption_key_escaped = encryption_key_str.replace("\\", "\\\\").replace(
        '"', '\\"'
    )

    decrypt_script = f"""#!/usr/bin/env python3
\"\"\"
Decrypt secrets in-memory and output as environment variables.
This script is executed during container startup to decrypt secrets
without writing plain text to the filesystem.
\"\"\"
import os
import sys
from pathlib import Path

# Import cryptography for decryption
try:
    from cryptography.fernet import Fernet
except ImportError:
    print("# Error: cryptography not available", file=sys.stderr)
    sys.exit(1)

def decrypt_secrets():
    \"\"\"Decrypt secrets from encrypted file and output as env file format.\"\"\"
    remote_dir = "{remote_dir}"
    secrets_file = f"{{remote_dir}}/.secrets.env.encrypted"
    encryption_key = "{encryption_key_escaped}"

    if not encryption_key:
        return

    # Read encrypted secrets file
    if not Path(secrets_file).exists():
        return

    try:
        fernet = Fernet(encryption_key.encode())

        with open(secrets_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if "=" in line:
                    key, encrypted_value = line.split("=", 1)
                    key = key.strip()
                    encrypted_value = encrypted_value.strip()

                    try:
                        decrypted_value = fernet.decrypt(encrypted_value.encode()).decode()
                        # Output as KEY=VALUE (properly escaped for .env file format)
                        needs_quoting = any(
                            char in decrypted_value
                            for char in ["\\n", "\\r", "\\t", '"', "\\\\", " ", "#", "=", "$", "`"]
                        )

                        if needs_quoting:
                            temp_val = decrypted_value.replace("\\\\", "\\\\\\\\")
                            temp_val = temp_val.replace('"', '\\\\"')
                            temp_val = temp_val.replace("\\n", "\\\\n")
                            temp_val = temp_val.replace("\\r", "\\\\r")
                            temp_val = temp_val.replace("\\t", "\\\\t")
                            temp_val = temp_val.replace("$", "\\\\$")
                            temp_val = temp_val.replace("`", "\\\\`")
                            output_value = '"' + temp_val + '"'
                        else:
                            output_value = decrypted_value
                        print("{{}}={{}}".format(key, output_value))
                    except Exception as e:
                        print(f"# Warning: Failed to decrypt {{key}}: {{e}}", file=sys.stderr)
    except Exception as e:
        print(f"# Error decrypting secrets: {{e}}", file=sys.stderr)

if __name__ == "__main__":
    decrypt_secrets()
"""

    decrypt_script_path = f"{remote_dir}/decrypt_secrets.py"
    if vps.write_file(decrypt_script, decrypt_script_path, mode="700"):
        console.print("[green]✓ Created secrets decryption script[/green]")
    else:
        console.print("[yellow]⚠️  Warning: Could not create decryption script[/yellow]")

    if has_secrets:
        console.print(
            "[dim]   (Secrets will be decrypted in-memory to shared memory during container startup)[/dim]"
        )

    # Initialize version tracker
    version_tracker = VersionTracker(bot_name, remote_dir)
    git_commit = version_tracker.get_current_git_commit()
    docker_tag = version_tracker.generate_docker_tag(git_commit)

    console.print(f"[dim]   Version: {docker_tag}[/dim]")

    # Build and start bot
    console.print("[cyan]🏗️  Building Docker image...[/cyan]")
    console.print(
        "[yellow]⏳ This may take 5-15 minutes (Docker-in-Docker is slow)...[/yellow]"
    )
    console.print(
        "[dim]   Output will appear when build completes (may be buffered)[/dim]\n"
    )

    # Run build with visible output for progress tracking
    build_success = vps.run_command(
        f"cd {remote_dir} && make build-tag TAG={docker_tag}",
        hide=False,  # Show output for progress visibility
    )

    if not build_success:
        console.print("[red]❌ Failed to build Docker image[/red]")
        version_tracker.add_deployment(vps, docker_tag, status="failed")
        return False

    console.print("\n[green]✓ Docker image built successfully[/green]\n")

    console.print("[cyan]🚀 Starting bot...[/cyan]")
    if not vps.run_command(f"cd {remote_dir} && make up"):
        console.print("[red]❌ Failed to start bot[/red]")
        version_tracker.add_deployment(vps, docker_tag, status="failed")
        return False

    console.print("[green]✓ Bot started[/green]\n")

    # Track successful deployment
    if version_tracker.add_deployment(vps, docker_tag, status="active"):
        console.print("[dim]   Deployment version saved[/dim]")

    # Cleanup old Docker images
    removed = version_tracker.cleanup_old_images(vps)
    if removed > 0:
        console.print(f"[dim]   Cleaned up {removed} old Docker image(s)[/dim]")

    return True


def _deploy_systemd(
    vps: Any,
    deploy_config: DeploymentConfig,
    bot_name: str,
    remote_dir: str,
    has_secrets: bool,
    encryption_key: Optional[str],
) -> bool:
    """Deploy bot using systemd.

    Args:
        vps: VPSConnection instance
        deploy_config: Deployment configuration
        bot_name: Bot name
        remote_dir: Remote directory path
        has_secrets: Whether secrets are configured
        encryption_key: Encryption key for secrets

    Returns:
        True if successful, False otherwise
    """
    # Install Python dependencies
    console.print("[cyan]📦 Installing Python dependencies...[/cyan]")
    python_version = deploy_config.get("bot.python_version", "3.11")
    if isinstance(python_version, str) and python_version.startswith("3."):
        python_version = ".".join(python_version.split(".")[:2])

    requirements_file = f"{remote_dir}/requirements.txt"
    if vps.run_command(f"test -f {requirements_file}"):
        if not vps.run_command(
            f"cd {remote_dir} && python{python_version} -m pip install --user -r requirements.txt"
        ):
            console.print(
                "[yellow]⚠️  Warning: Some dependencies may have failed to install[/yellow]"
            )
    else:
        console.print("[yellow]⚠️  Warning: requirements.txt not found[/yellow]")

    # Install systemd service file
    service_file = f"{remote_dir}/{bot_name}.service"
    systemd_service_path = f"/etc/systemd/system/{bot_name}.service"

    console.print("[cyan]📝 Installing systemd service...[/cyan]")
    if not vps.run_command(f"cp {service_file} {systemd_service_path}"):
        console.print("[red]❌ Failed to copy service file[/red]")
        return False

    # Reload systemd and enable service
    vps.run_command("systemctl daemon-reload")
    vps.run_command(f"systemctl enable {bot_name}")

    # Start service
    console.print("[cyan]🚀 Starting bot service...[/cyan]")
    if not vps.run_command(f"systemctl start {bot_name}"):
        console.print("[red]❌ Failed to start service[/red]")
        return False

    # Check service status
    result = vps.run_command(f"systemctl is-active {bot_name}", hide=True)
    if result:
        console.print("[green]✓ Bot service started[/green]\n")
    else:
        console.print(
            "[yellow]⚠️  Warning: Service may not be running properly[/yellow]"
        )
        console.print("[cyan]   Check logs: systemctl status {bot_name}[/cyan]\n")

    return True


@click.command()
@click.option("--config", default="deploy.yaml", help="Deployment config file")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--backup", is_flag=True, help="Create backup before updating")
@click.option("--no-backup", is_flag=True, help="Skip automatic backup")
def update(config: str, verbose: bool, backup: bool, no_backup: bool) -> None:
    """Update running bot on VPS."""
    console.print("🔄 [bold cyan]Updating bot...[/bold cyan]\n")

    # Load configuration
    if not Path(config).exists():
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        return

    deploy_config = DeploymentConfig(config)

    # Connect to VPS
    vps = VPSConnection(
        host=deploy_config.get("vps.host"),
        user=deploy_config.get("vps.user"),
        ssh_key=deploy_config.get("vps.ssh_key"),
        port=deploy_config.get("vps.port", 22),
    )

    try:
        bot_name = deploy_config.get("bot.name")
        remote_dir = f"/opt/{bot_name}"

        # Initialize version tracker
        version_tracker = VersionTracker(bot_name, remote_dir)
        git_commit = version_tracker.get_current_git_commit()
        docker_tag = version_tracker.generate_docker_tag(git_commit)

        console.print(f"[dim]   New version: {docker_tag}[/dim]")

        # Auto-backup before update (if enabled and not explicitly disabled)
        auto_backup_enabled = deploy_config.get(
            "backup.auto_backup_before_update", True
        )
        if backup or (auto_backup_enabled and not no_backup):
            backup_manager = BackupManager(bot_name, remote_dir)
            backup_manager.create_backup(vps, auto_backup=True)
            console.print()  # Add spacing

        # Transfer updated files
        console.print("[cyan]📤 Transferring updated files...[/cyan]")

        temp_dir = Path(".deploy-temp")
        temp_dir.mkdir(exist_ok=True)

        try:
            # Copy current directory files to temp
            for item in Path.cwd().iterdir():
                if item.name not in [
                    ".git",
                    ".venv",
                    "venv",
                    "__pycache__",
                    ".deploy-temp",
                    "logs",
                    ".pytest_cache",
                    "htmlcov",
                ]:
                    if item.is_file():
                        shutil.copy2(item, temp_dir)
                    elif item.is_dir():
                        shutil.copytree(item, temp_dir / item.name, dirs_exist_ok=True)

            # Transfer to VPS
            if not vps.transfer_files(temp_dir, remote_dir):
                console.print("[red]❌ Failed to transfer files[/red]")
                return

            console.print("[green]✓ Files transferred[/green]\n")

            # Rebuild and restart
            console.print("[cyan]🏗️  Rebuilding Docker image...[/cyan]")
            if not vps.run_command(
                f"cd {remote_dir} && make build-tag TAG={docker_tag}"
            ):
                console.print("[red]❌ Failed to build Docker image[/red]")
                version_tracker.add_deployment(vps, docker_tag, status="failed")
                return

            console.print("[cyan]🔄 Restarting bot...[/cyan]")
            if not vps.run_command(f"cd {remote_dir} && make up"):
                console.print("[red]❌ Failed to restart bot[/red]")
                version_tracker.add_deployment(vps, docker_tag, status="failed")
                return

            # Track successful update
            if version_tracker.add_deployment(vps, docker_tag, status="active"):
                console.print("[dim]   Deployment version saved[/dim]")

            # Cleanup old Docker images
            removed = version_tracker.cleanup_old_images(vps)
            if removed > 0:
                console.print(f"[dim]   Cleaned up {removed} old Docker image(s)[/dim]")

            console.print("\n[green]✅ Bot updated successfully![/green]")

        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    finally:
        vps.close()


@click.command()
@click.option("--config", default="deploy.yaml", help="Deployment config file")
@click.option("--cleanup", is_flag=True, help="Remove container and image")
@click.option("--backup", is_flag=True, help="Create backup before stopping")
@click.option("--no-backup", is_flag=True, help="Skip automatic backup")
def down(config: str, cleanup: bool, backup: bool, no_backup: bool) -> None:
    """Stop bot on VPS."""
    console.print("🛑 [bold cyan]Stopping bot...[/bold cyan]\n")

    # Load configuration
    if not Path(config).exists():
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        return

    deploy_config = DeploymentConfig(config)

    # Connect to VPS
    vps = VPSConnection(
        host=deploy_config.get("vps.host"),
        user=deploy_config.get("vps.user"),
        ssh_key=deploy_config.get("vps.ssh_key"),
        port=deploy_config.get("vps.port", 22),
    )

    try:
        bot_name = deploy_config.get("bot.name")
        remote_dir = f"/opt/{bot_name}"

        # Auto-backup before cleanup (if enabled and not explicitly disabled)
        if cleanup:
            auto_backup_enabled = deploy_config.get(
                "backup.auto_backup_before_cleanup", True
            )
            if backup or (auto_backup_enabled and not no_backup):
                backup_manager = BackupManager(bot_name, remote_dir)
                backup_manager.create_backup(vps, auto_backup=True)
                console.print()  # Add spacing

        # Stop bot
        if cleanup:
            console.print("[cyan]Stopping and removing containers...[/cyan]")
            vps.run_command(f"cd {remote_dir} && make clean")
            console.print("[green]✓ Bot stopped and cleaned up[/green]")
        else:
            console.print("[cyan]Stopping bot...[/cyan]")
            vps.run_command(f"cd {remote_dir} && make down")
            console.print("[green]✓ Bot stopped[/green]")

    finally:
        vps.close()


@click.command()
@click.option("--config", default="deploy.yaml", help="Deployment config file")
@click.option("--version", "-v", help="Specific version to rollback to (Docker tag)")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
def rollback(config: str, version: str, yes: bool) -> None:
    """Rollback to previous deployment version.

    Example:
        # Rollback to previous version
        telegram-bot-stack deploy rollback

        # Rollback to specific version
        telegram-bot-stack deploy rollback --version mybot:v1234567890-abc123
    """
    console.print("🔄 [bold cyan]Rolling back deployment...[/bold cyan]\n")

    # Load configuration
    if not Path(config).exists():
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        return

    deploy_config = DeploymentConfig(config)

    # Connect to VPS
    vps = VPSConnection(
        host=deploy_config.get("vps.host"),
        user=deploy_config.get("vps.user"),
        ssh_key=deploy_config.get("vps.ssh_key"),
        port=deploy_config.get("vps.port", 22),
    )

    try:
        if not vps.test_connection():
            console.print("[red]❌ Failed to connect to VPS[/red]")
            return

        bot_name = deploy_config.get("bot.name")
        remote_dir = f"/opt/{bot_name}"

        # Initialize version tracker
        version_tracker = VersionTracker(bot_name, remote_dir)

        # Get target version
        if version:
            # Rollback to specific version
            target_version = version_tracker.get_version_by_tag(vps, version)
            if not target_version:
                console.print(f"[red]❌ Version not found: {version}[/red]")
                console.print(
                    "\n[yellow]Run 'telegram-bot-stack deploy history' to see available versions[/yellow]"
                )
                return
        else:
            # Rollback to previous version
            target_version = version_tracker.get_previous_version(vps)
            if not target_version:
                console.print("[red]❌ No previous version found for rollback[/red]")
                console.print(
                    "\n[yellow]Run 'telegram-bot-stack deploy history' to see available versions[/yellow]"
                )
                return

        # Show rollback information
        console.print("[bold]Rollback Information:[/bold]")
        console.print(f"  Version: {target_version.docker_tag}")
        console.print(f"  Git Commit: {target_version.git_commit}")
        console.print(f"  Deployed: {target_version.deployed_at}")
        console.print()

        # Confirm rollback
        if not yes:
            from rich.prompt import Confirm

            if not Confirm.ask(
                "[yellow]⚠️  Are you sure you want to rollback?[/yellow]",
                default=False,
            ):
                console.print("[yellow]Rollback cancelled[/yellow]")
                return

        # Create backup before rollback
        console.print("[cyan]📦 Creating backup before rollback...[/cyan]")
        backup_manager = BackupManager(bot_name, remote_dir)
        backup_manager.create_backup(vps, auto_backup=True)
        console.print()

        # Stop current bot
        console.print("[cyan]🛑 Stopping current bot...[/cyan]")
        vps.run_command(f"cd {remote_dir} && make down")

        # Update docker-compose to use old image
        console.print(
            f"[cyan]🔄 Switching to version {target_version.docker_tag}...[/cyan]"
        )

        # Tag the old image as latest
        if not vps.run_command(
            f"docker tag {target_version.docker_tag} {bot_name}:latest"
        ):
            console.print("[red]❌ Failed to switch image tag[/red]")
            console.print(
                "[yellow]⚠️  Image may have been removed. Try specifying a version that exists.[/yellow]"
            )
            return

        # Start bot with rolled back version
        console.print("[cyan]🚀 Starting bot with previous version...[/cyan]")
        if not vps.run_command(f"cd {remote_dir} && make up"):
            console.print("[red]❌ Failed to start bot[/red]")
            return

        console.print("[green]✓ Bot started with previous version[/green]\n")

        # Update version status
        version_tracker.mark_version_status(
            vps, target_version.docker_tag, status="active"
        )
        console.print("[dim]   Version status updated[/dim]")

        # Show status
        console.print("[cyan]📊 Checking bot status...[/cyan]")
        vps.run_command(f"cd {remote_dir} && make status")

        console.print("\n[green]✅ Rollback successful![/green]\n")
        console.print("[bold]Useful commands:[/bold]")
        console.print("  View logs:   [cyan]telegram-bot-stack deploy logs[/cyan]")
        console.print("  Check status: [cyan]telegram-bot-stack deploy status[/cyan]")
        console.print("  View history: [cyan]telegram-bot-stack deploy history[/cyan]")

    finally:
        vps.close()


@click.command()
@click.option("--config", default="deploy.yaml", help="Deployment config file")
@click.option("--limit", "-n", default=10, help="Number of versions to show")
def history(config: str, limit: int) -> None:
    """Show deployment history.

    Example:
        telegram-bot-stack deploy history
    """
    console.print("📜 [bold cyan]Deployment History[/bold cyan]\n")

    # Load configuration
    if not Path(config).exists():
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        return

    deploy_config = DeploymentConfig(config)

    # Connect to VPS
    vps = VPSConnection(
        host=deploy_config.get("vps.host"),
        user=deploy_config.get("vps.user"),
        ssh_key=deploy_config.get("vps.ssh_key"),
        port=deploy_config.get("vps.port", 22),
    )

    try:
        if not vps.test_connection():
            console.print("[red]❌ Failed to connect to VPS[/red]")
            return

        bot_name = deploy_config.get("bot.name")
        remote_dir = f"/opt/{bot_name}"

        # Load deployment history
        version_tracker = VersionTracker(bot_name, remote_dir)
        versions = version_tracker.load_history(vps)

        if not versions:
            console.print("[yellow]No deployment history found[/yellow]")
            console.print("\n[dim]Deploy your bot to start tracking versions:[/dim]")
            console.print("[cyan]telegram-bot-stack deploy up[/cyan]")
            return

        # Show versions
        from rich.table import Table

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Status", width=12)
        table.add_column("Docker Tag", width=35)
        table.add_column("Git Commit", width=10)
        table.add_column("Deployed At", width=20)

        for version in versions[:limit]:
            # Add status emoji
            status_display = {
                "active": "✅ Active",
                "old": "📦 Old",
                "failed": "❌ Failed",
                "rolled_back": "🔄 Rolled Back",
            }.get(version.status, version.status)

            table.add_row(
                status_display,
                version.docker_tag,
                version.git_commit,
                version.deployed_at,
            )

        console.print(table)
        console.print(
            f"\n[dim]Showing {min(len(versions), limit)} of {len(versions)} versions[/dim]"
        )

        # Show rollback hint
        if len(versions) > 1:
            console.print("\n[bold]Rollback commands:[/bold]")
            console.print(
                "  Previous version: [cyan]telegram-bot-stack deploy rollback[/cyan]"
            )
            console.print(
                "  Specific version: [cyan]telegram-bot-stack deploy rollback --version <tag>[/cyan]"
            )

    finally:
        vps.close()
