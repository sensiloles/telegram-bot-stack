"""Deployment state detection for VPS."""

from dataclasses import dataclass
from typing import Any

from rich.console import Console
from rich.prompt import Confirm

console = Console()


@dataclass
class ContainerState:
    """Docker container state information."""

    exists: bool
    running: bool
    status: str
    uptime: str
    health: str
    name: str
    image: str


@dataclass
class ServiceState:
    """Systemd service state information."""

    exists: bool
    active: bool
    status: str
    uptime: str


class DeploymentStateDetector:
    """Detect and handle deployment state on VPS."""

    def __init__(self, vps: Any, bot_name: str, remote_dir: str):
        """Initialize deployment state detector.

        Args:
            vps: VPSConnection instance
            bot_name: Bot name
            remote_dir: Remote directory path
        """
        self.vps = vps
        self.bot_name = bot_name
        self.remote_dir = remote_dir

    def get_docker_state(self) -> ContainerState:
        """Get Docker container state.

        Returns:
            ContainerState with current state information
        """
        # Check if container exists
        result = self.vps.run_command(
            f"docker ps -a --filter name=^{self.bot_name}$ --format '{{{{.Status}}}}|{{{{.Image}}}}'",
            hide=True,
        )

        if not result:
            return ContainerState(
                exists=False,
                running=False,
                status="not deployed",
                uptime="",
                health="",
                name=self.bot_name,
                image="",
            )

        # Parse container info
        stdout = result.stdout.strip() if hasattr(result, "stdout") else ""
        if not stdout:
            return ContainerState(
                exists=False,
                running=False,
                status="not deployed",
                uptime="",
                health="",
                name=self.bot_name,
                image="",
            )

        parts = stdout.split("|")
        status = parts[0] if len(parts) > 0 else ""
        image = parts[1] if len(parts) > 1 else ""

        # Determine if running
        running = status.startswith("Up")

        # Parse uptime and health
        uptime = ""
        health = "unknown"

        if running:
            # Extract uptime (e.g., "Up 2 hours")
            if "Up" in status:
                uptime_start = status.find("Up") + 3
                # Find end of uptime (before parentheses or end)
                uptime_end = status.find("(", uptime_start)
                if uptime_end == -1:
                    uptime_end = len(status)
                uptime = status[uptime_start:uptime_end].strip()

            # Extract health status
            if "(healthy)" in status:
                health = "healthy"
            elif "(unhealthy)" in status:
                health = "unhealthy"
            elif "(starting)" in status:
                health = "starting"
            else:
                health = "no healthcheck"
        else:
            health = "not running"

        return ContainerState(
            exists=True,
            running=running,
            status=status,
            uptime=uptime,
            health=health,
            name=self.bot_name,
            image=image,
        )

    def get_systemd_state(self) -> ServiceState:
        """Get systemd service state.

        Returns:
            ServiceState with current state information
        """
        # Check if service exists
        result = self.vps.run_command(
            f"systemctl list-units --all --type=service --no-pager | grep {self.bot_name}.service",
            hide=True,
        )

        if not result or not result.stdout.strip():
            return ServiceState(
                exists=False, active=False, status="not deployed", uptime=""
            )

        # Get service status
        status_result = self.vps.run_command(
            f"systemctl is-active {self.bot_name}", hide=True
        )

        active = (
            status_result and status_result.stdout.strip() == "active"
            if hasattr(status_result, "stdout")
            else False
        )

        # Get service status details
        status_details = self.vps.run_command(
            f"systemctl status {self.bot_name} --no-pager", hide=True
        )

        status = status_details.stdout.strip() if status_details else "unknown"

        return ServiceState(exists=True, active=active, status=status, uptime="")

    def detect_stale_containers(self) -> list[str]:
        """Detect stale/zombie containers (exited/stopped but not removed).

        Returns:
            List of stale container names
        """
        result = self.vps.run_command(
            "docker ps -a --filter status=exited --filter status=created --format '{{.Names}}'",
            hide=True,
        )

        if not result:
            return []

        stdout = result.stdout.strip() if hasattr(result, "stdout") else ""
        if not stdout:
            return []

        # Filter containers related to this bot
        containers = stdout.split("\n")
        return [c for c in containers if self.bot_name in c]

    def cleanup_stale_containers(self) -> int:
        """Clean up stale containers.

        Returns:
            Number of containers cleaned up
        """
        stale = self.detect_stale_containers()

        if not stale:
            return 0

        console.print(f"\n⚠️  Found {len(stale)} stale container(s): {', '.join(stale)}")
        console.print("[cyan]Auto-cleaning stale containers...[/cyan]")

        cleaned = 0
        for container in stale:
            if self.vps.run_command(f"docker rm {container}", hide=True):
                cleaned += 1

        if cleaned > 0:
            console.print(f"[green]✓ Cleaned up {cleaned} container(s)[/green]\n")

        return cleaned

    def check_before_deploy(
        self, deployment_method: str = "docker", force: bool = False
    ) -> bool:
        """Check deployment state before deploying.

        Args:
            deployment_method: Deployment method (docker or systemd)
            force: If True, allow deployment even if bot is already running

        Returns:
            True if deployment should proceed, False otherwise
        """
        if deployment_method == "docker":
            state = self.get_docker_state()

            # Clean up stale containers first
            self.cleanup_stale_containers()

            if state.exists and state.running:
                # Bot is already running
                console.print(
                    "\n[yellow]⚠️  Warning: Bot is already deployed and running[/yellow]\n"
                )

                console.print("[bold]Current Status:[/bold]")
                console.print(f"  Container: {state.name}")
                console.print(f"  Status: {state.status}")
                console.print(f"  Uptime: {state.uptime}")
                console.print(f"  Health: {self._format_health(state.health)}")
                console.print(f"  Image: {state.image}\n")

                console.print("[bold]Options:[/bold]")
                console.print(
                    "  1. Update existing: [cyan]telegram-bot-stack deploy update[/cyan]"
                )
                console.print(
                    "  2. View status: [cyan]telegram-bot-stack deploy status[/cyan]"
                )
                console.print(
                    "  3. Force redeploy: [cyan]telegram-bot-stack deploy up --force[/cyan]"
                )
                console.print()

                if force:
                    console.print(
                        "[yellow]⚠️  Force mode enabled - stopping existing deployment...[/yellow]\n"
                    )
                    # Stop and remove existing container
                    self.vps.run_command(f"cd {self.remote_dir} && make down")
                    self.vps.run_command(f"docker rm -f {self.bot_name}", hide=True)
                    return True

                # Ask for confirmation
                if not Confirm.ask(
                    "[yellow]Continue with deployment anyway?[/yellow]", default=False
                ):
                    console.print("[yellow]Deployment cancelled[/yellow]")
                    return False

                # User confirmed - stop existing deployment
                console.print("[cyan]Stopping existing deployment...[/cyan]")
                self.vps.run_command(f"cd {self.remote_dir} && make down")
                self.vps.run_command(f"docker rm -f {self.bot_name}", hide=True)
                return True

            elif state.exists and not state.running:
                # Container exists but not running - clean it up
                console.print(
                    f"\n[yellow]⚠️  Found stopped container '{state.name}'[/yellow]"
                )
                console.print("[cyan]Removing stopped container...[/cyan]")
                self.vps.run_command(f"docker rm {state.name}", hide=True)
                console.print("[green]✓ Cleaned up[/green]\n")
                return True

        elif deployment_method == "systemd":
            service_state = self.get_systemd_state()

            if service_state.exists and service_state.active:
                console.print(
                    "\n[yellow]⚠️  Warning: Bot service is already running[/yellow]\n"
                )

                console.print("[bold]Current Status:[/bold]")
                console.print(f"  Service: {self.bot_name}")
                console.print("  Active: Yes")
                console.print()

                console.print("[bold]Options:[/bold]")
                console.print(
                    "  1. Update existing: [cyan]telegram-bot-stack deploy update[/cyan]"
                )
                console.print(
                    "  2. View status: [cyan]telegram-bot-stack deploy status[/cyan]"
                )
                console.print(
                    "  3. Force redeploy: [cyan]telegram-bot-stack deploy up --force[/cyan]"
                )
                console.print()

                if force:
                    console.print(
                        "[yellow]⚠️  Force mode enabled - stopping existing service...[/yellow]\n"
                    )
                    self.vps.run_command(f"systemctl stop {self.bot_name}")
                    return True

                if not Confirm.ask(
                    "[yellow]Continue with deployment anyway?[/yellow]", default=False
                ):
                    console.print("[yellow]Deployment cancelled[/yellow]")
                    return False

                # User confirmed - stop service
                console.print("[cyan]Stopping existing service...[/cyan]")
                self.vps.run_command(f"systemctl stop {self.bot_name}")
                return True

        return True

    def _format_health(self, health: str) -> str:
        """Format health status with color.

        Args:
            health: Health status string

        Returns:
            Formatted health string
        """
        if health == "healthy":
            return "✅ Healthy"
        elif health == "unhealthy":
            return "❌ Unhealthy"
        elif health == "starting":
            return "🔄 Starting"
        elif health == "no healthcheck":
            return "⚠️  No healthcheck"
        elif health == "not running":
            return "🛑 Not running"
        else:
            return f"❓ {health}"
