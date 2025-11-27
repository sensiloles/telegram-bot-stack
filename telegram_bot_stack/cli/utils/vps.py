"""
VPS operations utilities for deployment.

Handles SSH connections, file transfers, and remote command execution.
"""

import os
import re
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

        # Detect OS
        conn = self.connect()
        os_info = conn.run(
            "cat /etc/os-release | grep '^ID=' | cut -d'=' -f2", hide=True
        )
        os_id = os_info.stdout.strip().strip('"') if os_info.ok else "ubuntu"

        commands = []
        if os_id in ["ubuntu", "debian"]:
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
        elif os_id in ["centos", "rhel", "fedora"]:
            commands = [
                "yum install -y yum-utils",
                "yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo",
                "yum install -y docker-ce docker-ce-cli containerd.io",
                "systemctl start docker",
                "systemctl enable docker",
                "curl -L 'https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)' -o /usr/local/bin/docker-compose",
                "chmod +x /usr/local/bin/docker-compose",
            ]
        else:
            console.print(f"[red]Unsupported OS: {os_id}[/red]")
            return False

        for cmd in commands:
            if not self.run_command(cmd):
                console.print(f"[red]Docker installation failed at: {cmd}[/red]")
                return False

        console.print("[green]✓ Docker installed successfully[/green]")
        return True

    def check_python_version(
        self, min_version: str = "3.9"
    ) -> tuple[bool, Optional[str]]:
        """Check Python version on VPS.

        Args:
            min_version: Minimum required Python version (e.g., "3.9")

        Returns:
            Tuple of (is_sufficient, current_version)
        """
        try:
            conn = self.connect()
            # Try python3 first, then python
            result = conn.run(
                "python3 --version 2>&1 || python --version 2>&1", hide=True
            )
            if not result.ok:
                return (False, None)

            version_str = result.stdout.strip()
            # Extract version number (e.g., "Python 3.10.5" -> "3.10.5")
            match = re.search(r"(\d+\.\d+\.\d+)", version_str)
            if not match:
                return (False, version_str)

            current_version = match.group(1)
            min_parts = [int(x) for x in min_version.split(".")]
            current_parts = [int(x) for x in current_version.split(".")]

            # Compare versions
            is_sufficient = current_parts >= min_parts
            return (is_sufficient, current_version)
        except Exception as e:
            console.print(
                f"[yellow]Warning: Could not check Python version: {e}[/yellow]"
            )
            return (False, None)

    def install_python(self, version: str = "3.11") -> bool:
        """Install Python on VPS.

        Args:
            version: Python version to install (e.g., "3.11")

        Returns:
            True if installation succeeded, False otherwise
        """
        console.print(f"[cyan]Installing Python {version}...[/cyan]")

        # Detect OS
        conn = self.connect()
        os_info = conn.run(
            "cat /etc/os-release | grep '^ID=' | cut -d'=' -f2", hide=True
        )
        os_id = os_info.stdout.strip().strip('"') if os_info.ok else "ubuntu"

        major, minor = version.split(".")[:2]
        commands = []

        if os_id in ["ubuntu", "debian"]:
            # For Ubuntu/Debian, use deadsnakes PPA for newer Python versions
            commands = [
                "apt-get update",
                "apt-get install -y software-properties-common",
                "add-apt-repository -y ppa:deadsnakes/ppa",
                "apt-get update",
                f"apt-get install -y python{version} python{version}-venv python{version}-dev python3-pip",
                f"update-alternatives --install /usr/bin/python3 python3 /usr/bin/python{version} 1",
            ]
        elif os_id in ["centos", "rhel"]:
            # For CentOS/RHEL, use EPEL and SCL
            commands = [
                "yum install -y epel-release",
                "yum install -y python3 python3-pip python3-devel",
            ]
        else:
            console.print(f"[red]Unsupported OS for Python installation: {os_id}[/red]")
            return False

        for cmd in commands:
            if not self.run_command(cmd):
                console.print(f"[red]Python installation failed at: {cmd}[/red]")
                return False

        console.print(f"[green]✓ Python {version} installed successfully[/green]")
        return True

    def check_systemd_available(self) -> bool:
        """Check if systemd is available on VPS.

        Returns:
            True if systemd is available, False otherwise
        """
        return self.run_command("systemctl --version", hide=True)

    def validate_vps_requirements(
        self, deployment_method: str, min_python_version: str = "3.9"
    ) -> bool:
        """Validate VPS requirements for deployment method.

        Args:
            deployment_method: Deployment method ('docker' or 'systemd')
            min_python_version: Minimum required Python version

        Returns:
            True if all requirements met, False otherwise
        """
        console.print("[cyan]🔍 Validating VPS requirements...[/cyan]\n")

        all_ok = True

        # Check Python version
        is_sufficient, current_version = self.check_python_version(min_python_version)
        if not is_sufficient:
            if current_version:
                console.print(
                    f"[yellow]⚠️  Python version {current_version} is below required {min_python_version}[/yellow]"
                )
            else:
                console.print("[yellow]⚠️  Python not found[/yellow]")
            console.print(f"[cyan]   Installing Python {min_python_version}...[/cyan]")
            if not self.install_python(min_python_version):
                console.print("[red]❌ Failed to install Python[/red]")
                all_ok = False
            else:
                console.print("[green]✓ Python installed[/green]\n")
        else:
            console.print(f"[green]✓ Python {current_version} is sufficient[/green]\n")

        # Check deployment method requirements
        if deployment_method == "docker":
            if not self.check_docker_installed():
                console.print("[yellow]⚠️  Docker not found[/yellow]")
                console.print("[cyan]   Installing Docker...[/cyan]")
                if not self.install_docker():
                    console.print("[red]❌ Failed to install Docker[/red]")
                    all_ok = False
                else:
                    console.print("[green]✓ Docker installed[/green]\n")
            else:
                console.print("[green]✓ Docker is installed[/green]\n")
        elif deployment_method == "systemd":
            if not self.check_systemd_available():
                console.print("[red]❌ systemd is not available on this system[/red]")
                all_ok = False
            else:
                console.print("[green]✓ systemd is available[/green]\n")

        return all_ok

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

            # Encode content to base64 (b64encode always returns properly padded base64)
            content_bytes = content.encode("utf-8")
            content_b64 = base64.b64encode(content_bytes).decode("ascii")

            # Pass paths as command-line arguments to avoid shell/Python string escaping issues
            # This prevents command injection by avoiding string interpolation in Python code
            # Note: base64.b64encode always returns properly padded strings, so no padding fix needed
            temp_file_quoted = shlex.quote(temp_file)
            content_b64_quoted = shlex.quote(content_b64)
            python_cmd = (
                f'python3 -c "'
                f"import sys, base64; "
                f"temp_file=sys.argv[1]; "
                f"content_b64=sys.argv[2]; "
                f"try: "
                f"  # base64.b64decode handles padding automatically "
                f"  decoded = base64.b64decode(content_b64); "
                f"  f = open(temp_file, 'wb'); "
                f"  f.write(decoded); "
                f"  f.close(); "
                f"except Exception as e: "
                f"  print('Error: ' + str(e), file=sys.stderr); "
                f"  sys.exit(1)"
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


def get_container_health(conn: Connection, container_name: str) -> Dict[str, Any]:
    """Get container health status.

    Args:
        conn: Fabric Connection object
        container_name: Name of the container

    Returns:
        Dictionary with health information
    """
    health_info: Dict[str, Any] = {
        "running": False,
        "health_status": "unknown",
        "uptime": None,
        "restarts": 0,
        "last_restart": None,
        "exit_code": None,
    }

    try:
        # Check if container exists and is running
        result = conn.run(
            f"docker inspect --format='{{{{.State.Running}}}}' {container_name}",
            hide=True,
            warn=True,
        )
        if result.ok and result.stdout.strip() == "true":
            health_info["running"] = True

            # Get health status
            result = conn.run(
                f"docker inspect --format='{{{{.State.Health.Status}}}}' {container_name}",
                hide=True,
                warn=True,
            )
            if result.ok and result.stdout.strip():
                health_info["health_status"] = result.stdout.strip()

            # Get uptime
            result = conn.run(
                f"docker inspect --format='{{{{.State.StartedAt}}}}' {container_name}",
                hide=True,
                warn=True,
            )
            if result.ok:
                health_info["uptime"] = result.stdout.strip()

            # Get restart count
            result = conn.run(
                f"docker inspect --format='{{{{.RestartCount}}}}' {container_name}",
                hide=True,
                warn=True,
            )
            if result.ok:
                try:
                    health_info["restarts"] = int(result.stdout.strip())
                except ValueError:
                    pass

        else:
            # Container not running - get exit code
            result = conn.run(
                f"docker inspect --format='{{{{.State.ExitCode}}}}' {container_name}",
                hide=True,
                warn=True,
            )
            if result.ok:
                try:
                    health_info["exit_code"] = int(result.stdout.strip())
                except ValueError:
                    pass

    except Exception as e:
        console.print(f"[yellow]Warning: Failed to get health info: {e}[/yellow]")

    return health_info


def get_recent_errors(conn: Connection, container_name: str, lines: int = 50) -> str:
    """Get recent error logs from container.

    Args:
        conn: Fabric Connection object
        container_name: Name of the container
        lines: Number of log lines to retrieve (default: 50)

    Returns:
        Recent error logs as string
    """
    try:
        result = conn.run(
            f"docker logs --tail={lines} {container_name} 2>&1 | grep -i 'error\\|exception\\|failed\\|critical' || true",
            hide=True,
            warn=True,
        )
        if result.ok and result.stdout:
            return str(result.stdout.strip())
        return ""
    except Exception:
        return ""
