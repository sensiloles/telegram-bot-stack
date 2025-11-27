"""
VPS operations utilities for deployment.

Handles SSH connections, file transfers, and remote command execution.
"""

import os
import shlex
from pathlib import Path
from typing import Any, Dict, Optional

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
                return bool(result.ok)
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
        connect_kwargs: Dict[str, Any] = {}

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
            return bool(result.ok)
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
            # Properly escape remote_path to prevent command injection
            conn.run(f"mkdir -p {shlex.quote(remote_path)}", hide=True)

            # Use rsync for efficient file transfer
            console.print(f"[cyan]Transferring files to {remote_path}...[/cyan]")

            # Build rsync command
            # Properly escape all paths and SSH key to prevent command injection
            if self.ssh_key:
                ssh_key_quoted = shlex.quote(self.ssh_key)
                # rsync -e option expects a shell command string
                ssh_cmd = f"ssh -i {ssh_key_quoted}"
                ssh_key_arg = f"-e {shlex.quote(ssh_cmd)}"
            else:
                ssh_key_arg = ""
            local_path_quoted = shlex.quote(str(local_path))
            remote_path_quoted = shlex.quote(remote_path)
            rsync_cmd = f"rsync -avz --delete {ssh_key_arg} {local_path_quoted}/ {self.user}@{self.host}:{remote_path_quoted}/"

            os.system(rsync_cmd)

            console.print("[green]✓ Files transferred successfully[/green]")
            return True
        except Exception as e:
            console.print(f"[red]File transfer failed: {e}[/red]")
            return False

    def write_file(self, content: str, remote_path: str, mode: str = "644") -> bool:
        """Write file content to VPS.

        Args:
            content: File content to write
            remote_path: Remote file path
            mode: File permissions (default: 644)

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.connect()

            # Create remote directory if needed
            remote_dir = "/".join(remote_path.split("/")[:-1])
            if remote_dir:
                # Properly escape remote_dir to prevent command injection
                conn.run(f"mkdir -p {shlex.quote(remote_dir)}", hide=True)

            # Write to temporary file first, then move (atomic operation)
            temp_file = f"{remote_path}.tmp"

            # Use base64 encoding to avoid shell escaping issues
            import base64

            content_b64 = base64.b64encode(content.encode("utf-8")).decode("ascii")
            # Pass paths as command-line arguments to avoid shell/Python string escaping issues
            # This prevents command injection by avoiding string interpolation in Python code
            temp_file_quoted = shlex.quote(temp_file)
            content_b64_quoted = shlex.quote(content_b64)
            python_cmd = (
                f'python3 -c "'
                f"import sys, base64; "
                f"temp_file=sys.argv[1]; "
                f"content_b64=sys.argv[2]; "
                f"f=open(temp_file, 'w'); "
                f"f.write(base64.b64decode(content_b64).decode()); "
                f"f.close()"
                f'" -- {temp_file_quoted} {content_b64_quoted}'
            )
            conn.run(python_cmd, hide=True)

            # Move to final location and set permissions
            # Properly escape file paths to prevent command injection
            conn.run(
                f"mv {shlex.quote(temp_file)} {shlex.quote(remote_path)}", hide=True
            )
            conn.run(f"chmod {mode} {shlex.quote(remote_path)}", hide=True)

            return True
        except Exception as e:
            console.print(f"[red]Failed to write file: {e}[/red]")
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
        return bool(result.ok)
    except Exception:
        return False
