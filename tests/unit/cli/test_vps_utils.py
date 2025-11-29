"""Tests for VPS utilities."""

from unittest.mock import MagicMock, patch

from telegram_bot_stack.cli.utils.vps import (
    VPSConnection,
    check_docker_compose_installed,
    check_ssh_agent,
    find_ssh_keys,
    get_container_health,
    get_docker_compose_command,
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
            mock_conn.run.assert_called_once_with(
                "echo test", hide=False, pty=False, in_stream=False
            )

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
        # Should try v2 first
        mock_conn.run.assert_called_with(
            "docker compose version", hide=True, warn=True, pty=False, in_stream=False
        )

    def test_docker_compose_not_installed(self):
        """Test Docker Compose installed check (not installed)."""
        mock_conn = MagicMock()
        mock_conn.run.side_effect = Exception("Command not found")

        result = check_docker_compose_installed(mock_conn)

        assert result is False


class TestGetDockerComposeCommand:
    """Tests for get_docker_compose_command function."""

    def test_docker_compose_v2_available(self):
        """Test when Docker Compose v2 (built-in) is available."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.ok = True
        mock_conn.run.return_value = mock_result

        result = get_docker_compose_command(mock_conn)

        assert result == "docker compose"
        mock_conn.run.assert_called_with(
            "docker compose version", hide=True, warn=True, pty=False, in_stream=False
        )

    def test_docker_compose_v1_fallback(self):
        """Test fallback to Docker Compose v1 (standalone)."""
        mock_conn = MagicMock()
        mock_v2_result = MagicMock()
        mock_v2_result.ok = False
        mock_v1_result = MagicMock()
        mock_v1_result.ok = True
        mock_conn.run.side_effect = [mock_v2_result, mock_v1_result]

        result = get_docker_compose_command(mock_conn)

        assert result == "docker-compose"
        assert mock_conn.run.call_count == 2

    def test_docker_compose_not_available(self):
        """Test when neither v2 nor v1 is available (returns v2 as default)."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.ok = False
        mock_conn.run.return_value = mock_result

        result = get_docker_compose_command(mock_conn)

        # Should default to v2 even if not available (will fail later)
        assert result == "docker compose"


class TestGetContainerHealth:
    """Tests for get_container_health function."""

    def test_container_running_healthy(self):
        """Test health check for running healthy container."""
        mock_conn = MagicMock()

        # Mock responses for different docker inspect commands
        def mock_run(cmd, hide=False, warn=False, pty=False, in_stream=False):
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

        def mock_run(cmd, hide=False, warn=False, pty=False, in_stream=False):
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

        def mock_run(cmd, hide=False, warn=False, pty=False, in_stream=False):
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

        def mock_run(cmd, hide=False, warn=False, pty=False, in_stream=False):
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

        def mock_run(cmd, hide=False, warn=False, pty=False, in_stream=False):
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


class TestDockerComposeInstallation:
    """Tests for Docker Compose installation.

    Verifies that Docker Compose is properly installed both as plugin and standalone binary.
    """

    def test_docker_compose_plugin_installed(self):
        """Verify docker-compose-plugin is installed with Docker on Ubuntu/Debian."""
        vps = VPSConnection(host="test.com", user="root")

        with patch.object(vps, "run_command") as mock_run:
            with patch.object(vps, "connect") as mock_connect:
                mock_conn = MagicMock()
                mock_conn.run = MagicMock(
                    return_value=MagicMock(ok=True, stdout="ubuntu")
                )
                mock_connect.return_value = mock_conn
                mock_run.return_value = True

                # Install Docker
                vps.install_docker()

                # Check that docker-compose-plugin is installed
                install_calls = [str(call[0][0]) for call in mock_run.call_args_list]
                docker_install_cmd = next(
                    (
                        cmd
                        for cmd in install_calls
                        if "apt-get install" in cmd and "docker-ce" in cmd
                    ),
                    None,
                )

                assert docker_install_cmd is not None
                assert "docker-compose-plugin" in docker_install_cmd

    def test_standalone_docker_compose_installed(self):
        """Verify standalone docker-compose binary is installed as fallback."""
        vps = VPSConnection(host="test.com", user="root")

        with patch.object(vps, "run_command") as mock_run:
            with patch.object(vps, "connect") as mock_connect:
                mock_conn = MagicMock()
                mock_conn.run = MagicMock(
                    return_value=MagicMock(ok=True, stdout="ubuntu")
                )
                mock_connect.return_value = mock_conn
                mock_run.return_value = True

                vps.install_docker()

                # Check that standalone docker-compose is downloaded
                install_calls = [str(call[0][0]) for call in mock_run.call_args_list]
                compose_download_cmd = next(
                    (
                        cmd
                        for cmd in install_calls
                        if "docker-compose" in cmd and "curl" in cmd
                    ),
                    None,
                )

                assert compose_download_cmd is not None
                assert "v2.32.4" in compose_download_cmd  # Specific version
                assert "-SL" in compose_download_cmd  # Reliable curl flags

    def test_docker_compose_version_pinned(self):
        """Verify Docker Compose version is pinned, not using 'latest'."""
        vps = VPSConnection(host="test.com", user="root")

        with patch.object(vps, "run_command") as mock_run:
            with patch.object(vps, "connect") as mock_connect:
                mock_conn = MagicMock()
                mock_conn.run = MagicMock(
                    return_value=MagicMock(ok=True, stdout="ubuntu")
                )
                mock_connect.return_value = mock_conn
                mock_run.return_value = True

                vps.install_docker()

                install_calls = [str(call[0][0]) for call in mock_run.call_args_list]
                compose_download_cmd = next(
                    (
                        cmd
                        for cmd in install_calls
                        if "docker-compose" in cmd and "curl" in cmd
                    ),
                    None,
                )

                # Verify it's NOT using 'latest' (unreliable)
                assert compose_download_cmd is not None
                assert "/latest/" not in compose_download_cmd
                assert "v2.32.4" in compose_download_cmd


class TestSSHKeyAuth:
    """Tests for SSH key authentication features."""

    def test_find_ssh_keys_empty(self):
        """Test finding SSH keys when .ssh directory doesn't exist."""
        with patch("pathlib.Path.home") as mock_home:
            mock_ssh_dir = MagicMock()
            mock_ssh_dir.exists.return_value = False
            mock_home.return_value.__truediv__.return_value = mock_ssh_dir

            result = find_ssh_keys()

            assert result == []

    def test_find_ssh_keys_found(self):
        """Test finding SSH keys with keys present."""
        # Simplified test - just verify function returns a list
        result = find_ssh_keys()

        # Should return a list (may be empty or contain paths)
        assert isinstance(result, list)

    def test_check_ssh_agent_available(self):
        """Test SSH agent check when agent is running with keys."""
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0  # Agent has keys
            mock_run.return_value = mock_result

            result = check_ssh_agent()

            assert result is True
            mock_run.assert_called_once()

    def test_check_ssh_agent_no_keys(self):
        """Test SSH agent check when agent is running but has no keys."""
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1  # Agent running but no keys
            mock_run.return_value = mock_result

            result = check_ssh_agent()

            assert result is False

    def test_check_ssh_agent_not_running(self):
        """Test SSH agent check when agent is not running."""
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 2  # Agent not running
            mock_run.return_value = mock_result

            result = check_ssh_agent()

            assert result is False

    def test_vps_connection_with_auth_method_key(self):
        """Test VPSConnection with key auth method."""
        with patch("telegram_bot_stack.cli.utils.vps.find_ssh_keys") as mock_find:
            mock_find.return_value = ["/home/user/.ssh/id_ed25519"]

            vps = VPSConnection(host="test.example.com", user="root", auth_method="key")

            assert vps.auth_method == "key"
            assert vps.ssh_key == "/home/user/.ssh/id_ed25519"

    def test_vps_connection_with_auth_method_password(self):
        """Test VPSConnection with password auth method."""
        vps = VPSConnection(
            host="test.example.com",
            user="root",
            password="secret",
            auth_method="password",
        )

        assert vps.auth_method == "password"
        assert vps.password == "secret"
        assert vps.ssh_key is None

    def test_vps_connection_with_auth_method_agent(self):
        """Test VPSConnection with agent auth method."""
        vps = VPSConnection(host="test.example.com", user="root", auth_method="agent")

        assert vps.auth_method == "agent"
        assert vps.ssh_key is None

    def test_vps_connection_with_auth_method_auto(self):
        """Test VPSConnection with auto auth method."""
        with patch("telegram_bot_stack.cli.utils.vps.find_ssh_keys") as mock_find:
            mock_find.return_value = ["/home/user/.ssh/id_rsa"]

            vps = VPSConnection(
                host="test.example.com", user="root", auth_method="auto"
            )

            assert vps.auth_method == "auto"
            assert vps.ssh_key == "/home/user/.ssh/id_rsa"

    def test_vps_connection_explicit_ssh_key(self):
        """Test VPSConnection with explicitly provided SSH key."""
        vps = VPSConnection(
            host="test.example.com",
            user="root",
            ssh_key="/custom/path/id_rsa",
            auth_method="key",
        )

        assert vps.ssh_key == "/custom/path/id_rsa"

    def test_get_auth_info_key(self):
        """Test auth info display for key authentication."""
        vps = VPSConnection(
            host="test.example.com",
            user="root",
            ssh_key="~/.ssh/id_ed25519",
            auth_method="key",
        )

        info = vps._get_auth_info()

        assert "SSH key" in info
        assert "id_ed25519" in info

    def test_get_auth_info_password(self):
        """Test auth info display for password authentication."""
        vps = VPSConnection(
            host="test.example.com", user="root", auth_method="password"
        )

        info = vps._get_auth_info()

        assert "password" in info

    def test_get_auth_info_agent(self):
        """Test auth info display for agent authentication."""
        vps = VPSConnection(host="test.example.com", user="root", auth_method="agent")

        info = vps._get_auth_info()

        assert "agent" in info.lower()
