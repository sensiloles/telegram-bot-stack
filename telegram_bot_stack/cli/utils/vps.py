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
from invoke import Config
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

    def __enter__(self) -> "VPSConnection":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Exit context manager and close connection."""
        self.close()

    def test_connection(self) -> bool:
        """Test SSH connection to VPS.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            with console.status("[cyan]Testing SSH connection..."):
                conn = self._create_connection()
                result = conn.run(
                    "echo 'Connection test'", hide=True, pty=False, in_stream=False
                )
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

        # Configure Fabric to work with pytest's capture system
        # Disable all I/O threads to avoid ThreadException when pytest captures output
        # Use /dev/null for stdin to prevent thread from trying to read from closed stream

        config = Config(
            overrides={
                "run": {
                    "in_stream": False,  # Disable stdin thread (fixes ThreadException)
                    "watchers": [],  # Disable watchers
                }
            }
        )

        return Connection(
            host=self.host,
            user=self.user,
            port=self.port,
            connect_kwargs=connect_kwargs,
            config=config,
            inline_ssh_env=True,  # Use inline env vars instead of shell source
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
            # For long-running commands, show periodic updates
            if not hide and (
                "docker build" in command.lower() or "make build" in command.lower()
            ):
                console.print(
                    "[dim]   Running command (output will appear when complete)...[/dim]"
                )
            # Disable pty and in_stream to prevent ThreadException in tests
            # pty=False is safer for automated scripts, in_stream=False prevents stdin thread
            result = conn.run(command, hide=hide, pty=False, in_stream=False)
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
            "cat /etc/os-release | grep '^ID=' | cut -d'=' -f2",
            hide=True,
            pty=False,
            in_stream=False,
        )
        os_id = os_info.stdout.strip().strip('"') if os_info.ok else "ubuntu"

        commands = []
        if os_id in ["ubuntu", "debian"]:
            commands = [
                # Update package list
                "DEBIAN_FRONTEND=noninteractive apt-get update",
                # Install prerequisites
                "DEBIAN_FRONTEND=noninteractive apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release",
                # Add Docker GPG key
                "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg",
                # Add Docker repository
                'echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null',
                # Install Docker
                "DEBIAN_FRONTEND=noninteractive apt-get update",
                "DEBIAN_FRONTEND=noninteractive apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin",
                # Install standalone Docker Compose (fallback for older systems)
                "curl -SL https://github.com/docker/compose/releases/download/v2.32.4/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose",
                "chmod +x /usr/local/bin/docker-compose",
            ]
        elif os_id in ["centos", "rhel", "fedora"]:
            commands = [
                "yum install -y yum-utils",
                "yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo",
                "yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin",
                "systemctl start docker",
                "systemctl enable docker",
                # Install standalone Docker Compose (fallback)
                "curl -SL https://github.com/docker/compose/releases/download/v2.32.4/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose",
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
                "python3 --version 2>&1 || python --version 2>&1",
                hide=True,
                pty=False,
                in_stream=False,
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
            "cat /etc/os-release | grep '^ID=' | cut -d'=' -f2",
            hide=True,
            pty=False,
            in_stream=False,
        )
        os_id = os_info.stdout.strip().strip('"') if os_info.ok else "ubuntu"

        major, minor = version.split(".")[:2]
        commands = []

        if os_id in ["ubuntu", "debian"]:
            # For Ubuntu/Debian, use deadsnakes PPA for newer Python versions
            commands = [
                "DEBIAN_FRONTEND=noninteractive apt-get update",
                "DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common",
                "DEBIAN_FRONTEND=noninteractive add-apt-repository -y ppa:deadsnakes/ppa",
                "DEBIAN_FRONTEND=noninteractive apt-get update",
                f"DEBIAN_FRONTEND=noninteractive apt-get install -y python{version} python{version}-venv python{version}-dev python3-pip",
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
            conn.run(
                f"mkdir -p {shlex.quote(remote_path)}",
                hide=True,
                pty=False,
                in_stream=False,
            )

            console.print(f"[cyan]Transferring files to {remote_path}...[/cyan]")

            # Try rsync first (faster), fallback to SFTP if unavailable
            import glob
            import subprocess

            try:
                # Build rsync command with SSH options
                ssh_opts = "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"

                if self.ssh_key:
                    ssh_key_quoted = shlex.quote(self.ssh_key)
                    ssh_cmd = f"ssh -i {ssh_key_quoted} -p {self.port} {ssh_opts}"
                else:
                    ssh_cmd = f"ssh -p {self.port} {ssh_opts}"

                ssh_key_arg = f"-e {shlex.quote(ssh_cmd)}"
                local_path_quoted = shlex.quote(str(local_path))
                remote_path_quoted = shlex.quote(remote_path)
                rsync_cmd = f"rsync -avz --delete {ssh_key_arg} {local_path_quoted}/ {self.user}@{self.host}:{remote_path_quoted}/"

                result = subprocess.run(
                    rsync_cmd, shell=True, capture_output=True, text=True, timeout=60
                )

                if result.returncode == 0:
                    console.print(
                        "[green]✓ Files transferred successfully (rsync)[/green]"
                    )
                    return True
                # If rsync failed, fall through to SFTP fallback
                console.print(
                    "[yellow]rsync not available, using SFTP fallback...[/yellow]"
                )
            except Exception:
                console.print("[yellow]Using SFTP for file transfer...[/yellow]")

            # Fallback: Use Fabric's put (SFTP) to transfer files
            file_count = 0
            for item in glob.glob(f"{local_path}/**/*", recursive=True):
                item_path = Path(item)
                if item_path.is_file():
                    # Calculate relative path
                    rel_path = item_path.relative_to(local_path)
                    remote_file_path = f"{remote_path}/{rel_path}"

                    # Create parent directory on remote
                    remote_parent = str(Path(remote_file_path).parent)
                    conn.run(
                        f"mkdir -p {shlex.quote(remote_parent)}",
                        hide=True,
                        pty=False,
                        in_stream=False,
                    )

                    # Transfer file
                    conn.put(str(item_path), remote_file_path)
                    file_count += 1

            console.print(
                f"[green]✓ {file_count} files transferred successfully (SFTP)[/green]"
            )
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
                conn.run(
                    f"mkdir -p {shlex.quote(remote_dir)}",
                    hide=True,
                    pty=False,
                    in_stream=False,
                )

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
            # Use Python one-liner to decode and write file
            # Split into multiple lines in shell command using semicolons
            python_cmd = (
                f"python3 -c 'import sys, base64; "
                f'f=open(sys.argv[1], "wb"); '
                f"f.write(base64.b64decode(sys.argv[2])); "
                f"f.close()' "
                f"{temp_file_quoted} {content_b64_quoted}"
            )
            conn.run(python_cmd, hide=True, pty=False, in_stream=False)

            # Move to final location and set permissions
            # Properly escape file paths to prevent command injection
            conn.run(
                f"mv {shlex.quote(temp_file)} {shlex.quote(remote_path)}",
                hide=True,
                pty=False,
                in_stream=False,
            )
            conn.run(
                f"chmod {mode} {shlex.quote(remote_path)}",
                hide=True,
                pty=False,
                in_stream=False,
            )

            return True
        except Exception as e:
            console.print(f"[red]Failed to write file: {e}[/red]")
            return False

    def close(self) -> None:
        """Close SSH connection."""
        if self.connection:
            self.connection.close()
            self.connection = None


def get_docker_compose_command(conn: Connection) -> str:
    """Get the appropriate docker compose command (v2 or v1).

    Tries 'docker compose' (v2, built-in) first, falls back to 'docker-compose' (v1, standalone).

    Args:
        conn: Fabric Connection object

    Returns:
        'docker compose' or 'docker-compose' depending on what's available
    """
    try:
        # Try new built-in command first (Docker Compose v2)
        result = conn.run(
            "docker compose version", hide=True, warn=True, pty=False, in_stream=False
        )
        if result.ok:
            return "docker compose"
    except Exception:
        pass

    try:
        # Fall back to standalone docker-compose (v1)
        result = conn.run(
            "docker-compose --version",
            hide=True,
            warn=True,
            pty=False,
            in_stream=False,
        )
        if result.ok:
            return "docker-compose"
    except Exception:
        pass

    # Default to v2 (will fail if not installed, but that's expected)
    return "docker compose"


def check_docker_compose_installed(conn: Connection) -> bool:
    """Check if Docker Compose is installed.

    Args:
        conn: Fabric Connection object

    Returns:
        True if Docker Compose is installed, False otherwise
    """
    try:
        # Try v2 first
        result = conn.run(
            "docker compose version", hide=True, warn=True, pty=False, in_stream=False
        )
        if result.ok:
            return True
    except Exception:
        pass

    try:
        # Fall back to v1
        result = conn.run(
            "docker-compose --version",
            hide=True,
            warn=True,
            pty=False,
            in_stream=False,
        )
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
            pty=False,
            in_stream=False,
        )
        if result.ok and result.stdout.strip() == "true":
            health_info["running"] = True

            # Get health status
            result = conn.run(
                f"docker inspect --format='{{{{.State.Health.Status}}}}' {container_name}",
                hide=True,
                warn=True,
                pty=False,
                in_stream=False,
            )
            if result.ok and result.stdout.strip():
                health_info["health_status"] = result.stdout.strip()

            # Get uptime
            result = conn.run(
                f"docker inspect --format='{{{{.State.StartedAt}}}}' {container_name}",
                hide=True,
                warn=True,
                pty=False,
                in_stream=False,
            )
            if result.ok:
                health_info["uptime"] = result.stdout.strip()

            # Get restart count
            result = conn.run(
                f"docker inspect --format='{{{{.RestartCount}}}}' {container_name}",
                hide=True,
                warn=True,
                pty=False,
                in_stream=False,
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
                pty=False,
                in_stream=False,
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
            pty=False,
            in_stream=False,
        )
        if result.ok and result.stdout:
            output = str(result.stdout.strip())
            # If container doesn't exist, docker logs returns error message
            # Return empty string for non-existent containers
            if "No such container" in output or "Error response from daemon" in output:
                return ""
            return output
        return ""
    except Exception:
        return ""
