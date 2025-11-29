"""Tests for deployment state detection."""

from unittest.mock import MagicMock

import pytest

from telegram_bot_stack.cli.utils.deployment_state import (
    ContainerState,
    DeploymentStateDetector,
    ServiceState,
)


class MockResult:
    """Mock result from VPS command."""

    def __init__(self, stdout: str = "", success: bool = True):
        """Initialize mock result."""
        self.stdout = stdout
        self.success = success

    def __bool__(self) -> bool:
        """Return success status."""
        return self.success


class TestDeploymentStateDetector:
    """Tests for DeploymentStateDetector class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.vps = MagicMock()
        self.bot_name = "test-bot"
        self.remote_dir = "/opt/test-bot"
        self.detector = DeploymentStateDetector(
            self.vps, self.bot_name, self.remote_dir
        )

    def test_get_docker_state_not_deployed(self) -> None:
        """Test getting Docker state when container doesn't exist."""
        self.vps.run_command.return_value = MockResult("", success=False)

        state = self.detector.get_docker_state()

        assert isinstance(state, ContainerState)
        assert state.exists is False
        assert state.running is False
        assert state.status == "not deployed"

    def test_get_docker_state_running_healthy(self) -> None:
        """Test getting Docker state when container is running and healthy."""
        self.vps.run_command.return_value = MockResult(
            "Up 2 hours (healthy)|test-bot:latest"
        )

        state = self.detector.get_docker_state()

        assert state.exists is True
        assert state.running is True
        assert state.health == "healthy"
        assert "2 hours" in state.uptime
        assert state.image == "test-bot:latest"

    def test_get_docker_state_running_unhealthy(self) -> None:
        """Test getting Docker state when container is unhealthy."""
        self.vps.run_command.return_value = MockResult(
            "Up 1 hour (unhealthy)|test-bot:v1.0"
        )

        state = self.detector.get_docker_state()

        assert state.exists is True
        assert state.running is True
        assert state.health == "unhealthy"

    def test_get_docker_state_stopped(self) -> None:
        """Test getting Docker state when container is stopped."""
        self.vps.run_command.return_value = MockResult(
            "Exited (0) 5 minutes ago|test-bot:latest"
        )

        state = self.detector.get_docker_state()

        assert state.exists is True
        assert state.running is False
        assert state.health == "not running"

    def test_get_docker_state_starting(self) -> None:
        """Test getting Docker state when container is starting."""
        self.vps.run_command.return_value = MockResult(
            "Up 10 seconds (starting)|test-bot:latest"
        )

        state = self.detector.get_docker_state()

        assert state.exists is True
        assert state.running is True
        assert state.health == "starting"

    def test_get_docker_state_no_healthcheck(self) -> None:
        """Test getting Docker state when no healthcheck is configured."""
        self.vps.run_command.return_value = MockResult("Up 3 days|test-bot:latest")

        state = self.detector.get_docker_state()

        assert state.exists is True
        assert state.running is True
        assert state.health == "no healthcheck"

    def test_get_systemd_state_not_deployed(self) -> None:
        """Test getting systemd state when service doesn't exist."""
        self.vps.run_command.return_value = MockResult("", success=False)

        state = self.detector.get_systemd_state()

        assert isinstance(state, ServiceState)
        assert state.exists is False
        assert state.active is False
        assert state.status == "not deployed"

    def test_get_systemd_state_active(self) -> None:
        """Test getting systemd state when service is active."""
        # First call: list units (service exists)
        # Second call: is-active (returns "active")
        # Third call: status details
        self.vps.run_command.side_effect = [
            MockResult("test-bot.service loaded active running"),
            MockResult("active"),
            MockResult("● test-bot.service - Test Bot\n   Loaded: loaded"),
        ]

        state = self.detector.get_systemd_state()

        assert state.exists is True
        assert state.active is True

    def test_get_systemd_state_inactive(self) -> None:
        """Test getting systemd state when service is inactive."""
        self.vps.run_command.side_effect = [
            MockResult("test-bot.service loaded inactive dead"),
            MockResult("inactive"),
            MockResult("● test-bot.service - Test Bot\n   Loaded: loaded"),
        ]

        state = self.detector.get_systemd_state()

        assert state.exists is True
        assert state.active is False

    def test_detect_stale_containers_none(self) -> None:
        """Test detecting stale containers when none exist."""
        self.vps.run_command.return_value = MockResult("")

        stale = self.detector.detect_stale_containers()

        assert stale == []

    def test_detect_stale_containers_found(self) -> None:
        """Test detecting stale containers."""
        self.vps.run_command.return_value = MockResult(
            "test-bot\nother-bot-test-bot\ncompletely-different"
        )

        stale = self.detector.detect_stale_containers()

        # Should only include containers with bot_name in them
        assert len(stale) == 2
        assert "test-bot" in stale
        assert "other-bot-test-bot" in stale
        assert "completely-different" not in stale

    def test_cleanup_stale_containers(self) -> None:
        """Test cleaning up stale containers."""
        # Mock detect_stale_containers to return some containers
        self.vps.run_command.side_effect = [
            MockResult("test-bot-old\ntest-bot-stale"),  # detect_stale_containers
            MockResult("", success=True),  # docker rm test-bot-old
            MockResult("", success=True),  # docker rm test-bot-stale
        ]

        cleaned = self.detector.cleanup_stale_containers()

        assert cleaned == 2

    def test_cleanup_stale_containers_none(self) -> None:
        """Test cleanup when no stale containers exist."""
        self.vps.run_command.return_value = MockResult("")

        cleaned = self.detector.cleanup_stale_containers()

        assert cleaned == 0

    def test_check_before_deploy_not_running(self) -> None:
        """Test check before deploy when bot is not running."""
        self.vps.run_command.side_effect = [
            MockResult(""),  # cleanup_stale_containers: no stale
            MockResult("", success=False),  # get_docker_state: not deployed
        ]

        result = self.detector.check_before_deploy("docker", force=False)

        assert result is True

    def test_check_before_deploy_already_running_user_cancels(self) -> None:
        """Test check before deploy when bot is running and user cancels."""
        pytest.importorskip("rich.prompt")
        from unittest.mock import patch

        # Mock cleanup_stale_containers to avoid side effects
        with patch.object(self.detector, "cleanup_stale_containers", return_value=0):
            self.vps.run_command.return_value = MockResult(
                "Up 1 hour (healthy)|test-bot:latest"
            )  # get_docker_state

            # Mock user canceling confirmation
            with patch("rich.prompt.Confirm.ask", return_value=False):
                result = self.detector.check_before_deploy("docker", force=False)

        assert result is False

    def test_check_before_deploy_already_running_user_confirms(self) -> None:
        """Test check before deploy when bot is running and user confirms."""
        pytest.importorskip("rich.prompt")
        from unittest.mock import patch

        self.vps.run_command.side_effect = [
            MockResult(""),  # cleanup_stale_containers
            MockResult("Up 1 hour (healthy)|test-bot:latest"),  # get_docker_state
            MockResult("", success=True),  # make down
            MockResult("", success=True),  # docker rm
        ]

        # Mock user confirming
        with patch("rich.prompt.Confirm.ask", return_value=True):
            result = self.detector.check_before_deploy("docker", force=False)

        assert result is True

    def test_check_before_deploy_force_mode(self) -> None:
        """Test check before deploy with force mode."""
        # Important: Mock get_docker_state directly to avoid cleanup logic
        from unittest.mock import patch

        mock_state = ContainerState(
            exists=True,
            running=True,
            status="Up 1 hour (healthy)",
            uptime="1 hour",
            health="healthy",
            name="test-bot",
            image="test-bot:latest",
        )

        with patch.object(self.detector, "get_docker_state", return_value=mock_state):
            with patch.object(
                self.detector, "cleanup_stale_containers", return_value=0
            ):
                self.vps.run_command.side_effect = [
                    MockResult("", success=True),  # make down
                    MockResult("", success=True),  # docker rm
                ]

                result = self.detector.check_before_deploy("docker", force=True)

                # Should not ask for confirmation in force mode
                assert result is True
                # Should call make down and docker rm
                assert self.vps.run_command.call_count == 2

    def test_check_before_deploy_stopped_container(self) -> None:
        """Test check before deploy when container is stopped."""
        self.vps.run_command.side_effect = [
            MockResult(""),  # cleanup_stale_containers
            MockResult("Exited (0) 1 hour ago|test-bot:latest"),  # get_docker_state
            MockResult("", success=True),  # docker rm
        ]

        result = self.detector.check_before_deploy("docker", force=False)

        # Should automatically clean up stopped container
        assert result is True

    def test_check_before_deploy_systemd_running(self) -> None:
        """Test check before deploy for systemd when service is running."""
        pytest.importorskip("rich.prompt")
        from unittest.mock import patch

        # Mock systemd state
        self.vps.run_command.side_effect = [
            MockResult("test-bot.service loaded active running"),  # list units
            MockResult("active"),  # is-active
            MockResult("● test-bot.service"),  # status
        ]

        # Mock user canceling
        with patch("rich.prompt.Confirm.ask", return_value=False):
            result = self.detector.check_before_deploy("systemd", force=False)

        assert result is False

    def test_check_before_deploy_systemd_force(self) -> None:
        """Test check before deploy for systemd with force mode."""
        self.vps.run_command.side_effect = [
            MockResult("test-bot.service loaded active running"),  # list units
            MockResult("active"),  # is-active
            MockResult("● test-bot.service"),  # status
            MockResult("", success=True),  # systemctl stop
        ]

        result = self.detector.check_before_deploy("systemd", force=True)

        assert result is True

    def test_format_health(self) -> None:
        """Test health status formatting."""
        assert "✅" in self.detector._format_health("healthy")
        assert "❌" in self.detector._format_health("unhealthy")
        assert "🔄" in self.detector._format_health("starting")
        assert "⚠️" in self.detector._format_health("no healthcheck")
        assert "🛑" in self.detector._format_health("not running")
        assert "❓" in self.detector._format_health("unknown")


class TestContainerState:
    """Tests for ContainerState dataclass."""

    def test_create_container_state(self) -> None:
        """Test creating ContainerState."""
        state = ContainerState(
            exists=True,
            running=True,
            status="Up 1 hour (healthy)",
            uptime="1 hour",
            health="healthy",
            name="test-bot",
            image="test-bot:latest",
        )

        assert state.exists is True
        assert state.running is True
        assert state.health == "healthy"


class TestServiceState:
    """Tests for ServiceState dataclass."""

    def test_create_service_state(self) -> None:
        """Test creating ServiceState."""
        state = ServiceState(
            exists=True, active=True, status="active (running)", uptime="1 hour"
        )

        assert state.exists is True
        assert state.active is True
        assert "active" in state.status
