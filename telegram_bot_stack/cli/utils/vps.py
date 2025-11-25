"""
VPS operations utilities for deployment.

Handles SSH connections, file transfers, and remote command execution.
"""

import os
from pathlib import Path
from typing import Optional

from fabric import Connection
from rich.console import Console

console = Console()


class VPSConnection:
    """Manages SSH connection to VPS."""

    def __init__(
        self,
        host: str,
        user: str = "root",
        ssh_key: Optional[str] = None,
        port: int = 22,
    ):
        """Initialize VPS connection parameters.

        Args:
            host: VPS hostname or IP address
            user: SSH user (default: root)
            ssh_key: Path to SSH private key (optional)
            port: SSH port (default: 22)
        """
        self.host = host
        self.user = user
        self.ssh_key = os.path.expanduser(ssh_key) if ssh_key else None
        self.port = port
        self.connection: Optional[Connection] = None

    def test_connection(self) -> bool:
        """Test SSH connection to VPS.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            with console.status("[cyan]Testing SSH connection..."):
                conn = self._create_connection()
                result = conn.run("echo 'Connection test'", hide=True)
                return result.ok
        except Exception as e:
            console.print(f"[red]Connection failed: {e}[/red]")
            return False

    def connect(self) -> Connection:
        """Establish SSH connection to VPS.

        Returns:
            Fabric Connection object

        Raises:
            Exception: If connection fails
        """
        if self.connection is None:
            self.connection = self._create_connection()
        return self.connection

    def _create_connection(self) -> Connection:
        """Create Fabric connection with SSH key or password.

        Returns:
            Fabric Connection object
        """
        connect_kwargs = {}

        if self.ssh_key:
            connect_kwargs["key_filename"] = self.ssh_key
        else:
            # Will prompt for password if no key provided
            connect_kwargs["look_for_keys"] = True

        return Connection(
            host=self.host,
            user=self.user,
            port=self.port,
            connect_kwargs=connect_kwargs,
        )

    def run_command(self, command: str, hide: bool = False) -> bool:
        """Run command on VPS.

        Args:
            command: Command to execute
            hide: Hide command output (default: False)

        Returns:
            True if command succeeded, False otherwise
        """
        try:
            conn = self.connect()
            result = conn.run(command, hide=hide)
            return result.ok
        except Exception as e:
            console.print(f"[red]Command failed: {e}[/red]")
            return False

    def check_docker_installed(self) -> bool:
        """Check if Docker is installed on VPS.

        Returns:
            True if Docker is installed, False otherwise
        """
        return self.run_command("docker --version", hide=True)

    def install_docker(self) -> bool:
        """Install Docker on VPS.

        Returns:
            True if installation succeeded, False otherwise
        """
        console.print("[cyan]Installing Docker...[/cyan]")

        commands = [
            # Update package list
            "apt-get update",
            # Install prerequisites
            "apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release",
            # Add Docker GPG key
            "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg",
            # Add Docker repository
            'echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null',
            # Install Docker
            "apt-get update",
            "apt-get install -y docker-ce docker-ce-cli containerd.io",
            # Install Docker Compose
            "curl -L 'https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)' -o /usr/local/bin/docker-compose",
            "chmod +x /usr/local/bin/docker-compose",
        ]

        for cmd in commands:
            if not self.run_command(cmd):
                console.print("[red]Docker installation failed[/red]")
                return False

        console.print("[green]✓ Docker installed successfully[/green]")
        return True

    def transfer_files(self, local_path: Path, remote_path: str) -> bool:
        """Transfer files to VPS using rsync.

        Args:
            local_path: Local directory or file path
            remote_path: Remote destination path

        Returns:
            True if transfer succeeded, False otherwise
        """
        try:
            conn = self.connect()

            # Create remote directory if it doesn't exist
            conn.run(f"mkdir -p {remote_path}", hide=True)

            # Use rsync for efficient file transfer
            console.print(f"[cyan]Transferring files to {remote_path}...[/cyan]")

            # Build rsync command
            ssh_key_arg = f"-e 'ssh -i {self.ssh_key}'" if self.ssh_key else ""
            rsync_cmd = f"rsync -avz --delete {ssh_key_arg} {local_path}/ {self.user}@{self.host}:{remote_path}/"

            os.system(rsync_cmd)

            console.print("[green]✓ Files transferred successfully[/green]")
            return True
        except Exception as e:
            console.print(f"[red]File transfer failed: {e}[/red]")
            return False

    def close(self) -> None:
        """Close SSH connection."""
        if self.connection:
            self.connection.close()
            self.connection = None


def check_docker_compose_installed(conn: Connection) -> bool:
    """Check if Docker Compose is installed.

    Args:
        conn: Fabric Connection object

    Returns:
        True if Docker Compose is installed, False otherwise
    """
    try:
        result = conn.run("docker-compose --version", hide=True)
        return result.ok
    except Exception:
        return False
