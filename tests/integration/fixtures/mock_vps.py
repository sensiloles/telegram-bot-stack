"""Mock VPS fixture using Testcontainers for integration testing."""

import time
from pathlib import Path
from typing import Generator

import pytest
from testcontainers.core.container import DockerContainer


class MockVPS:
    """Mock VPS container for integration testing using Testcontainers."""

    def __init__(self, container: DockerContainer, ssh_key_path: str):
        """Initialize Mock VPS.

        Args:
            container: Testcontainers DockerContainer instance
            ssh_key_path: Path to SSH private key
        """
        self.container = container
        self.host = "127.0.0.1"
        self.user = "root"
        self.ssh_key_path = ssh_key_path
        self.port = int(container.get_exposed_port(22))

    def exec(self, command: str) -> str:
        """Execute command in container.

        Args:
            command: Command to execute

        Returns:
            Command output
        """
        result = self.container.exec(command)
        return result.output.decode("utf-8") if result.output else ""

    def cleanup(self) -> None:
        """Clean up test bot containers (not the Mock VPS itself)."""
        # Stop and remove bot containers created during tests
        self.exec(
            "docker ps -a --filter 'name=test-bot' --filter 'name=bot-' -q | "
            "xargs -r docker stop 2>/dev/null || true"
        )
        self.exec(
            "docker ps -a --filter 'name=test-bot' --filter 'name=bot-' -q | "
            "xargs -r docker rm 2>/dev/null || true"
        )

        # Remove test volumes
        self.exec(
            "docker volume ls --filter 'name=test-bot' --filter 'name=bot-' -q | "
            "xargs -r docker volume rm 2>/dev/null || true"
        )


@pytest.fixture(scope="session")
def mock_vps() -> Generator[MockVPS, None, None]:
    """Pytest fixture for Mock VPS using Testcontainers.

    This fixture creates a Docker container simulating a VPS with SSH access.
    Scope is 'session' to reuse the same container across all tests.

    Yields:
        MockVPS instance
    """
    # Generate SSH key
    key_dir = Path(__file__).parent / ".ssh-test"
    key_dir.mkdir(exist_ok=True)
    key_path = key_dir / "id_rsa"

    # Generate SSH key if it doesn't exist
    if not key_path.exists():
        import subprocess

        subprocess.run(
            ["ssh-keygen", "-t", "rsa", "-b", "4096", "-f", str(key_path), "-N", ""],
            check=True,
            capture_output=True,
        )

    # Create and start container using Testcontainers
    container = (
        DockerContainer("mock-vps:latest")
        .with_bind_ports(22, None)  # Auto-assign port
        .with_name(f"mock-vps-test-{int(time.time())}")
        .with_kwargs(privileged=True)  # For Docker-in-Docker
    )

    # Start container
    container.start()

    # Wait a moment for container to be fully up
    time.sleep(1)

    # Copy SSH public key to container using docker cp (more reliable than exec)
    import subprocess
    import tempfile

    pub_key_path = key_path.parent / f"{key_path.name}.pub"

    # Write public key to temp file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".pub") as tmp:
        tmp.write(pub_key_path.read_text())
        tmp_path = tmp.name

    try:
        # Copy public key to container
        container_id = container.get_wrapped_container().id
        subprocess.run(
            ["docker", "cp", tmp_path, f"{container_id}:/root/.ssh/authorized_keys"],
            check=True,
            timeout=5,
            capture_output=True,
        )
        # Set correct permissions and ownership
        subprocess.run(
            [
                "docker",
                "exec",
                container_id,
                "chown",
                "root:root",
                "/root/.ssh/authorized_keys",
            ],
            check=True,
            timeout=5,
            capture_output=True,
        )
        subprocess.run(
            [
                "docker",
                "exec",
                container_id,
                "chmod",
                "600",
                "/root/.ssh/authorized_keys",
            ],
            check=True,
            timeout=5,
            capture_output=True,
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    # Wait for SSH daemon to be ready with timeout
    import socket
    import subprocess

    max_retries = 30
    ssh_port = int(container.get_exposed_port(22))

    for attempt in range(max_retries):
        try:
            # Try to connect to SSH port (faster than exec or full SSH)
            with socket.create_connection(("127.0.0.1", ssh_port), timeout=1):
                # Port is open, wait a bit more and test SSH
                time.sleep(0.5)

                ssh_result = subprocess.run(
                    [
                        "ssh",
                        "-i",
                        str(key_path.absolute()),
                        "-p",
                        str(ssh_port),
                        "-o",
                        "StrictHostKeyChecking=no",
                        "-o",
                        "UserKnownHostsFile=/dev/null",
                        "-o",
                        "ConnectTimeout=2",
                        "-o",
                        "ServerAliveInterval=1",
                        "root@127.0.0.1",
                        "echo ready",
                    ],
                    capture_output=True,
                    timeout=5,
                )
                if ssh_result.returncode == 0:
                    break
        except (OSError, subprocess.TimeoutExpired, Exception):
            pass

        if attempt < max_retries - 1:
            time.sleep(1)
    else:
        container.stop()
        raise RuntimeError(
            f"Mock VPS SSH not ready after {max_retries} retries on port {ssh_port}"
        )

    # Create MockVPS instance
    vps = MockVPS(container, str(key_path.absolute()))

    yield vps

    # Cleanup: stop container
    try:
        container.stop()
    except Exception:
        pass  # Container might already be stopped


@pytest.fixture
def clean_vps(mock_vps: MockVPS) -> Generator[MockVPS, None, None]:
    """Pytest fixture for clean VPS.

    Cleans up any test containers before and after each test.

    Args:
        mock_vps: Mock VPS fixture

    Yields:
        Clean MockVPS instance
    """
    # Cleanup before test
    mock_vps.cleanup()

    # Fix any broken apt packages from previous tests
    try:
        mock_vps.container.exec("dpkg --configure -a 2>&1 || true")
        mock_vps.container.exec("apt-get --fix-broken install -y 2>&1 || true")
        mock_vps.container.exec("apt-get update 2>&1 || true")
    except Exception:
        pass  # Ignore errors during cleanup

    # Ensure Docker daemon is stopped (to avoid conflicts)
    try:
        mock_vps.container.exec("pkill dockerd 2>&1 || true")
    except Exception:
        pass

    yield mock_vps

    # Cleanup after test
    mock_vps.cleanup()

    # Fix packages again after test
    try:
        mock_vps.container.exec("dpkg --configure -a 2>&1 || true")
        mock_vps.container.exec("apt-get --fix-broken install -y 2>&1 || true")
    except Exception:
        pass
