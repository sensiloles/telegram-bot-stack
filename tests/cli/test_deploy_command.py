"""Tests for deploy command."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from telegram_bot_stack.cli.commands.deploy import deploy
from telegram_bot_stack.cli.utils.deployment import DeploymentConfig


@pytest.fixture
def runner():
    """Create CLI runner."""
    return CliRunner()


@pytest.fixture
def temp_deploy_config(tmp_path):
    """Create temporary deployment config."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "deploy.yaml"
    config = DeploymentConfig(str(config_file))
    config.set("vps.host", "test.example.com")
    config.set("vps.user", "root")
    config.set("vps.ssh_key", "~/.ssh/id_rsa")
    config.set("vps.port", 22)
    config.set("bot.name", "test-bot")
    config.set("bot.token_env", "BOT_TOKEN")
    config.set("bot.entry_point", "bot.py")
    config.set("bot.python_version", "3.11")
    config.save()
    return config_file


class TestDeployInit:
    """Tests for deploy init command."""

    def test_init_with_options(self, runner, tmp_path):
        """Test init command with all options provided."""
        os.chdir(tmp_path)

        with patch(
            "telegram_bot_stack.cli.utils.vps.VPSConnection.test_connection",
            return_value=True,
        ):
            result = runner.invoke(
                deploy,
                [
                    "init",
                    "--host",
                    "test.example.com",
                    "--user",
                    "root",
                    "--ssh-key",
                    "~/.ssh/id_rsa",
                    "--bot-name",
                    "test-bot",
                ],
            )

            assert result.exit_code == 0
            assert "Configuration saved" in result.output
            assert Path("deploy.yaml").exists()

    def test_init_connection_failure(self, runner, tmp_path):
        """Test init command with connection failure."""
        os.chdir(tmp_path)

        with patch(
            "telegram_bot_stack.cli.utils.vps.VPSConnection.test_connection",
            return_value=False,
        ):
            result = runner.invoke(
                deploy,
                [
                    "init",
                    "--host",
                    "test.example.com",
                    "--user",
                    "root",
                    "--ssh-key",
                    "~/.ssh/id_rsa",
                    "--bot-name",
                    "test-bot",
                ],
            )

            assert result.exit_code == 0
            assert "SSH connection failed" in result.output
            assert not Path("deploy.yaml").exists()


class TestDeployUp:
    """Tests for deploy up command."""

    def test_up_without_config(self, runner, tmp_path):
        """Test up command without config file."""
        os.chdir(tmp_path)

        result = runner.invoke(deploy, ["up"])

        assert result.exit_code == 0
        assert "Configuration file not found" in result.output

    def test_up_with_valid_config(self, runner, tmp_path, temp_deploy_config):
        """Test up command with valid config."""
        os.chdir(tmp_path)

        # Copy config to current directory
        import shutil

        shutil.copy(temp_deploy_config, tmp_path / "deploy.yaml")

        # Create dummy bot files
        (tmp_path / "bot.py").write_text("# Bot file")
        (tmp_path / "requirements.txt").write_text("python-telegram-bot>=22.3")

        with (
            patch(
                "telegram_bot_stack.cli.commands.deploy.operations.VPSConnection"
            ) as mock_vps,
            patch(
                "telegram_bot_stack.cli.commands.deploy.operations.SecretsManager"
            ) as mock_secrets,
        ):
            # Mock VPS operations
            mock_instance = MagicMock()
            mock_instance.test_connection.return_value = True
            mock_instance.check_docker_installed.return_value = True
            mock_instance.run_command.return_value = True
            mock_instance.transfer_files.return_value = True
            mock_instance.write_file.return_value = True
            mock_vps.return_value = mock_instance

            # Mock SecretsManager
            mock_secrets_instance = MagicMock()
            mock_secrets_instance.list_secrets.return_value = {}
            mock_secrets.return_value = mock_secrets_instance

            result = runner.invoke(deploy, ["up"])

            assert result.exit_code == 0
            assert "Deployment successful" in result.output


class TestDeployStatus:
    """Tests for deploy status command."""

    def test_status_without_config(self, runner, tmp_path):
        """Test status command without config file."""
        os.chdir(tmp_path)

        result = runner.invoke(deploy, ["status"])

        assert result.exit_code == 0
        assert "Configuration file not found" in result.output

    def test_status_with_config(self, runner, tmp_path, temp_deploy_config):
        """Test status command with valid config."""
        os.chdir(tmp_path)

        # Copy config to current directory
        import shutil

        shutil.copy(temp_deploy_config, tmp_path / "deploy.yaml")

        with patch(
            "telegram_bot_stack.cli.commands.deploy.monitoring.VPSConnection"
        ) as mock_vps:
            mock_instance = MagicMock()
            mock_instance.run_command.return_value = True
            mock_vps.return_value = mock_instance

            result = runner.invoke(deploy, ["status"])

            assert result.exit_code == 0
            # Should call run_command for status checks
            assert mock_instance.run_command.called


class TestDeployLogs:
    """Tests for deploy logs command."""

    def test_logs_without_config(self, runner, tmp_path):
        """Test logs command without config file."""
        os.chdir(tmp_path)

        result = runner.invoke(deploy, ["logs"])

        assert result.exit_code == 0
        assert "Configuration file not found" in result.output

    def test_logs_with_config(self, runner, tmp_path, temp_deploy_config):
        """Test logs command with valid config."""
        os.chdir(tmp_path)

        # Copy config to current directory
        import shutil

        shutil.copy(temp_deploy_config, tmp_path / "deploy.yaml")

        with patch(
            "telegram_bot_stack.cli.commands.deploy.monitoring.VPSConnection"
        ) as mock_vps:
            mock_instance = MagicMock()
            mock_instance.run_command.return_value = True
            mock_vps.return_value = mock_instance

            result = runner.invoke(deploy, ["logs", "--tail", "20"])

            assert result.exit_code == 0
            assert mock_instance.run_command.called


class TestDeployDown:
    """Tests for deploy down command."""

    def test_down_without_config(self, runner, tmp_path):
        """Test down command without config file."""
        os.chdir(tmp_path)

        result = runner.invoke(deploy, ["down"])

        assert result.exit_code == 0
        assert "Configuration file not found" in result.output

    def test_down_with_config(self, runner, tmp_path, temp_deploy_config):
        """Test down command with valid config."""
        os.chdir(tmp_path)

        # Copy config to current directory
        import shutil

        shutil.copy(temp_deploy_config, tmp_path / "deploy.yaml")

        with patch(
            "telegram_bot_stack.cli.commands.deploy.operations.VPSConnection"
        ) as mock_vps:
            mock_instance = MagicMock()
            mock_instance.run_command.return_value = True
            mock_vps.return_value = mock_instance

            result = runner.invoke(deploy, ["down"])

            assert result.exit_code == 0
            assert "Bot stopped" in result.output

    def test_down_with_cleanup(self, runner, tmp_path, temp_deploy_config):
        """Test down command with cleanup flag."""
        os.chdir(tmp_path)

        # Copy config to current directory
        import shutil

        shutil.copy(temp_deploy_config, tmp_path / "deploy.yaml")

        with patch(
            "telegram_bot_stack.cli.commands.deploy.operations.VPSConnection"
        ) as mock_vps:
            mock_instance = MagicMock()
            mock_instance.run_command.return_value = True
            mock_vps.return_value = mock_instance

            result = runner.invoke(deploy, ["down", "--cleanup"])

            assert result.exit_code == 0
            assert "cleaned up" in result.output


class TestDeployUpdate:
    """Tests for deploy update command."""

    def test_update_without_config(self, runner, tmp_path):
        """Test update command without config file."""
        os.chdir(tmp_path)

        result = runner.invoke(deploy, ["update"])

        assert result.exit_code == 0
        assert "Configuration file not found" in result.output

    def test_update_with_config(self, runner, tmp_path, temp_deploy_config):
        """Test update command with valid config."""
        os.chdir(tmp_path)

        # Copy config to current directory
        import shutil

        shutil.copy(temp_deploy_config, tmp_path / "deploy.yaml")

        # Create dummy bot files
        (tmp_path / "bot.py").write_text("# Updated bot file")

        with patch(
            "telegram_bot_stack.cli.commands.deploy.operations.VPSConnection"
        ) as mock_vps:
            mock_instance = MagicMock()
            mock_instance.transfer_files.return_value = True
            mock_instance.run_command.return_value = True
            mock_vps.return_value = mock_instance

            result = runner.invoke(deploy, ["update"])

            assert result.exit_code == 0
            assert "Bot updated successfully" in result.output


class TestDeployRollback:
    """Tests for deploy rollback command."""

    def test_rollback_without_config(self, runner, tmp_path):
        """Test rollback command without config file."""
        os.chdir(tmp_path)

        result = runner.invoke(deploy, ["rollback"])

        assert result.exit_code == 0
        assert "Configuration file not found" in result.output

    def test_rollback_to_previous_version(self, runner, tmp_path, temp_deploy_config):
        """Test rollback to previous version."""
        os.chdir(tmp_path)

        # Copy config to current directory
        import shutil

        shutil.copy(temp_deploy_config, tmp_path / "deploy.yaml")

        with (
            patch(
                "telegram_bot_stack.cli.commands.deploy.operations.VPSConnection"
            ) as mock_vps,
            patch(
                "telegram_bot_stack.cli.commands.deploy.operations.VersionTracker"
            ) as mock_tracker,
            patch(
                "telegram_bot_stack.cli.commands.deploy.operations.BackupManager"
            ) as mock_backup,
        ):
            # Mock VPS connection
            mock_instance = MagicMock()
            mock_instance.test_connection.return_value = True
            mock_instance.run_command.return_value = True
            mock_vps.return_value = mock_instance

            # Mock version tracker
            mock_tracker_instance = MagicMock()
            mock_version = MagicMock()
            mock_version.docker_tag = "test-bot:v1234567890-abc123"
            mock_version.git_commit = "abc123"
            mock_version.deployed_at = "2025-01-26 14:30:00"
            mock_tracker_instance.get_previous_version.return_value = mock_version
            mock_tracker_instance.mark_version_status.return_value = True
            mock_tracker.return_value = mock_tracker_instance

            # Mock backup manager
            mock_backup_instance = MagicMock()
            mock_backup_instance.create_backup.return_value = "backup.tar.gz"
            mock_backup.return_value = mock_backup_instance

            result = runner.invoke(deploy, ["rollback", "--yes"])

            assert result.exit_code == 0
            assert "Rollback successful" in result.output

    def test_rollback_no_previous_version(self, runner, tmp_path, temp_deploy_config):
        """Test rollback when no previous version exists."""
        os.chdir(tmp_path)

        # Copy config to current directory
        import shutil

        shutil.copy(temp_deploy_config, tmp_path / "deploy.yaml")

        with (
            patch(
                "telegram_bot_stack.cli.commands.deploy.operations.VPSConnection"
            ) as mock_vps,
            patch(
                "telegram_bot_stack.cli.commands.deploy.operations.VersionTracker"
            ) as mock_tracker,
        ):
            mock_instance = MagicMock()
            mock_instance.test_connection.return_value = True
            mock_vps.return_value = mock_instance

            mock_tracker_instance = MagicMock()
            mock_tracker_instance.get_previous_version.return_value = None
            mock_tracker.return_value = mock_tracker_instance

            result = runner.invoke(deploy, ["rollback"])

            assert result.exit_code == 0
            assert "No previous version found" in result.output

    def test_rollback_to_specific_version(self, runner, tmp_path, temp_deploy_config):
        """Test rollback to specific version."""
        os.chdir(tmp_path)

        # Copy config to current directory
        import shutil

        shutil.copy(temp_deploy_config, tmp_path / "deploy.yaml")

        with (
            patch(
                "telegram_bot_stack.cli.commands.deploy.operations.VPSConnection"
            ) as mock_vps,
            patch(
                "telegram_bot_stack.cli.commands.deploy.operations.VersionTracker"
            ) as mock_tracker,
            patch(
                "telegram_bot_stack.cli.commands.deploy.operations.BackupManager"
            ) as mock_backup,
        ):
            mock_instance = MagicMock()
            mock_instance.test_connection.return_value = True
            mock_instance.run_command.return_value = True
            mock_vps.return_value = mock_instance

            mock_tracker_instance = MagicMock()
            mock_version = MagicMock()
            mock_version.docker_tag = "test-bot:v1234567880-def456"
            mock_version.git_commit = "def456"
            mock_version.deployed_at = "2025-01-26 14:20:00"
            mock_tracker_instance.get_version_by_tag.return_value = mock_version
            mock_tracker_instance.mark_version_status.return_value = True
            mock_tracker.return_value = mock_tracker_instance

            mock_backup_instance = MagicMock()
            mock_backup_instance.create_backup.return_value = "backup.tar.gz"
            mock_backup.return_value = mock_backup_instance

            result = runner.invoke(
                deploy,
                ["rollback", "--version", "test-bot:v1234567880-def456", "--yes"],
            )

            assert result.exit_code == 0
            assert "Rollback successful" in result.output


class TestDeployHistory:
    """Tests for deploy history command."""

    def test_history_without_config(self, runner, tmp_path):
        """Test history command without config file."""
        os.chdir(tmp_path)

        result = runner.invoke(deploy, ["history"])

        assert result.exit_code == 0
        assert "Configuration file not found" in result.output

    def test_history_empty(self, runner, tmp_path, temp_deploy_config):
        """Test history command with no deployments."""
        os.chdir(tmp_path)

        # Copy config to current directory
        import shutil

        shutil.copy(temp_deploy_config, tmp_path / "deploy.yaml")

        with (
            patch(
                "telegram_bot_stack.cli.commands.deploy.operations.VPSConnection"
            ) as mock_vps,
            patch(
                "telegram_bot_stack.cli.commands.deploy.operations.VersionTracker"
            ) as mock_tracker,
        ):
            mock_instance = MagicMock()
            mock_instance.test_connection.return_value = True
            mock_vps.return_value = mock_instance

            mock_tracker_instance = MagicMock()
            mock_tracker_instance.load_history.return_value = []
            mock_tracker.return_value = mock_tracker_instance

            result = runner.invoke(deploy, ["history"])

            assert result.exit_code == 0
            assert "No deployment history found" in result.output

    def test_history_with_versions(self, runner, tmp_path, temp_deploy_config):
        """Test history command with multiple versions."""
        os.chdir(tmp_path)

        # Copy config to current directory
        import shutil

        shutil.copy(temp_deploy_config, tmp_path / "deploy.yaml")

        with (
            patch(
                "telegram_bot_stack.cli.commands.deploy.operations.VPSConnection"
            ) as mock_vps,
            patch(
                "telegram_bot_stack.cli.commands.deploy.operations.VersionTracker"
            ) as mock_tracker,
        ):
            mock_instance = MagicMock()
            mock_instance.test_connection.return_value = True
            mock_vps.return_value = mock_instance

            # Mock versions
            from telegram_bot_stack.cli.utils.version_tracking import DeploymentVersion

            mock_versions = [
                DeploymentVersion(
                    timestamp="1234567890",
                    git_commit="abc123",
                    docker_tag="test-bot:v1234567890-abc123",
                    status="active",
                    deployed_at="2025-01-26 14:30:00",
                ),
                DeploymentVersion(
                    timestamp="1234567880",
                    git_commit="def456",
                    docker_tag="test-bot:v1234567880-def456",
                    status="old",
                    deployed_at="2025-01-26 14:20:00",
                ),
            ]

            mock_tracker_instance = MagicMock()
            mock_tracker_instance.load_history.return_value = mock_versions
            mock_tracker.return_value = mock_tracker_instance

            result = runner.invoke(deploy, ["history"])

            assert result.exit_code == 0
            assert "Deployment History" in result.output
            assert "abc123" in result.output
            assert "def456" in result.output
            assert "Active" in result.output

    def test_history_with_limit(self, runner, tmp_path, temp_deploy_config):
        """Test history command with limit."""
        os.chdir(tmp_path)

        # Copy config to current directory
        import shutil

        shutil.copy(temp_deploy_config, tmp_path / "deploy.yaml")

        with (
            patch(
                "telegram_bot_stack.cli.commands.deploy.operations.VPSConnection"
            ) as mock_vps,
            patch(
                "telegram_bot_stack.cli.commands.deploy.operations.VersionTracker"
            ) as mock_tracker,
        ):
            mock_instance = MagicMock()
            mock_instance.test_connection.return_value = True
            mock_vps.return_value = mock_instance

            from telegram_bot_stack.cli.utils.version_tracking import DeploymentVersion

            mock_versions = [
                DeploymentVersion(
                    timestamp=str(1234567890 - i),
                    git_commit=f"commit{i}",
                    docker_tag=f"test-bot:v{1234567890 - i}-commit{i}",
                    status="old",
                    deployed_at=f"2025-01-26 14:{30-i}:00",
                )
                for i in range(5)
            ]

            mock_tracker_instance = MagicMock()
            mock_tracker_instance.load_history.return_value = mock_versions
            mock_tracker.return_value = mock_tracker_instance

            result = runner.invoke(deploy, ["history", "--limit", "3"])

            assert result.exit_code == 0
            assert "Showing 3 of 5 versions" in result.output
