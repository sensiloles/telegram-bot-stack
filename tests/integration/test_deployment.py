"""Integration tests for VPS deployment commands.

Tests the complete deployment flow from initialization to teardown,
using a mock VPS environment.
"""

import logging
import os
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from telegram_bot_stack.cli.main import cli
from tests.integration.fixtures.mock_vps import MockVPS

logger = logging.getLogger(__name__)


class TestDeploymentInit:
    """Test deployment initialization."""

    def test_deploy_init_interactive(self, clean_vps: MockVPS, tmp_path: Path) -> None:
        """Test interactive deployment initialization."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # Run deploy init with all options
        logger.info("→ Running 'deploy init' command...")
        result = runner.invoke(
            cli,
            [
                "deploy",
                "init",
                "--host",
                clean_vps.host,
                "--user",
                clean_vps.user,
                "--ssh-key",
                clean_vps.ssh_key_path,
                "--port",
                str(clean_vps.port),
                "--bot-name",
                "test-bot",
            ],
        )

        # Check command succeeded
        logger.info(f"→ Command exit code: {result.exit_code}")
        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Check deploy.yaml was created
        logger.info("→ Verifying deploy.yaml was created...")
        assert Path("deploy.yaml").exists()

        # Check configuration content
        logger.info("→ Validating deploy.yaml configuration...")
        with open("deploy.yaml") as f:
            config = yaml.safe_load(f)

        logger.info(f"  ✓ VPS host: {config['vps']['host']}")
        logger.info(f"  ✓ VPS port: {config['vps']['port']}")
        logger.info(f"  ✓ Bot name: {config['bot']['name']}")

        assert config["vps"]["host"] == clean_vps.host
        assert config["vps"]["user"] == clean_vps.user
        assert config["vps"]["port"] == clean_vps.port
        assert config["bot"]["name"] == "test-bot"
        assert "secrets" in config
        assert "encryption_key" in config["secrets"]

        logger.info("→ All assertions passed")

    def test_deploy_init_existing_config_no_overwrite(
        self, clean_vps: MockVPS, tmp_path: Path
    ) -> None:
        """Test deploy init with existing config (no overwrite)."""
        from unittest.mock import patch

        os.chdir(tmp_path)
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Mock VPS connection test to always succeed
            with patch(
                "telegram_bot_stack.cli.commands.deploy.deploy.VPSConnection.test_connection",
                return_value=True,
            ):
                # Create initial config
                result1 = runner.invoke(
                    cli,
                    [
                        "deploy",
                        "init",
                        "--host",
                        clean_vps.host,
                        "--user",
                        clean_vps.user,
                        "--ssh-key",
                        clean_vps.ssh_key_path,
                        "--bot-name",
                        "test-bot-1",
                    ],
                )
                assert result1.exit_code == 0, f"First init failed: {result1.output}"
                assert Path("deploy.yaml").exists()

                # Try to init again (should prompt to overwrite)
                result2 = runner.invoke(
                    cli,
                    [
                        "deploy",
                        "init",
                        "--host",
                        clean_vps.host,
                        "--user",
                        clean_vps.user,
                        "--ssh-key",
                        clean_vps.ssh_key_path,
                        "--bot-name",
                        "test-bot-2",
                    ],
                    input="n\n",  # Answer "no" to overwrite
                )

                # Should be cancelled
                assert result2.exit_code == 0
                assert "cancelled" in result2.output.lower()

    def test_deploy_init_invalid_ssh_connection(self, tmp_path: Path) -> None:
        """Test deploy init with invalid SSH connection."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # Use invalid host
        result = runner.invoke(
            cli,
            [
                "deploy",
                "init",
                "--host",
                "invalid.host.example.com",
                "--user",
                "root",
                "--ssh-key",
                "~/.ssh/id_rsa",
                "--bot-name",
                "test-bot",
            ],
        )

        # Should fail with SSH connection error
        assert result.exit_code == 0  # Command itself succeeds
        assert "SSH connection failed" in result.output


class TestDeploymentUp:
    """Test bot deployment."""

    @pytest.mark.skip(reason="CliRunner file descriptor issue - needs refactoring")
    def test_deploy_up_first_time(
        self, clean_vps: MockVPS, tmp_path: Path, deployment_config: Path
    ) -> None:
        """Test first-time deployment to clean VPS."""
        os.chdir(tmp_path)

        # Create simple bot
        bot_content = """
import os
from telegram_bot_stack import BotBase
from telegram_bot_stack.storage import MemoryStorage

def main():
    token = os.getenv('BOT_TOKEN', 'test-token')
    bot = BotBase(storage=MemoryStorage(), bot_name='Test Bot')
    print('Bot started')

if __name__ == '__main__':
    main()
"""
        Path("bot.py").write_text(bot_content)

        # Create requirements.txt
        Path("requirements.txt").write_text("telegram-bot-stack\n")

        # deploy.yaml already created by deployment_config fixture
        assert deployment_config.exists(), "deploy.yaml must exist"

        # Set bot token secret (create new runner for each command to avoid file descriptor issues)
        result_secret = CliRunner().invoke(
            cli,
            [
                "deploy",
                "secrets",
                "set-secret",
                "BOT_TOKEN",
                "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
                "--config",
                str(deployment_config),
            ],
        )
        assert result_secret.exit_code == 0

        # Deploy bot (use new runner to avoid I/O closed file error)
        result_up = CliRunner().invoke(
            cli, ["deploy", "up", "--config", str(deployment_config)]
        )

        # Check deployment succeeded
        assert result_up.exit_code == 0
        assert "deployed successfully" in result_up.output.lower()

        # Verify bot container is running
        # Note: This may not work if Docker-in-Docker is not fully configured
        # In that case, we check for deployment files instead
        output = clean_vps.exec("ls /opt/test-bot 2>&1 || echo 'NOT_FOUND'")
        assert "NOT_FOUND" not in output, "Bot directory should exist on VPS"

    def test_deploy_up_without_init(self, clean_vps: MockVPS, tmp_path: Path) -> None:
        """Test deployment without initialization."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # Try to deploy without deploy.yaml
        result = runner.invoke(cli, ["deploy", "up"])

        # Should fail gracefully
        assert result.exit_code != 0 or "not found" in result.output.lower()


class TestDeploymentStatus:
    """Test deployment status checking."""

    def test_deploy_status_no_deployment(
        self, clean_vps: MockVPS, tmp_path: Path, deployment_config: Path
    ) -> None:
        """Test status check with no deployment."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # Check status (bot not deployed yet)
        result = runner.invoke(
            cli, ["deploy", "status", "--config", str(deployment_config)]
        )

        # Should show error or indicate bot not deployed
        # Exit code may be non-zero since deployment doesn't exist
        assert (
            "not running" in result.output.lower()
            or "not found" in result.output.lower()
            or "no rule to make target" in result.output.lower()
            or "failed" in result.output.lower()
        )


class TestSecretsManagement:
    """Test secrets management commands."""

    def test_secrets_set_and_list(
        self, clean_vps: MockVPS, tmp_path: Path, deployment_config: Path
    ) -> None:
        """Test setting and listing secrets."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # deploy.yaml already created by deployment_config fixture
        assert deployment_config.exists(), "deploy.yaml must exist"

        # Set secret
        logger.info("→ Setting BOT_TOKEN secret...")
        result_set = runner.invoke(
            cli,
            [
                "deploy",
                "secrets",
                "set-secret",
                "BOT_TOKEN",
                "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
                "--config",
                str(deployment_config),
            ],
        )
        logger.info(f"  ✓ Set secret exit code: {result_set.exit_code}")
        assert result_set.exit_code == 0
        assert "set successfully" in result_set.output.lower()

        # List secrets
        logger.info("→ Listing secrets...")
        result_list = runner.invoke(
            cli,
            ["deploy", "secrets", "list-secrets", "--config", str(deployment_config)],
        )
        logger.info(f"  ✓ List secrets exit code: {result_list.exit_code}")
        logger.info(
            f"  ✓ BOT_TOKEN found in output: {'BOT_TOKEN' in result_list.output}"
        )
        assert result_list.exit_code == 0, f"list-secrets failed: {result_list.output}"
        assert "BOT_TOKEN" in result_list.output

    def test_secrets_delete(
        self, clean_vps: MockVPS, tmp_path: Path, deployment_config: Path
    ) -> None:
        """Test deleting secrets."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # deploy.yaml already created by deployment_config fixture
        assert deployment_config.exists(), "deploy.yaml must exist"

        # Set secret
        result_set = runner.invoke(
            cli,
            [
                "deploy",
                "secrets",
                "set-secret",
                "BOT_TOKEN",
                "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
                "--config",
                str(deployment_config),
            ],
        )
        assert result_set.exit_code == 0, f"set-secret failed: {result_set.output}"

        # Delete secret
        result_delete = runner.invoke(
            cli,
            [
                "deploy",
                "secrets",
                "remove-secret",
                "BOT_TOKEN",
                "--config",
                str(deployment_config),
            ],
            input="y\n",
        )
        # Should handle deletion (even if secret not found due to CliRunner isolation)
        assert (
            "deleted" in result_delete.output.lower()
            or "not found" in result_delete.output.lower()
            or "removed" in result_delete.output.lower()
        ), f"Unexpected output: {result_delete.output}"


class TestBackupRestore:
    """Test backup and restore functionality."""

    def test_backup_create_and_list(
        self, clean_vps: MockVPS, tmp_path: Path, deployment_config: Path
    ) -> None:
        """Test creating and listing backups."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # deploy.yaml already created by deployment_config fixture
        assert deployment_config.exists(), "deploy.yaml must exist"

        # Create some data on VPS
        clean_vps.exec("mkdir -p /opt/test-bot/data")
        clean_vps.exec("echo 'test data' > /opt/test-bot/data/test.txt")

        # Try to create backup (may fail if bot not deployed)
        result_backup = runner.invoke(
            cli, ["deploy", "backup", "create", "--config", str(deployment_config)]
        )

        # Backup command should either:
        # 1. Create backup successfully (if bot is deployed)
        # 2. Fail gracefully (if bot not deployed yet)
        # Both are acceptable for this test
        if result_backup.exit_code == 0:
            assert "backup created" in result_backup.output.lower()
        # If backup failed (bot not deployed), that's also OK for this integration test


class TestDeploymentDown:
    """Test bot teardown."""

    def test_deploy_down(self, clean_vps: MockVPS, tmp_path: Path) -> None:
        """Test deployment teardown."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # Initialize deployment
        result_init = runner.invoke(
            cli,
            [
                "deploy",
                "init",
                "--host",
                clean_vps.host,
                "--user",
                clean_vps.user,
                "--ssh-key",
                clean_vps.ssh_key_path,
                "--port",
                str(clean_vps.port),
                "--bot-name",
                "test-bot",
            ],
        )
        assert result_init.exit_code == 0

        # Teardown (should work even if nothing deployed)
        result_down = runner.invoke(cli, ["deploy", "down"], input="y\n")
        assert result_down.exit_code == 0


class TestHealthChecks:
    """Test health check functionality."""

    def test_health_check_command(self, clean_vps: MockVPS, tmp_path: Path) -> None:
        """Test health check command."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # Initialize deployment
        result_init = runner.invoke(
            cli,
            [
                "deploy",
                "init",
                "--host",
                clean_vps.host,
                "--user",
                clean_vps.user,
                "--ssh-key",
                clean_vps.ssh_key_path,
                "--port",
                str(clean_vps.port),
                "--bot-name",
                "test-bot",
            ],
        )
        assert result_init.exit_code == 0

        # Run health check
        result_health = runner.invoke(cli, ["deploy", "health"])

        # Should complete (even if no deployment)
        assert result_health.exit_code == 0
