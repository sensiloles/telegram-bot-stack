"""Mock VPS fixture using Testcontainers for integration testing."""

import logging
import os
import time
from pathlib import Path
from typing import Generator

import pytest
from testcontainers.core.container import DockerContainer

# Configure logging for integration tests
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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
        logger.debug(f"[MockVPS] Executing command: {command[:100]}")
        result = self.container.exec(command)
        output = result.output.decode("utf-8") if result.output else ""
        logger.debug(f"[MockVPS] Command output: {output[:200]}")
        return output

    def cleanup(self) -> None:
        """Clean up test bot containers (not the Mock VPS itself)."""
        logger.info("[MockVPS] Cleaning up test containers...")
        # Stop and remove bot containers created during tests
        # Note: Use grep -v trick to avoid xargs errors on empty input (xargs -r is GNU-only)
        self.exec(
            "docker ps -a --filter name=test-bot --filter name=bot- -q 2>/dev/null | "
            "grep . | xargs docker stop 2>/dev/null || true"
        )
        self.exec(
            "docker ps -a --filter name=test-bot --filter name=bot- -q 2>/dev/null | "
            "grep . | xargs docker rm 2>/dev/null || true"
        )

        # Remove test volumes
        self.exec(
            "docker volume ls --filter name=test-bot --filter name=bot- -q 2>/dev/null | "
            "grep . | xargs docker volume rm 2>/dev/null || true"
        )
        logger.info("[MockVPS] Cleanup complete")


@pytest.fixture(scope="session")
def mock_vps() -> Generator[MockVPS, None, None]:
    """Pytest fixture for Mock VPS using Testcontainers.

    This fixture creates a Docker container simulating a VPS with SSH access.
    Scope is 'session' to reuse the same container across all tests.

    Yields:
        MockVPS instance
    """
    logger.info("=" * 80)
    logger.info("[MockVPS] Starting Mock VPS container setup...")
    logger.info("=" * 80)

    # Generate SSH key
    key_dir = Path(__file__).parent / ".ssh-test"
    key_dir.mkdir(exist_ok=True)
    key_path = key_dir / "id_rsa"

    # Generate SSH key if it doesn't exist
    if not key_path.exists():
        import subprocess

        logger.info(f"[MockVPS] Generating SSH key at {key_path}")
        subprocess.run(
            ["ssh-keygen", "-t", "rsa", "-b", "4096", "-f", str(key_path), "-N", ""],
            check=True,
            capture_output=True,
        )
        logger.info("[MockVPS] SSH key generated successfully")
    else:
        logger.info(f"[MockVPS] Using existing SSH key at {key_path}")

    # Create and start container using Testcontainers
    # Use PID + timestamp to ensure unique names when running in parallel
    unique_id = f"{os.getpid()}-{int(time.time())}"
    container_name = f"mock-vps-test-{unique_id}"
    logger.info(
        f"[MockVPS] Creating container '{container_name}' from image 'mock-vps:latest'"
    )

    container = (
        DockerContainer("mock-vps:latest")
        .with_bind_ports(22, None)  # Auto-assign port
        .with_name(container_name)
        .with_kwargs(privileged=True)  # For Docker-in-Docker
    )

    # Start container
    logger.info("[MockVPS] Starting container...")
    container.start()
    container_id = container.get_wrapped_container().id[:12]
    logger.info(f"[MockVPS] Container started: {container_id}")

    # Wait a moment for container to be fully up
    logger.info("[MockVPS] Waiting for container initialization...")
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
        logger.info(
            f"[MockVPS] Copying SSH public key to container {container_id[:12]}"
        )
        subprocess.run(
            ["docker", "cp", tmp_path, f"{container_id}:/root/.ssh/authorized_keys"],
            check=True,
            timeout=10,  # Increased timeout for reliability
            capture_output=True,
        )
        logger.debug("[MockVPS] Setting SSH key permissions...")
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
            timeout=10,  # Increased timeout for reliability
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
            timeout=10,  # Increased timeout for reliability
            capture_output=True,
        )
        logger.info("[MockVPS] SSH key configured successfully")
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    # Wait for SSH daemon to be ready with timeout
    import socket
    import subprocess

    max_retries = 30
    ssh_port = int(container.get_exposed_port(22))
    logger.info(f"[MockVPS] Waiting for SSH daemon on port {ssh_port}...")
    logger.info(f"[MockVPS] Will retry up to {max_retries} times (max ~30 seconds)")

    for attempt in range(max_retries):
        try:
            # Try to connect to SSH port (faster than exec or full SSH)
            with socket.create_connection(("127.0.0.1", ssh_port), timeout=1):
                # Port is open, wait a bit more and test SSH
                time.sleep(0.5)

                logger.debug(
                    f"[MockVPS] Attempt {attempt + 1}/{max_retries}: Testing SSH connection..."
                )
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
                    timeout=10,  # Increased timeout for reliability
                )
                if ssh_result.returncode == 0:
                    logger.info(
                        f"[MockVPS] SSH connection successful on attempt {attempt + 1}"
                    )
                    break
                else:
                    logger.debug(
                        f"[MockVPS] SSH test failed: {ssh_result.stderr[:100]}"
                    )
        except (OSError, subprocess.TimeoutExpired, Exception) as e:
            logger.debug(
                f"[MockVPS] Connection attempt {attempt + 1} failed: {type(e).__name__}"
            )

        if attempt < max_retries - 1:
            time.sleep(1)
    else:
        logger.error(f"[MockVPS] SSH not ready after {max_retries} retries!")
        logger.error("[MockVPS] Fetching container logs for debugging...")
        try:
            import subprocess

            logs = subprocess.run(
                ["docker", "logs", container_id, "--tail", "50"],
                capture_output=True,
                timeout=10,  # Increased timeout for reliability
            )
            logger.error(f"[MockVPS] Container logs:\n{logs.stdout.decode('utf-8')}")
            logger.error(f"[MockVPS] Container errors:\n{logs.stderr.decode('utf-8')}")
        except Exception as e:
            logger.error(f"[MockVPS] Failed to fetch logs: {e}")

        container.stop()
        raise RuntimeError(
            f"Mock VPS SSH not ready after {max_retries} retries on port {ssh_port}"
        )

    # Create MockVPS instance
    vps = MockVPS(container, str(key_path.absolute()))
    logger.info("=" * 80)
    logger.info(f"[MockVPS] Mock VPS ready! SSH: root@127.0.0.1:{ssh_port}")
    logger.info(f"[MockVPS] Container ID: {container_id}")
    logger.info("=" * 80)

    yield vps

    # Cleanup: stop container
    logger.info("=" * 80)
    logger.info("[MockVPS] Stopping Mock VPS container...")
    try:
        container.stop()
        logger.info("[MockVPS] Container stopped successfully")
    except Exception as e:
        logger.warning(f"[MockVPS] Error stopping container: {e}")
    logger.info("=" * 80)


@pytest.fixture
def clean_vps(mock_vps: MockVPS) -> Generator[MockVPS, None, None]:
    """Pytest fixture for clean VPS.

    Cleans up any test containers before and after each test.
    Uses lightweight cleanup for better performance.

    Args:
        mock_vps: Mock VPS fixture

    Yields:
        Clean MockVPS instance
    """
    logger.info("[clean_vps] Preparing clean VPS for test...")

    # Lightweight cleanup before test (only containers, not full package fix)
    mock_vps.cleanup()

    # Only fix packages if there are actual errors (check first)
    logger.debug("[clean_vps] Checking for broken packages...")
    try:
        # Use bash -c to properly handle shell redirections
        check_result = mock_vps.exec("/bin/bash -c 'dpkg --audit 2>&1'")
        if check_result.strip():  # Only fix if there are broken packages
            logger.debug("[clean_vps] Fixing broken packages...")
            mock_vps.exec("/bin/bash -c 'dpkg --configure -a 2>&1 || true'")
            mock_vps.exec("/bin/bash -c 'apt-get --fix-broken install -y 2>&1 || true'")
    except Exception as e:
        logger.debug(f"[clean_vps] Package check error (ignored): {e}")

    # Ensure Docker daemon is stopped (to avoid conflicts)
    logger.debug("[clean_vps] Stopping Docker daemon...")
    try:
        mock_vps.exec("pkill dockerd 2>&1 || true")
    except Exception as e:
        logger.debug(f"[clean_vps] Docker stop error (ignored): {e}")

    logger.info("[clean_vps] Clean VPS ready for test")
    yield mock_vps

    # Lightweight cleanup after test
    logger.info("[clean_vps] Cleaning up after test...")
    mock_vps.cleanup()

    # Only fix packages if needed (lightweight check)
    logger.debug("[clean_vps] Post-test cleanup...")
    try:
        # Use bash -c to properly handle shell redirections
        check_result = mock_vps.exec("/bin/bash -c 'dpkg --audit 2>&1'")
        if check_result.strip():
            mock_vps.exec("/bin/bash -c 'dpkg --configure -a 2>&1 || true'")
    except Exception as e:
        logger.debug(f"[clean_vps] Post-test cleanup error (ignored): {e}")

    logger.info("[clean_vps] Test cleanup complete")
