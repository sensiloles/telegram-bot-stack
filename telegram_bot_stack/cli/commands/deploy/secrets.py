"""Secrets management commands for deployment."""

from pathlib import Path

import click
from rich.console import Console

from telegram_bot_stack.cli.utils.deployment import DeploymentConfig
from telegram_bot_stack.cli.utils.secrets import SecretsManager
from telegram_bot_stack.cli.utils.vps import VPSConnection

console = Console()


@click.group()
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
