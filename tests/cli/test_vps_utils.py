"""Tests for VPS utilities."""

from unittest.mock import MagicMock, patch

from telegram_bot_stack.cli.utils.vps import (
    VPSConnection,
    check_docker_compose_installed,
    get_container_health,
    get_recent_errors,
)


class TestVPSConnection:
    """Tests for VPSConnection class."""

    def test_init(self):
        """Test VPSConnection initialization."""
        vps = VPSConnection(
            host="test.example.com", user="root", ssh_key="~/.ssh/id_rsa", port=22
        )

        assert vps.host == "test.example.com"
        assert vps.user == "root"
        assert vps.port == 22
        assert vps.connection is None

    def test_test_connection_success(self):
        """Test successful connection test."""
        vps = VPSConnection(host="test.example.com", user="root")

        with patch.object(vps, "_create_connection") as mock_create:
            mock_conn = MagicMock()
            mock_result = MagicMock()
            mock_result.ok = True
            mock_conn.run.return_value = mock_result
            mock_create.return_value = mock_conn

            result = vps.test_connection()

            assert result is True
            mock_conn.run.assert_called_once()

    def test_test_connection_failure(self):
        """Test failed connection test."""
        vps = VPSConnection(host="test.example.com", user="root")

        with patch.object(vps, "_create_connection") as mock_create:
            mock_create.side_effect = Exception("Connection failed")

            result = vps.test_connection()

            assert result is False

    def test_run_command_success(self):
        """Test successful command execution."""
        vps = VPSConnection(host="test.example.com", user="root")

        with patch.object(vps, "connect") as mock_connect:
            mock_conn = MagicMock()
            mock_result = MagicMock()
            mock_result.ok = True
            mock_conn.run.return_value = mock_result
            mock_connect.return_value = mock_conn

            result = vps.run_command("echo test")

            assert result is True
            mock_conn.run.assert_called_once_with("echo test", hide=False)

    def test_run_command_failure(self):
        """Test failed command execution."""
        vps = VPSConnection(host="test.example.com", user="root")

        with patch.object(vps, "connect") as mock_connect:
            mock_connect.side_effect = Exception("Command failed")

            result = vps.run_command("invalid command")

            assert result is False

    def test_check_docker_installed_true(self):
        """Test Docker installed check (installed)."""
        vps = VPSConnection(host="test.example.com", user="root")

        with patch.object(vps, "run_command") as mock_run:
            mock_run.return_value = True

            result = vps.check_docker_installed()

            assert result is True
            mock_run.assert_called_once_with("docker --version", hide=True)

    def test_check_docker_installed_false(self):
        """Test Docker installed check (not installed)."""
        vps = VPSConnection(host="test.example.com", user="root")

        with patch.object(vps, "run_command") as mock_run:
            mock_run.return_value = False

            result = vps.check_docker_installed()

            assert result is False

    def test_install_docker_success(self):
        """Test successful Docker installation."""
        vps = VPSConnection(host="test.example.com", user="root")

        # Mock connection and os detection
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.ok = True
        mock_result.stdout = "ubuntu"
        mock_conn.run.return_value = mock_result

        with (
            patch.object(vps, "connect", return_value=mock_conn),
            patch.object(vps, "run_command") as mock_run,
        ):
            mock_run.return_value = True

            result = vps.install_docker()

            assert result is True
            # Should call multiple commands
            assert mock_run.call_count > 5

    def test_install_docker_failure(self):
        """Test failed Docker installation."""
        vps = VPSConnection(host="test.example.com", user="root")

        # Mock connection and os detection
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.ok = True
        mock_result.stdout = "ubuntu"
        mock_conn.run.return_value = mock_result

        with (
            patch.object(vps, "connect", return_value=mock_conn),
            patch.object(vps, "run_command") as mock_run,
        ):
            mock_run.return_value = False

            result = vps.install_docker()

            assert result is False

    def test_close_connection(self):
        """Test closing connection."""
        vps = VPSConnection(host="test.example.com", user="root")

        mock_conn = MagicMock()
        vps.connection = mock_conn

        vps.close()

        mock_conn.close.assert_called_once()
        assert vps.connection is None


class TestCheckDockerComposeInstalled:
    """Tests for check_docker_compose_installed function."""

    def test_docker_compose_installed(self):
        """Test Docker Compose installed check (installed)."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.ok = True
        mock_conn.run.return_value = mock_result

        result = check_docker_compose_installed(mock_conn)

        assert result is True
        mock_conn.run.assert_called_once_with("docker-compose --version", hide=True)

    def test_docker_compose_not_installed(self):
        """Test Docker Compose installed check (not installed)."""
        mock_conn = MagicMock()
        mock_conn.run.side_effect = Exception("Command not found")

        result = check_docker_compose_installed(mock_conn)

        assert result is False


class TestGetContainerHealth:
    """Tests for get_container_health function."""

    def test_container_running_healthy(self):
        """Test health check for running healthy container."""
        mock_conn = MagicMock()

        # Mock responses for different docker inspect commands
        def mock_run(cmd, hide=False, warn=False):
            result = MagicMock()
            result.ok = True
            if "State.Running" in cmd:
                result.stdout = "true"
            elif "State.Health.Status" in cmd:
                result.stdout = "healthy"
            elif "State.StartedAt" in cmd:
                result.stdout = "2025-11-27T10:00:00Z"
            elif "RestartCount" in cmd:
                result.stdout = "0"
            return result

        mock_conn.run = mock_run

        health = get_container_health(mock_conn, "test-bot")

        assert health["running"] is True
        assert health["health_status"] == "healthy"
        assert health["uptime"] == "2025-11-27T10:00:00Z"
        assert health["restarts"] == 0

    def test_container_not_running(self):
        """Test health check for stopped container."""
        mock_conn = MagicMock()

        def mock_run(cmd, hide=False, warn=False):
            result = MagicMock()
            result.ok = True
            if "State.Running" in cmd:
                result.stdout = "false"
            elif "State.ExitCode" in cmd:
                result.stdout = "1"
            return result

        mock_conn.run = mock_run

        health = get_container_health(mock_conn, "test-bot")

        assert health["running"] is False
        assert health["exit_code"] == 1

    def test_container_unhealthy(self):
        """Test health check for unhealthy container."""
        mock_conn = MagicMock()

        def mock_run(cmd, hide=False, warn=False):
            result = MagicMock()
            result.ok = True
            if "State.Running" in cmd:
                result.stdout = "true"
            elif "State.Health.Status" in cmd:
                result.stdout = "unhealthy"
            elif "State.StartedAt" in cmd:
                result.stdout = "2025-11-27T10:00:00Z"
            elif "RestartCount" in cmd:
                result.stdout = "3"
            return result

        mock_conn.run = mock_run

        health = get_container_health(mock_conn, "test-bot")

        assert health["running"] is True
        assert health["health_status"] == "unhealthy"
        assert health["restarts"] == 3

    def test_container_starting(self):
        """Test health check for starting container."""
        mock_conn = MagicMock()

        def mock_run(cmd, hide=False, warn=False):
            result = MagicMock()
            result.ok = True
            if "State.Running" in cmd:
                result.stdout = "true"
            elif "State.Health.Status" in cmd:
                result.stdout = "starting"
            elif "State.StartedAt" in cmd:
                result.stdout = "2025-11-27T10:00:00Z"
            elif "RestartCount" in cmd:
                result.stdout = "0"
            return result

        mock_conn.run = mock_run

        health = get_container_health(mock_conn, "test-bot")

        assert health["running"] is True
        assert health["health_status"] == "starting"

    def test_container_not_found(self):
        """Test health check for non-existent container."""
        mock_conn = MagicMock()

        def mock_run(cmd, hide=False, warn=False):
            result = MagicMock()
            result.ok = False
            return result

        mock_conn.run = mock_run

        health = get_container_health(mock_conn, "nonexistent-bot")

        assert health["running"] is False
        assert health["health_status"] == "unknown"


class TestGetRecentErrors:
    """Tests for get_recent_errors function."""

    def test_get_errors_found(self):
        """Test getting recent errors when errors exist."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.ok = True
        mock_result.stdout = "ERROR: Connection failed\nERROR: Timeout\n"
        mock_conn.run.return_value = mock_result

        errors = get_recent_errors(mock_conn, "test-bot", lines=50)

        assert "ERROR: Connection failed" in errors
        assert "ERROR: Timeout" in errors

    def test_get_errors_none_found(self):
        """Test getting recent errors when no errors exist."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.ok = True
        mock_result.stdout = ""
        mock_conn.run.return_value = mock_result

        errors = get_recent_errors(mock_conn, "test-bot", lines=50)

        assert errors == ""

    def test_get_errors_command_failed(self):
        """Test getting recent errors when command fails."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.ok = False
        mock_conn.run.return_value = mock_result

        errors = get_recent_errors(mock_conn, "test-bot", lines=50)

        assert errors == ""

    def test_get_errors_exception(self):
        """Test getting recent errors when exception occurs."""
        mock_conn = MagicMock()
        mock_conn.run.side_effect = Exception("Connection error")

        errors = get_recent_errors(mock_conn, "test-bot", lines=50)

        assert errors == ""
