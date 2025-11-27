"""Monitoring commands for deployment (status, logs)."""

from pathlib import Path

import click
from rich.console import Console

from telegram_bot_stack.cli.utils.deployment import DeploymentConfig
from telegram_bot_stack.cli.utils.vps import VPSConnection

console = Console()


@click.command()
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


@click.command()
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
