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

        with patch("telegram_bot_stack.cli.utils.vps.VPSConnection") as mock_vps:
            # Mock successful connection test
            mock_vps.return_value.test_connection.return_value = True

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

        with patch("telegram_bot_stack.cli.utils.vps.VPSConnection") as mock_vps:
            # Mock failed connection test
            mock_vps.return_value.test_connection.return_value = False

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
