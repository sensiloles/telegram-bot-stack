"""Core deployment commands (init, backup, restore)."""

import shutil
from pathlib import Path

import click
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

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
    console.print("\n[green]✓ Configuration saved to deploy.yaml[/green]")

    # Copy example deploy.yaml for reference
    templates_dir = Path(__file__).parent.parent.parent / "templates" / "docker"
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
