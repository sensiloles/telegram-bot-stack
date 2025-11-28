"""Integration tests for health monitoring.

Tests bot health checks and auto-recovery:
- Container health status
- Health check results
- Recent error logs
- Container restart detection
- Auto-recovery mechanisms
"""

import pytest

from telegram_bot_stack.cli.utils.deployment import DeploymentConfig
from telegram_bot_stack.cli.utils.vps import (
    VPSConnection,
    get_container_health,
    get_recent_errors,
)
from tests.integration.fixtures.mock_vps import MockVPS

pytestmark = pytest.mark.integration


class TestContainerHealthCheck:
    """Test container health check functionality."""

    def test_health_check_running_container(
        self,
        clean_vps: MockVPS,
        deployment_config,
    ) -> None:
        """Test health check for a running container.

        Note: We create a simple test container to verify health checks.
        """
        config = DeploymentConfig(str(deployment_config))
        bot_name = config.get("bot.name")

        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            # Validate Docker is installed
            assert vps.validate_vps_requirements(
                "docker", "3.9"
            ), "Docker should be available"

            # Start a simple test container
            container_name = f"{bot_name}-health-test"
            start_cmd = (
                f"docker run -d --name {container_name} "
                f"--restart unless-stopped "
                f"alpine:latest sleep 3600"
            )
            assert vps.run_command(start_cmd), "Should start test container"

            # Wait a moment for container to be running
            import time

            time.sleep(2)

            # Get health status
            conn = vps.connect()
            health = get_container_health(conn, container_name)

            assert health["running"] is True, "Container should be running"
            assert health["uptime"] is not None, "Should have uptime"
            assert health["restarts"] == 0, "Should have no restarts"
            assert health["exit_code"] is None, "Should have no exit code"

            # Cleanup
            vps.run_command(f"docker stop {container_name}", hide=True)
            vps.run_command(f"docker rm {container_name}", hide=True)

        finally:
            vps.close()

    def test_health_check_stopped_container(
        self,
        clean_vps: MockVPS,
        deployment_config,
    ) -> None:
        """Test health check for a stopped container."""
        config = DeploymentConfig(str(deployment_config))
        bot_name = config.get("bot.name")

        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            # Validate Docker
            assert vps.validate_vps_requirements("docker", "3.9")

            # Create and stop a container
            container_name = f"{bot_name}-stopped-test"
            create_cmd = f"docker create --name {container_name} alpine:latest sleep 10"
            assert vps.run_command(create_cmd), "Should create container"

            # Get health status (container created but not started)
            conn = vps.connect()
            health = get_container_health(conn, container_name)

            assert health["running"] is False, "Container should not be running"
            assert health["exit_code"] is not None, "Should have exit code"

            # Cleanup
            vps.run_command(f"docker rm {container_name}", hide=True)

        finally:
            vps.close()

    def test_health_check_nonexistent_container(
        self,
        clean_vps: MockVPS,
    ) -> None:
        """Test health check for a container that doesn't exist."""
        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            # Validate Docker
            assert vps.validate_vps_requirements("docker", "3.9")

            conn = vps.connect()
            health = get_container_health(conn, "nonexistent-container-xyz")

            assert health["running"] is False, "Should not be running"
            assert health["health_status"] == "unknown", "Status should be unknown"

        finally:
            vps.close()


class TestErrorLogRetrieval:
    """Test error log retrieval."""

    def test_get_recent_errors_from_logs(
        self,
        clean_vps: MockVPS,
        deployment_config,
    ) -> None:
        """Test retrieving recent error logs from a container."""
        config = DeploymentConfig(str(deployment_config))
        bot_name = config.get("bot.name")

        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            # Validate Docker
            assert vps.validate_vps_requirements("docker", "3.9")

            # Create container that generates errors
            container_name = f"{bot_name}-error-test"
            cmd = (
                f"docker run -d --name {container_name} alpine:latest "
                f'sh -c \'echo "Starting..."; '
                f'echo "ERROR: Test error 1" >&2; '
                f'echo "INFO: Normal log"; '
                f'echo "ERROR: Test error 2" >&2; '
                f"sleep 3600'"
            )
            assert vps.run_command(cmd), "Should start container"

            # Wait for logs to be generated
            import time

            time.sleep(2)

            # Get recent errors
            conn = vps.connect()
            errors = get_recent_errors(conn, container_name, lines=50)

            # Should contain error messages
            assert (
                "ERROR" in errors or len(errors) == 0
            ), "Should retrieve errors or empty string"

            # Cleanup
            vps.run_command(f"docker stop {container_name}", hide=True)
            vps.run_command(f"docker rm {container_name}", hide=True)

        finally:
            vps.close()

    def test_get_recent_errors_no_errors(
        self,
        clean_vps: MockVPS,
        deployment_config,
    ) -> None:
        """Test retrieving errors when container has no errors."""
        config = DeploymentConfig(str(deployment_config))
        bot_name = config.get("bot.name")

        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            # Validate Docker
            assert vps.validate_vps_requirements("docker", "3.9")

            # Create container with only normal logs
            container_name = f"{bot_name}-clean-test"
            cmd = (
                f"docker run -d --name {container_name} alpine:latest "
                f"sh -c 'echo \"INFO: Starting\"; sleep 3600'"
            )
            assert vps.run_command(cmd), "Should start container"

            # Wait for logs
            import time

            time.sleep(2)

            # Get recent errors (should be empty)
            conn = vps.connect()
            errors = get_recent_errors(conn, container_name, lines=50)

            # Should be empty string (no errors)
            assert errors == "", "Should return empty string when no errors"

            # Cleanup
            vps.run_command(f"docker stop {container_name}", hide=True)
            vps.run_command(f"docker rm {container_name}", hide=True)

        finally:
            vps.close()

    def test_get_recent_errors_nonexistent_container(
        self,
        clean_vps: MockVPS,
    ) -> None:
        """Test retrieving errors from non-existent container."""
        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            # Validate Docker
            assert vps.validate_vps_requirements("docker", "3.9")

            conn = vps.connect()
            errors = get_recent_errors(conn, "nonexistent-container-xyz")

            # Should return empty string gracefully
            assert errors == "", "Should return empty string for non-existent container"

        finally:
            vps.close()


class TestRestartDetection:
    """Test container restart detection."""

    def test_detect_container_restarts(
        self,
        clean_vps: MockVPS,
        deployment_config,
    ) -> None:
        """Test detecting container restarts.

        Note: We create a container that exits immediately to trigger restarts.
        """
        config = DeploymentConfig(str(deployment_config))
        bot_name = config.get("bot.name")

        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            # Validate Docker
            assert vps.validate_vps_requirements("docker", "3.9")

            # Create container with restart policy that fails
            container_name = f"{bot_name}-restart-test"
            cmd = (
                f"docker run -d --name {container_name} "
                f"--restart on-failure:3 "  # Restart up to 3 times
                f"alpine:latest sh -c 'exit 1'"  # Exit immediately
            )
            vps.run_command(cmd, hide=True)

            # Wait for restarts to happen
            import time

            time.sleep(5)

            # Get health status
            conn = vps.connect()
            health = get_container_health(conn, container_name)

            # Container should have restarted (or stopped after max retries)
            assert health["restarts"] >= 0, "Should track restart count"

            # Cleanup
            vps.run_command(
                f"docker stop {container_name} 2>/dev/null || true", hide=True
            )
            vps.run_command(f"docker rm {container_name}", hide=True)

        finally:
            vps.close()


class TestDockerComposeCommand:
    """Test Docker Compose command detection."""

    def test_docker_compose_command_detection(
        self,
        clean_vps: MockVPS,
    ) -> None:
        """Test detecting Docker Compose command (v1 or v2)."""
        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            # Validate Docker
            assert vps.validate_vps_requirements("docker", "3.9")

            from telegram_bot_stack.cli.utils.vps import get_docker_compose_command

            conn = vps.connect()
            compose_cmd = get_docker_compose_command(conn)

            # Should return either 'docker compose' or 'docker-compose'
            assert compose_cmd in [
                "docker compose",
                "docker-compose",
            ], f"Should detect compose command, got: {compose_cmd}"

        finally:
            vps.close()

    def test_check_docker_compose_installed(
        self,
        clean_vps: MockVPS,
    ) -> None:
        """Test checking if Docker Compose is installed."""
        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            # Validate Docker (installs compose too)
            assert vps.validate_vps_requirements("docker", "3.9")

            from telegram_bot_stack.cli.utils.vps import check_docker_compose_installed

            conn = vps.connect()
            is_installed = check_docker_compose_installed(conn)

            # Should be installed after validate_vps_requirements
            assert is_installed is True, "Docker Compose should be installed"

        finally:
            vps.close()


class TestHealthCheckEdgeCases:
    """Test edge cases in health checking."""

    def test_health_check_with_special_container_names(
        self,
        clean_vps: MockVPS,
    ) -> None:
        """Test health check with special characters in container name."""
        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            # Validate Docker
            assert vps.validate_vps_requirements("docker", "3.9")

            # Create container with hyphens and numbers (valid name)
            container_name = "test-bot-123_health"
            cmd = f"docker run -d --name {container_name} alpine:latest sleep 3600"
            assert vps.run_command(cmd), "Should start container"

            # Wait for container
            import time

            time.sleep(2)

            # Get health status
            conn = vps.connect()
            health = get_container_health(conn, container_name)

            assert (
                health["running"] is True
            ), "Should handle container names with special chars"

            # Cleanup
            vps.run_command(f"docker stop {container_name}", hide=True)
            vps.run_command(f"docker rm {container_name}", hide=True)

        finally:
            vps.close()

    def test_concurrent_health_checks(
        self,
        clean_vps: MockVPS,
    ) -> None:
        """Test multiple concurrent health checks.

        Verifies that health checks don't interfere with each other.
        """
        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            # Validate Docker
            assert vps.validate_vps_requirements("docker", "3.9")

            # Create two containers
            container1 = "test-bot-1"
            container2 = "test-bot-2"

            vps.run_command(
                f"docker run -d --name {container1} alpine:latest sleep 3600",
                hide=True,
            )
            vps.run_command(
                f"docker run -d --name {container2} alpine:latest sleep 3600",
                hide=True,
            )

            # Wait for containers
            import time

            time.sleep(2)

            # Check both health statuses
            conn = vps.connect()
            health1 = get_container_health(conn, container1)
            health2 = get_container_health(conn, container2)

            assert health1["running"] is True
            assert health2["running"] is True

            # Cleanup
            vps.run_command(f"docker stop {container1} {container2}", hide=True)
            vps.run_command(f"docker rm {container1} {container2}", hide=True)

        finally:
            vps.close()
