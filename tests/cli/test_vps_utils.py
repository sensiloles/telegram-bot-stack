"""Tests for VPS utilities."""

from unittest.mock import MagicMock, patch

from telegram_bot_stack.cli.utils.vps import (
    VPSConnection,
    check_docker_compose_installed,
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

        with patch.object(vps, "run_command") as mock_run:
            mock_run.return_value = True

            result = vps.install_docker()

            assert result is True
            # Should call multiple commands
            assert mock_run.call_count > 5

    def test_install_docker_failure(self):
        """Test failed Docker installation."""
        vps = VPSConnection(host="test.example.com", user="root")

        with patch.object(vps, "run_command") as mock_run:
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
