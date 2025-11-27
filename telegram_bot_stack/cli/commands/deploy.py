"""
VPS deployment commands for telegram-bot-stack.

Provides one-command deployment to VPS with Docker.
"""

import shutil
from pathlib import Path

import click
from rich.console import Console
from rich.prompt import Confirm, Prompt

from telegram_bot_stack.cli.utils.backup import BackupManager
from telegram_bot_stack.cli.utils.deployment import DeploymentConfig
from telegram_bot_stack.cli.utils.secrets import SecretsManager
from telegram_bot_stack.cli.utils.vps import VPSConnection

console = Console()


@click.group()
def deploy() -> None:
    """Deploy bot to VPS (production deployment)."""
    pass


@deploy.command()
@click.option("--host", help="VPS hostname or IP address")
@click.option("--user", default="root", help="SSH user (default: root)")
@click.option("--ssh-key", help="Path to SSH private key")
@click.option("--port", default=22, help="SSH port (default: 22)")
@click.option("--bot-name", help="Bot name (for container/image names)")
@click.option("--bot-token-env", default="BOT_TOKEN", help="Bot token env var name")
def init(
    host: str, user: str, ssh_key: str, port: int, bot_name: str, bot_token_env: str
) -> None:
    """Initialize deployment configuration (interactive setup)."""
    console.print("🚀 [bold cyan]VPS Deployment Setup[/bold cyan]\n")

    # Check if deploy.yaml already exists
    if Path("deploy.yaml").exists():
        if not Confirm.ask(
            "[yellow]deploy.yaml already exists. Overwrite?[/yellow]", default=False
        ):
            console.print("[yellow]Setup cancelled[/yellow]")
            return

    # Interactive prompts if values not provided
    if not host:
        host = Prompt.ask("VPS Host (hostname or IP)")

    if not user:
        user = Prompt.ask("SSH User", default="root")

    if not ssh_key:
        default_key = "~/.ssh/id_rsa"
        ssh_key = Prompt.ask("SSH Key Path", default=default_key)

    if not bot_name:
        # Try to detect bot name from current directory
        default_name = Path.cwd().name
        bot_name = Prompt.ask("Bot Name", default=default_name)

    # Test SSH connection
    console.print("\n[cyan]Testing SSH connection...[/cyan]")
    vps = VPSConnection(host=host, user=user, ssh_key=ssh_key, port=port)

    try:
        if not vps.test_connection():
            console.print("[red]❌ SSH connection failed[/red]")
            console.print(
                "\n[yellow]Please check your VPS details and SSH key permissions[/yellow]"
            )
            return

        console.print("[green]✓ SSH connection successful[/green]")
    finally:
        # Always close VPS connection
        vps.close()

    # Create deployment configuration
    config = DeploymentConfig("deploy.yaml")
    config.set("vps.host", host)
    config.set("vps.user", user)
    config.set("vps.ssh_key", ssh_key)
    config.set("vps.port", port)
    config.set("bot.name", bot_name)
    config.set("bot.token_env", bot_token_env)
    config.set("bot.entry_point", "bot.py")
    config.set("bot.python_version", "3.11")
    config.set("deployment.method", "docker")
    config.set("deployment.auto_restart", True)
    config.set("deployment.log_rotation", True)
    config.set("resources.memory_limit", "256M")
    config.set("resources.memory_reservation", "128M")
    config.set("resources.cpu_limit", "0.5")
    config.set("resources.cpu_reservation", "0.25")
    config.set("logging.level", "INFO")
    config.set("logging.max_size", "5m")
    config.set("logging.max_files", "5")
    config.set("environment.timezone", "UTC")

    # Generate encryption key for secrets management
    encryption_key = SecretsManager.generate_key()
    config.set("secrets.encryption_key", encryption_key)

    # Backup configuration
    config.set("backup.enabled", True)
    config.set("backup.auto_backup_before_update", True)
    config.set("backup.auto_backup_before_cleanup", True)
    config.set("backup.retention_days", 7)
    config.set("backup.max_backups", 10)

    config.save()

    # Copy example deploy.yaml for reference
    templates_dir = Path(__file__).parent.parent / "templates" / "docker"
    example_file = templates_dir / "deploy.yaml.example"
    if example_file.exists():
        shutil.copy(example_file, "deploy.yaml.example")
        console.print("[dim]ℹ️  deploy.yaml.example copied for reference[/dim]")

    console.print("\n[green]✅ Configuration saved to deploy.yaml[/green]")
    console.print("[green]✅ Encryption key generated for secrets management[/green]")
    console.print("\n[bold]Next steps:[/bold]")
    console.print("1. Review deploy.yaml and adjust settings if needed")
    console.print(
        "2. Set secrets on VPS: [cyan]telegram-bot-stack deploy secrets set BOT_TOKEN 'your-token'[/cyan]"
    )
    console.print("3. Run: [cyan]telegram-bot-stack deploy up[/cyan]")
    console.print("\n[dim]See deploy.yaml.example for all available options[/dim]")
    console.print(
        "[yellow]⚠️  Keep deploy.yaml secure - it contains your encryption key![/yellow]"
    )


@deploy.command()
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

        # Check and install Docker if needed
        console.print("[cyan]🐳 Checking Docker installation...[/cyan]")
        if not vps.check_docker_installed():
            console.print("[yellow]Docker not found, installing...[/yellow]")
            if not vps.install_docker():
                console.print("[red]❌ Failed to install Docker[/red]")
                return
        else:
            console.print("[green]✓ Docker is installed[/green]\n")

        # Prepare deployment directory
        bot_name = deploy_config.get("bot.name")
        remote_dir = f"/opt/{bot_name}"

        console.print(f"[cyan]📦 Preparing deployment directory: {remote_dir}[/cyan]")
        vps.run_command(f"mkdir -p {remote_dir}")

        # Generate Docker files from templates
        console.print("[cyan]📝 Generating Docker configuration...[/cyan]")
        from telegram_bot_stack.cli.utils.deployment import (
            DockerTemplateRenderer,
            create_env_file,
        )

        temp_dir = Path(".deploy-temp")
        temp_dir.mkdir(exist_ok=True)

        try:
            # Check if secrets exist before rendering templates
            # This determines whether .secrets.env should be included in docker-compose.yml
            encryption_key = deploy_config.get("secrets.encryption_key")
            has_secrets = False

            if encryption_key:
                secrets_manager = SecretsManager(bot_name, remote_dir, encryption_key)
                # Check if secrets exist (without decrypting)
                encrypted_secrets = secrets_manager.list_secrets(
                    vps, return_values=False
                )
                has_secrets = len(encrypted_secrets) > 0

            # Render templates
            renderer = DockerTemplateRenderer(deploy_config, has_secrets=has_secrets)
            renderer.render_all(temp_dir)

            # Create .env file (secrets will be loaded from .secrets.env on VPS)
            env_file = temp_dir / ".env"
            create_env_file(deploy_config, env_file)

            console.print("[green]✓ Docker configuration generated[/green]\n")

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

            # Create decryption script that decrypts secrets in-memory during container startup
            # This ensures secrets remain encrypted at rest on VPS filesystem
            # Note: has_secrets was already determined above
            encryption_key = deploy_config.get("secrets.encryption_key")

            # Create Python script that decrypts secrets in-memory and outputs to stdout
            # This script runs during container startup, never writes plain text to filesystem
            # Escape encryption_key for use in Python string (handle None case)
            encryption_key_str = encryption_key if encryption_key else ""
            # Escape backslashes and quotes for Python string literal
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
                        # Simple escaping: quote if contains special characters
                        needs_quoting = any(
                            char in decrypted_value
                            for char in ["\\n", "\\r", "\\t", '"', "\\\\", " ", "#", "=", "$", "`"]
                        )

                        if needs_quoting:
                            # Build escaped value step by step
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
                        # Use format to avoid f-string nesting issues
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
                console.print(
                    "[yellow]⚠️  Warning: Could not create decryption script[/yellow]"
                )

            # Note: Makefile template now handles decryption via decrypt_secrets.py
            # Secrets are decrypted to /dev/shm (shared memory, RAM-based, not persisted)
            if has_secrets:
                console.print(
                    "[dim]   (Secrets will be decrypted in-memory to shared memory during container startup)[/dim]"
                )

            # Build and start bot
            console.print("[cyan]🏗️  Building Docker image...[/cyan]")
            if not vps.run_command(f"cd {remote_dir} && docker-compose build"):
                console.print("[red]❌ Failed to build Docker image[/red]")
                return

            console.print("[green]✓ Docker image built[/green]\n")

            console.print("[cyan]🚀 Starting bot...[/cyan]")
            # Makefile handles secrets decryption via decrypt_secrets.py
            # Secrets are decrypted to /dev/shm (shared memory) before docker-compose starts
            if not vps.run_command(f"cd {remote_dir} && make up"):
                console.print("[red]❌ Failed to start bot[/red]")
                return

            console.print("[green]✓ Bot started[/green]\n")

            # Show status
            console.print("[cyan]📊 Checking bot status...[/cyan]")
            vps.run_command(f"cd {remote_dir} && docker-compose ps")

            console.print("\n[green]🎉 Deployment successful![/green]\n")
            console.print("[bold]Bot Information:[/bold]")
            console.print(f"  Name: {bot_name}")
            console.print(f"  Host: {deploy_config.get('vps.host')}")
            console.print(f"  Directory: {remote_dir}")
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


@deploy.command()
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
            vps.run_command(f"cd {remote_dir} && docker-compose build")

            console.print("[cyan]🔄 Restarting bot...[/cyan]")
            vps.run_command(f"cd {remote_dir} && docker-compose up -d")

            console.print("\n[green]✅ Bot updated successfully![/green]")

        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    finally:
        vps.close()


@deploy.command()
@click.option("--config", default="deploy.yaml", help="Deployment config file")
def status(config: str) -> None:
    """Check bot status on VPS."""
    console.print("📊 [bold cyan]Bot Status[/bold cyan]\n")

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

    bot_name = deploy_config.get("bot.name")
    remote_dir = f"/opt/{bot_name}"

    # Show container status
    console.print("[cyan]Container Status:[/cyan]")
    vps.run_command(f"cd {remote_dir} && docker-compose ps")

    console.print("\n[cyan]Resource Usage:[/cyan]")
    vps.run_command(f"docker stats --no-stream {bot_name}")

    console.print("\n[cyan]Recent Logs:[/cyan]")
    vps.run_command(f"cd {remote_dir} && docker-compose logs --tail=20")

    vps.close()


@deploy.command()
@click.option("--config", default="deploy.yaml", help="Deployment config file")
@click.option("--follow", "-f", is_flag=True, help="Follow log output")
@click.option("--tail", default=50, help="Number of lines to show (default: 50)")
def logs(config: str, follow: bool, tail: int) -> None:
    """View bot logs from VPS."""
    console.print("📋 [bold cyan]Bot Logs[/bold cyan]\n")

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

    remote_dir = f"/opt/{deploy_config.get('bot.name')}"

    # Stream logs
    follow_flag = "-f" if follow else ""
    vps.run_command(
        f"cd {remote_dir} && docker-compose logs {follow_flag} --tail={tail}"
    )

    vps.close()


@deploy.command()
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
            vps.run_command(f"cd {remote_dir} && docker-compose down -v --rmi all")
            console.print("[green]✓ Bot stopped and cleaned up[/green]")
        else:
            console.print("[cyan]Stopping bot...[/cyan]")
            vps.run_command(f"cd {remote_dir} && docker-compose down")
            console.print("[green]✓ Bot stopped[/green]")

    finally:
        vps.close()


@deploy.group()
def secrets() -> None:
    """Manage deployment secrets (secure token storage)."""
    pass


@secrets.command()
@click.option("--config", default="deploy.yaml", help="Deployment config file")
@click.argument("key")
@click.argument("value")
def set_secret(config: str, key: str, value: str) -> None:
    """Set a secret value on VPS.

    Example:
        telegram-bot-stack deploy secrets set BOT_TOKEN "your-token-here"
    """
    console.print(f"🔐 [bold cyan]Setting secret: {key}[/bold cyan]\n")

    # Load configuration
    if not Path(config).exists():
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        console.print("\n[yellow]Run 'telegram-bot-stack deploy init' first[/yellow]")
        return

    deploy_config = DeploymentConfig(config)

    if not deploy_config.validate():
        console.print("[red]❌ Invalid configuration[/red]")
        return

    # Get encryption key from config
    encryption_key = deploy_config.get("secrets.encryption_key")
    if not encryption_key:
        console.print("[red]❌ Encryption key not found in deploy.yaml[/red]")
        console.print(
            "\n[yellow]Run 'telegram-bot-stack deploy init' to generate encryption key[/yellow]"
        )
        return

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

        # Set secret
        secrets_manager = SecretsManager(bot_name, remote_dir, encryption_key)
        if secrets_manager.set_secret(key, value, vps):
            console.print(f"[green]✅ Secret '{key}' set successfully[/green]")
        else:
            console.print(f"[red]❌ Failed to set secret '{key}'[/red]")

    finally:
        # Always close VPS connection
        vps.close()


@secrets.command()
@click.option("--config", default="deploy.yaml", help="Deployment config file")
@click.argument("key")
def get_secret(config: str, key: str) -> None:
    """Get a secret value from VPS (for debugging).

    Example:
        telegram-bot-stack deploy secrets get BOT_TOKEN
    """
    # Load configuration
    if not Path(config).exists():
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        return

    deploy_config = DeploymentConfig(config)

    # Get encryption key
    encryption_key = deploy_config.get("secrets.encryption_key")
    if not encryption_key:
        console.print("[red]❌ Encryption key not found[/red]")
        return

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

        # Get secret
        secrets_manager = SecretsManager(bot_name, remote_dir, encryption_key)
        value = secrets_manager.get_secret(key, vps)

        if value:
            console.print(f"[green]{key}={value}[/green]")
        else:
            console.print(f"[yellow]Secret '{key}' not found[/yellow]")

    finally:
        # Always close VPS connection
        vps.close()


@secrets.command()
@click.option("--config", default="deploy.yaml", help="Deployment config file")
def list_secrets(config: str) -> None:
    """List all secrets (names only, not values).

    Example:
        telegram-bot-stack deploy secrets list
    """
    console.print("🔐 [bold cyan]Stored Secrets[/bold cyan]\n")

    # Load configuration
    if not Path(config).exists():
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        return

    deploy_config = DeploymentConfig(config)

    # Get encryption key
    encryption_key = deploy_config.get("secrets.encryption_key")
    if not encryption_key:
        console.print("[red]❌ Encryption key not found[/red]")
        return

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

        # List secrets
        secrets_manager = SecretsManager(bot_name, remote_dir, encryption_key)
        secrets = secrets_manager.list_secrets(vps)

        if secrets:
            console.print("[bold]Secret names:[/bold]")
            for key in sorted(secrets.keys()):
                console.print(f"  • {key}")
        else:
            console.print("[yellow]No secrets stored[/yellow]")

    finally:
        # Always close VPS connection
        vps.close()


@secrets.command()
@click.option("--config", default="deploy.yaml", help="Deployment config file")
@click.argument("key")
def remove_secret(config: str, key: str) -> None:
    """Remove a secret from VPS.

    Example:
        telegram-bot-stack deploy secrets remove BOT_TOKEN
    """
    console.print(f"🗑️  [bold cyan]Removing secret: {key}[/bold cyan]\n")

    # Load configuration
    if not Path(config).exists():
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        return

    deploy_config = DeploymentConfig(config)

    # Get encryption key
    encryption_key = deploy_config.get("secrets.encryption_key")
    if not encryption_key:
        console.print("[red]❌ Encryption key not found[/red]")
        return

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

        # Remove secret
        secrets_manager = SecretsManager(bot_name, remote_dir, encryption_key)
        if secrets_manager.remove_secret(key, vps):
            console.print(f"[green]✅ Secret '{key}' removed successfully[/green]")
        else:
            console.print(f"[red]❌ Failed to remove secret '{key}'[/red]")

    finally:
        # Always close VPS connection
        vps.close()


@deploy.group(invoke_without_command=True)
@click.pass_context
@click.option("--config", default="deploy.yaml", help="Deployment config file")
def backup(ctx: click.Context, config: str) -> None:
    """Manage bot backups (data safety)."""
    # If no subcommand provided, create backup
    if ctx.invoked_subcommand is None:
        ctx.forward(create_backup)


@backup.command("create")
@click.option("--config", default="deploy.yaml", help="Deployment config file")
def create_backup(config: str) -> None:
    """Create a backup of bot data.

    Example:
        telegram-bot-stack deploy backup
    """
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

        # Create backup
        backup_manager = BackupManager(bot_name, remote_dir)
        backup_filename = backup_manager.create_backup(vps, auto_backup=False)

        if backup_filename:
            # Cleanup old backups
            retention_days = deploy_config.get("backup.retention_days", 7)
            max_backups = deploy_config.get("backup.max_backups", 10)
            deleted = backup_manager.cleanup_old_backups(
                vps, retention_days=retention_days, max_backups=max_backups
            )
            if deleted > 0:
                console.print(f"[dim]   Cleaned up {deleted} old backup(s)[/dim]")

    finally:
        vps.close()


@backup.command("list")
@click.option("--config", default="deploy.yaml", help="Deployment config file")
def list_backups(config: str) -> None:
    """List all available backups.

    Example:
        telegram-bot-stack deploy backup list
    """
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

        # List backups
        backup_manager = BackupManager(bot_name, remote_dir)
        backups = backup_manager.list_backups(vps)

        if backups:
            console.print("📦 [bold cyan]Available Backups[/bold cyan]\n")
            from rich.table import Table

            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Filename")
            table.add_column("Size")
            table.add_column("Date")

            for backup in backups:
                date_str = (
                    backup["date"].strftime("%Y-%m-%d %H:%M:%S")
                    if backup["date"]
                    else "Unknown"
                )
                table.add_row(backup["filename"], backup["size"], date_str)

            console.print(table)
        else:
            console.print("[yellow]No backups found[/yellow]")

    finally:
        vps.close()


@backup.command()
@click.option("--config", default="deploy.yaml", help="Deployment config file")
@click.argument("backup_filename")
@click.option("--output", "-o", default=".", help="Local directory to save backup")
def download(config: str, backup_filename: str, output: str) -> None:
    """Download backup from VPS to local machine.

    Example:
        telegram-bot-stack deploy backup download backup-20250126-143022.tar.gz
    """
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

        # Download backup
        backup_manager = BackupManager(bot_name, remote_dir)
        backup_manager.download_backup(vps, backup_filename, Path(output))

    finally:
        vps.close()


@deploy.command()
@click.option("--config", default="deploy.yaml", help="Deployment config file")
@click.argument("backup_filename")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
def restore(config: str, backup_filename: str, yes: bool) -> None:
    """Restore bot data from backup.

    Example:
        telegram-bot-stack deploy restore backup-20250126-143022.tar.gz
    """
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

        # Restore backup
        backup_manager = BackupManager(bot_name, remote_dir)
        backup_manager.restore_backup(vps, backup_filename, confirm=not yes)

    finally:
        vps.close()
