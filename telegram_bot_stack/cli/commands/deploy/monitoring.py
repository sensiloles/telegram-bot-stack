"""Monitoring commands for deployment (status, logs, health)."""

from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from telegram_bot_stack.cli.utils.deployment import DeploymentConfig
from telegram_bot_stack.cli.utils.vps import (
    VPSConnection,
    get_container_health,
    get_recent_errors,
)

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

    # Show container status (make status includes both ps and stats)
    console.print("[cyan]Container Status:[/cyan]")
    vps.run_command(f"cd {remote_dir} && make status")

    console.print("\n[cyan]Recent Logs:[/cyan]")
    vps.run_command(f"cd {remote_dir} && TAIL=20 FOLLOW= make logs")

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
    follow_flag = "f" if follow else ""
    vps.run_command(f"cd {remote_dir} && TAIL={tail} FOLLOW={follow_flag} make logs")

    vps.close()


@click.command()
@click.option("--config", default="deploy.yaml", help="Deployment config file")
@click.option("--errors", "-e", is_flag=True, help="Show recent errors only")
def health(config: str, errors: bool) -> None:
    """Check bot health and automatic recovery status.

    Shows:
    - Container status (running/stopped/restarting)
    - Health check status
    - Uptime
    - Restart count and last restart time
    - Recent errors (if --errors flag is used)

    Example:
        telegram-bot-stack deploy health
        telegram-bot-stack deploy health --errors
    """
    console.print("🏥 [bold cyan]Bot Health Check[/bold cyan]\n")

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
        conn = vps.connect()

        # Get health information
        health_info = get_container_health(conn, bot_name)

        # Display health status
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="cyan")
        table.add_column("Status", style="white")

        # Container status
        if health_info["running"]:
            status_text = "[green]✓ Running[/green]"
        else:
            exit_code = health_info.get("exit_code")
            if exit_code is not None:
                status_text = f"[red]✗ Stopped (exit code: {exit_code})[/red]"
            else:
                status_text = "[red]✗ Not running[/red]"
        table.add_row("Container", status_text)

        # Health check status
        health_status = health_info.get("health_status", "unknown")
        if health_status == "healthy":
            health_text = "[green]✓ Healthy[/green]"
        elif health_status == "unhealthy":
            health_text = "[red]✗ Unhealthy[/red]"
        elif health_status == "starting":
            health_text = "[yellow]⏳ Starting[/yellow]"
        else:
            health_text = "[dim]No healthcheck configured[/dim]"
        table.add_row("Health Status", health_text)

        # Uptime
        uptime = health_info.get("uptime")
        if uptime:
            try:
                # Parse Docker timestamp
                start_time = datetime.fromisoformat(uptime.replace("Z", "+00:00"))
                now = datetime.now(start_time.tzinfo)
                uptime_delta = now - start_time
                days = uptime_delta.days
                hours, remainder = divmod(uptime_delta.seconds, 3600)
                minutes, _ = divmod(remainder, 60)

                if days > 0:
                    uptime_text = f"{days}d {hours}h {minutes}m"
                elif hours > 0:
                    uptime_text = f"{hours}h {minutes}m"
                else:
                    uptime_text = f"{minutes}m"
                table.add_row("Uptime", uptime_text)
            except (ValueError, AttributeError):
                table.add_row("Uptime", uptime)
        else:
            table.add_row("Uptime", "[dim]N/A[/dim]")

        # Restart count
        restarts = health_info.get("restarts", 0)
        if restarts > 0:
            restart_text = f"[yellow]{restarts} restart(s)[/yellow]"
        else:
            restart_text = "[green]0 restarts[/green]"
        table.add_row("Restarts", restart_text)

        console.print(table)

        # Show automatic recovery configuration
        console.print("\n[bold]Automatic Recovery:[/bold]")
        auto_restart = deploy_config.get("deployment.auto_restart", True)
        if auto_restart:
            console.print(
                "  [green]✓ Enabled[/green] - Container will restart on failure"
            )
            console.print("  [dim]Max retries: 3 within 5 minutes[/dim]")
        else:
            console.print("  [yellow]⚠️  Disabled[/yellow] - Manual restart required")

        # Show recent errors if requested
        if errors:
            console.print("\n[bold]Recent Errors:[/bold]")
            recent_errors = get_recent_errors(conn, bot_name, lines=100)
            if recent_errors:
                console.print(f"[red]{recent_errors}[/red]")
            else:
                console.print("[green]No recent errors found[/green]")

        # Show recommendations
        if not health_info["running"]:
            console.print("\n[yellow]⚠️  Bot is not running![/yellow]")
            console.print("\n[bold]Recommended actions:[/bold]")
            console.print(
                "  1. Check logs: [cyan]telegram-bot-stack deploy logs[/cyan]"
            )
            console.print("  2. Restart bot: [cyan]telegram-bot-stack deploy up[/cyan]")
        elif health_status == "unhealthy":
            console.print("\n[yellow]⚠️  Bot is unhealthy![/yellow]")
            console.print("\n[bold]Recommended actions:[/bold]")
            console.print(
                "  1. Check errors: [cyan]telegram-bot-stack deploy health --errors[/cyan]"
            )
            console.print("  2. View logs: [cyan]telegram-bot-stack deploy logs[/cyan]")
            console.print(
                "  3. Restart if needed: [cyan]telegram-bot-stack deploy up[/cyan]"
            )
        elif restarts > 3:
            console.print("\n[yellow]⚠️  Multiple restarts detected![/yellow]")
            console.print("\n[bold]Recommended actions:[/bold]")
            console.print(
                "  1. Check errors: [cyan]telegram-bot-stack deploy health --errors[/cyan]"
            )
            console.print("  2. Review configuration: [cyan]cat deploy.yaml[/cyan]")
            console.print("  3. Check bot code for issues")

    finally:
        vps.close()
