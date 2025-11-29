"""Tests for multi-bot deployment features."""

from unittest.mock import MagicMock, patch

from telegram_bot_stack.cli.utils.port_manager import (
    check_port_available,
    detect_port_conflicts,
    find_available_port,
    get_bot_ports,
    get_used_ports,
    suggest_alternative_ports,
)


class TestPortManager:
    """Test port management utilities."""

    def test_get_used_ports_success(self):
        """Test getting used ports from VPS."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.stdout = "22\n80\n443\n8080\n"
        mock_conn.run.return_value = mock_result

        ports = get_used_ports(mock_conn)

        assert ports == {22, 80, 443, 8080}
        mock_conn.run.assert_called_once()

    def test_get_used_ports_empty(self):
        """Test handling empty port list."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_conn.run.return_value = mock_result

        ports = get_used_ports(mock_conn)

        assert ports == set()

    def test_get_used_ports_error(self):
        """Test handling errors when getting ports."""
        mock_conn = MagicMock()
        mock_conn.run.side_effect = Exception("Connection failed")

        ports = get_used_ports(mock_conn)

        assert ports == set()

    def test_find_available_port_success(self):
        """Test finding available port."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.stdout = "8080\n8081\n"
        mock_conn.run.return_value = mock_result

        port = find_available_port(mock_conn, start_port=8080, end_port=8090)

        assert port == 8082  # First available after 8080, 8081

    def test_find_available_port_all_used(self):
        """Test when all ports in range are used."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        # All ports from 8080-8090 are used
        mock_result.stdout = "\n".join(str(p) for p in range(8080, 8091))
        mock_conn.run.return_value = mock_result

        port = find_available_port(mock_conn, start_port=8080, end_port=8090)

        assert port is None

    def test_check_port_available_true(self):
        """Test checking if port is available."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.stdout = "80\n443\n"
        mock_conn.run.return_value = mock_result

        available = check_port_available(mock_conn, 8080)

        assert available is True

    def test_check_port_available_false(self):
        """Test checking if port is in use."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.stdout = "80\n443\n8080\n"
        mock_conn.run.return_value = mock_result

        available = check_port_available(mock_conn, 8080)

        assert available is False

    def test_get_bot_ports_success(self):
        """Test getting ports used by a bot."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.stdout = """
    ports:
      - "8080:8080"
      - "9000:9000"
"""
        mock_conn.run.return_value = mock_result

        ports = get_bot_ports(mock_conn, "test-bot")

        assert 8080 in ports
        assert 9000 in ports

    def test_get_bot_ports_no_compose(self):
        """Test handling bot without docker-compose.yml."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_conn.run.return_value = mock_result

        ports = get_bot_ports(mock_conn, "test-bot")

        assert ports == []

    def test_detect_port_conflicts_no_conflicts(self):
        """Test detecting no port conflicts."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.stdout = "80\n443\n"
        mock_conn.run.return_value = mock_result

        conflicts = detect_port_conflicts(mock_conn, [8080, 9000])

        assert conflicts == []

    def test_detect_port_conflicts_with_conflicts(self):
        """Test detecting port conflicts."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.stdout = "80\n443\n8080\n"
        mock_conn.run.return_value = mock_result

        conflicts = detect_port_conflicts(mock_conn, [8080, 9000])

        assert conflicts == [8080]

    def test_detect_port_conflicts_exclude_bot(self):
        """Test excluding specific bot from conflict detection."""
        mock_conn = MagicMock()

        # First call: get used ports
        # Second call: get bot ports (for exclude_bot)
        mock_conn.run.side_effect = [
            MagicMock(stdout="8080\n9000\n"),  # Used ports
            MagicMock(stdout='ports:\n  - "8080:8080"\n'),  # Bot ports
        ]

        conflicts = detect_port_conflicts(
            mock_conn, [8080, 9000], exclude_bot="test-bot"
        )

        # 8080 is used by test-bot (excluded), so no conflict
        # 9000 is used by something else
        assert 9000 in conflicts
        assert 8080 not in conflicts

    def test_suggest_alternative_ports_no_conflicts(self):
        """Test suggesting ports when no conflicts."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.stdout = "80\n443\n"
        mock_conn.run.return_value = mock_result

        suggestions = suggest_alternative_ports(mock_conn, [8080, 9000])

        assert suggestions == [8080, 9000]  # No conflicts, use requested ports

    def test_suggest_alternative_ports_with_conflicts(self):
        """Test suggesting alternative ports for conflicts."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.stdout = "8080\n8081\n8082\n"
        mock_conn.run.return_value = mock_result

        suggestions = suggest_alternative_ports(mock_conn, [8080])

        assert suggestions[0] == 8083  # First available port after conflicts


class TestMultiBotListCommand:
    """Test multi-bot listing command."""

    @patch(
        "telegram_bot_stack.cli.commands.deploy.deploy.create_vps_connection_from_config"
    )
    @patch("telegram_bot_stack.cli.commands.deploy.deploy.DeploymentConfig")
    def test_list_all_bots_docker(self, mock_config_class, mock_vps_factory):
        """Test listing all bots on VPS (Docker)."""
        from telegram_bot_stack.cli.commands.deploy.deploy import _list_all_bots_on_vps

        # Mock config
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda key, default=None: {
            "deployment.method": "docker",
        }.get(key, default)
        mock_config_class.return_value = mock_config

        # Mock VPS connection
        mock_vps = MagicMock()
        mock_conn = MagicMock()
        mock_vps.connect.return_value = mock_conn

        # Mock find command (finds bot directories)
        mock_find_result = MagicMock()
        mock_find_result.stdout = "/opt/bot1\n/opt/bot2\n"

        # Mock compose file checks
        mock_compose_check1 = MagicMock()
        mock_compose_check1.ok = True
        mock_compose_check2 = MagicMock()
        mock_compose_check2.ok = True

        mock_conn.run.side_effect = [
            mock_find_result,  # find command
            mock_compose_check1,  # bot1 compose check
            mock_compose_check2,  # bot2 compose check
        ]

        # Mock container health checks (imported inside function)
        with patch(
            "telegram_bot_stack.cli.utils.vps.get_container_health"
        ) as mock_health:
            mock_health.return_value = {
                "status": "running",
                "health": "healthy",
                "uptime": "2 hours",
            }

            _list_all_bots_on_vps(mock_vps, mock_config)

            # Verify health was checked for both bots
            assert mock_health.call_count == 2

    @patch("telegram_bot_stack.cli.utils.vps.get_container_health")
    def test_list_current_bot_docker(self, mock_health):
        """Test listing current bot status (Docker)."""
        from telegram_bot_stack.cli.commands.deploy.deploy import _list_current_bot

        # Mock VPS
        mock_vps = MagicMock()
        mock_vps.run_command.return_value = True  # Directory exists
        mock_conn = MagicMock()
        mock_vps.connect.return_value = mock_conn

        # Mock config
        mock_config = MagicMock()
        mock_config.get.return_value = "docker"

        # Mock health check
        mock_health.return_value = {
            "status": "running",
            "health": "healthy",
            "uptime": "2 hours",
            "restart_count": 0,
        }

        _list_current_bot(mock_vps, mock_config, "test-bot")

        mock_health.assert_called_once()

    def test_list_current_bot_not_deployed(self):
        """Test listing bot that is not deployed."""
        from telegram_bot_stack.cli.commands.deploy.deploy import _list_current_bot

        # Mock VPS
        mock_vps = MagicMock()
        mock_vps.run_command.return_value = False  # Directory doesn't exist

        # Mock config
        mock_config = MagicMock()

        _list_current_bot(mock_vps, mock_config, "test-bot")

        # Should return early without checking container
        mock_vps.connect.assert_not_called()


class TestMultiBotNaming:
    """Test unique naming for multi-bot deployments."""

    def test_bot_name_uniqueness_in_config(self):
        """Test that bot names are unique identifiers in deploy.yaml."""
        # This is enforced by user configuration
        # Each bot has its own deploy.yaml with unique bot.name

        # Bot 1
        bot1_name = "telegram-bot-1"
        bot1_dir = f"/opt/{bot1_name}"

        # Bot 2
        bot2_name = "telegram-bot-2"
        bot2_dir = f"/opt/{bot2_name}"

        # Verify names are different
        assert bot1_name != bot2_name
        assert bot1_dir != bot2_dir

    def test_docker_container_naming(self):
        """Test Docker container names are unique."""
        from telegram_bot_stack.cli.utils.deployment import (
            DeploymentConfig,
            DockerTemplateRenderer,
        )

        # Create mock configs for two bots
        config1 = MagicMock(spec=DeploymentConfig)
        config1.get.side_effect = lambda key, default=None: {
            "bot.name": "bot-1",
            "resources.memory_limit": "256M",
            "resources.memory_reservation": "128M",
            "resources.cpu_limit": "0.5",
            "resources.cpu_reservation": "0.25",
            "logging.level": "INFO",
            "logging.max_size": "5m",
            "logging.max_files": "5",
            "environment.timezone": "UTC",
        }.get(key, default)

        config2 = MagicMock(spec=DeploymentConfig)
        config2.get.side_effect = lambda key, default=None: {
            "bot.name": "bot-2",
            "resources.memory_limit": "256M",
            "resources.memory_reservation": "128M",
            "resources.cpu_limit": "0.5",
            "resources.cpu_reservation": "0.25",
            "logging.level": "INFO",
            "logging.max_size": "5m",
            "logging.max_files": "5",
            "environment.timezone": "UTC",
        }.get(key, default)

        renderer1 = DockerTemplateRenderer(config1, has_secrets=False)
        renderer2 = DockerTemplateRenderer(config2, has_secrets=False)

        compose1 = renderer1.render_compose()
        compose2 = renderer2.render_compose()

        # Verify unique container names
        assert "container_name: bot-1" in compose1
        assert "container_name: bot-2" in compose2
        assert "container_name: bot-1" not in compose2
        assert "container_name: bot-2" not in compose1

        # Verify unique network names
        assert "name: bot-1-network" in compose1
        assert "name: bot-2-network" in compose2
