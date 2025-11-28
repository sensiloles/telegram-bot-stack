"""Mock VPS fixture for testing deployment.

This module provides fixtures for creating and managing a mock VPS
environment using Docker containers for integration testing.
"""

import subprocess
import time
from pathlib import Path
from typing import Generator, Optional

import pytest


class MockVPS:
    """Mock VPS environment for testing."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 2222,
        user: str = "root",
        ssh_key_path: Optional[str] = None,
    ):
        """Initialize Mock VPS.

        Args:
            host: VPS hostname (default: localhost)
            port: SSH port (default: 2222)
            user: SSH user (default: root)
            ssh_key_path: Path to SSH private key
        """
        self.host = host
        self.port = port
        self.user = user
        self.ssh_key_path = ssh_key_path or self._generate_ssh_key()
        self.container_name = "telegram-bot-stack-mock-vps"
        self._started = False

    def _generate_ssh_key(self) -> str:
        """Get path for SSH key (will be copied from container).

        Returns:
            Absolute path where private key will be stored
        """
        key_dir = Path(__file__).parent / ".ssh-test"
        key_dir.mkdir(exist_ok=True)
        key_path = key_dir / "id_rsa"

        return str(key_path.absolute())

    def start(self) -> None:
        """Start Mock VPS container."""
        if self._started:
            return

        fixtures_dir = Path(__file__).parent

        # Build and start container
        # Try docker compose (v2) first, fallback to docker-compose (v1)
        try:
            subprocess.run(
                [
                    "docker",
                    "compose",
                    "-f",
                    str(fixtures_dir / "docker-compose.mock-vps.yml"),
                    "up",
                    "-d",
                    "--build",
                ],
                check=True,
                cwd=str(fixtures_dir),
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            subprocess.run(
                [
                    "docker-compose",
                    "-f",
                    str(fixtures_dir / "docker-compose.mock-vps.yml"),
                    "up",
                    "-d",
                    "--build",
                ],
                check=True,
                cwd=str(fixtures_dir),
            )

        # Wait a bit for container to start
        time.sleep(3)

        # Copy SSH key from container first
        self._setup_ssh_key()

        # Wait for SSH to be ready (now we have the key to test connection)
        self._wait_for_ssh()

        self._started = True

    def stop(self) -> None:
        """Stop Mock VPS container."""
        if not self._started:
            return

        fixtures_dir = Path(__file__).parent

        # Try docker compose (v2) first, fallback to docker-compose (v1)
        try:
            subprocess.run(
                [
                    "docker",
                    "compose",
                    "-f",
                    str(fixtures_dir / "docker-compose.mock-vps.yml"),
                    "down",
                    "-v",
                ],
                check=True,
                cwd=str(fixtures_dir),
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            subprocess.run(
                [
                    "docker-compose",
                    "-f",
                    str(fixtures_dir / "docker-compose.mock-vps.yml"),
                    "down",
                    "-v",
                ],
                check=True,
                cwd=str(fixtures_dir),
            )

        self._started = False

    def _wait_for_ssh(self, timeout: int = 60) -> None:
        """Wait for SSH to be available.

        Args:
            timeout: Maximum time to wait in seconds
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Check if sshd process is running
                result = subprocess.run(
                    [
                        "docker",
                        "exec",
                        self.container_name,
                        "pgrep",
                        "-x",
                        "sshd",
                    ],
                    capture_output=True,
                    timeout=5,
                )
                if result.returncode == 0 and result.stdout.strip():
                    # Give SSH a moment to fully initialize
                    time.sleep(2)

                    # Test actual SSH connection
                    try:
                        ssh_test = subprocess.run(
                            [
                                "ssh",
                                "-i",
                                self.ssh_key_path,
                                "-p",
                                str(self.port),
                                "-o",
                                "StrictHostKeyChecking=no",
                                "-o",
                                "UserKnownHostsFile=/dev/null",
                                "-o",
                                "ConnectTimeout=5",
                                f"{self.user}@{self.host}",
                                "echo 'SSH ready'",
                            ],
                            capture_output=True,
                            timeout=10,
                        )
                        if ssh_test.returncode == 0:
                            return
                    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                        pass

            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                pass

            time.sleep(2)

        raise TimeoutError("SSH service did not start in time")

    def _setup_ssh_key(self) -> None:
        """Copy SSH private key FROM container to use for tests.

        The container generates its own SSH key pair during build.
        We copy the private key from the container to the host so tests
        can use it to connect via SSH.
        """
        # Ensure SSH key directory exists
        key_dir = Path(self.ssh_key_path).parent
        key_dir.mkdir(parents=True, exist_ok=True)

        # Copy private key from container to host
        subprocess.run(
            [
                "docker",
                "cp",
                f"{self.container_name}:/root/.ssh/id_rsa",
                str(self.ssh_key_path),
            ],
            check=True,
        )

        # Set correct permissions for private key
        subprocess.run(["chmod", "600", str(self.ssh_key_path)], check=True)

        # Also copy public key for reference
        pub_key_path = f"{self.ssh_key_path}.pub"
        subprocess.run(
            [
                "docker",
                "cp",
                f"{self.container_name}:/root/.ssh/id_rsa.pub",
                pub_key_path,
            ],
            check=True,
        )

    def exec(self, command: str) -> tuple[int, str, str]:
        """Execute command in container.

        Args:
            command: Command to execute

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        result = subprocess.run(
            ["docker", "exec", self.container_name, "bash", "-c", command],
            capture_output=True,
            text=True,
        )

        return result.returncode, result.stdout, result.stderr

    def is_container_running(self, container_name: str) -> bool:
        """Check if a container is running inside Mock VPS.

        Args:
            container_name: Name of container to check

        Returns:
            True if container is running
        """
        exit_code, stdout, _ = self.exec(
            f"docker ps --filter name={container_name} --format '{{{{.Names}}}}'"
        )

        return exit_code == 0 and container_name in stdout

    def get_container_logs(self, container_name: str) -> str:
        """Get logs from container inside Mock VPS.

        Args:
            container_name: Name of container

        Returns:
            Container logs
        """
        _, stdout, _ = self.exec(f"docker logs {container_name}")
        return stdout

    def cleanup(self) -> None:
        """Clean up test bot containers and volumes (but NOT the Mock VPS itself)."""
        # Stop and remove bot containers (but not the Mock VPS container)
        # Look for containers that match typical bot names
        self.exec(
            "docker ps -a --filter 'name=test-bot' --filter 'name=bot-' -q | "
            "xargs -r docker stop 2>/dev/null || true"
        )
        self.exec(
            "docker ps -a --filter 'name=test-bot' --filter 'name=bot-' -q | "
            "xargs -r docker rm 2>/dev/null || true"
        )

        # Remove test volumes (but preserve mock-vps volumes)
        self.exec(
            "docker volume ls --filter 'name=test-bot' --filter 'name=bot-' -q | "
            "xargs -r docker volume rm 2>/dev/null || true"
        )


@pytest.fixture(scope="session")
def mock_vps() -> Generator[MockVPS, None, None]:
    """Pytest fixture for Mock VPS environment.

    Yields:
        MockVPS instance for testing
    """
    # Skip if Docker not available
    try:
        subprocess.run(
            ["docker", "version"], capture_output=True, check=True, timeout=5
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        pytest.skip("Docker not available")

    vps = MockVPS()

    try:
        vps.start()
        yield vps
    finally:
        vps.cleanup()
        vps.stop()


@pytest.fixture
def clean_vps(mock_vps: MockVPS) -> Generator[MockVPS, None, None]:
    """Pytest fixture for clean VPS.

    Args:
        mock_vps: Mock VPS fixture

    Yields:
        Clean MockVPS instance
    """
    # Verify Mock VPS is started
    assert mock_vps._started, "Mock VPS must be started"

    # Give SSH a moment to be ready (simple approach)
    import time

    time.sleep(1)

    yield mock_vps

    # Cleanup after test to remove any bot containers created during the test
    mock_vps.cleanup()
