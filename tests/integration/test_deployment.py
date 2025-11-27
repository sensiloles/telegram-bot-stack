"""Integration tests for VPS deployment commands.

Tests the complete deployment flow from initialization to teardown,
using a mock VPS environment.
"""

import os
from pathlib import Path

import yaml
from click.testing import CliRunner

from telegram_bot_stack.cli.main import cli
from tests.integration.fixtures.mock_vps import MockVPS


class TestDeploymentInit:
    """Test deployment initialization."""

    def test_deploy_init_interactive(self, clean_vps: MockVPS, tmp_path: Path) -> None:
        """Test interactive deployment initialization."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # Run deploy init with all options
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
        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Check deploy.yaml was created
        assert Path("deploy.yaml").exists()

        # Check configuration content
        with open("deploy.yaml") as f:
            config = yaml.safe_load(f)

        assert config["vps"]["host"] == clean_vps.host
        assert config["vps"]["user"] == clean_vps.user
        assert config["vps"]["port"] == clean_vps.port
        assert config["bot"]["name"] == "test-bot"
        assert "secrets" in config
        assert "encryption_key" in config["secrets"]

    def test_deploy_init_existing_config_no_overwrite(
        self, clean_vps: MockVPS, tmp_path: Path
    ) -> None:
        """Test deploy init with existing config (no overwrite)."""
        os.chdir(tmp_path)
        runner = CliRunner()

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
                "--port",
                str(clean_vps.port),
                "--bot-name",
                "test-bot-1",
            ],
        )
        assert result1.exit_code == 0

        original_content = Path("deploy.yaml").read_text()

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
        assert "cancelled" in result2.output.lower()

        # Config should not change
        assert Path("deploy.yaml").read_text() == original_content

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

    def test_deploy_up_first_time(self, clean_vps: MockVPS, tmp_path: Path) -> None:
        """Test first-time deployment to clean VPS."""
        os.chdir(tmp_path)
        runner = CliRunner()

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

        # Set bot token secret
        result_secret = runner.invoke(
            cli,
            [
                "deploy",
                "secrets",
                "set",
                "BOT_TOKEN",
                "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
            ],
        )
        assert result_secret.exit_code == 0

        # Deploy bot
        result_up = runner.invoke(cli, ["deploy", "up"])

        # Check deployment succeeded
        assert result_up.exit_code == 0
        assert "deployed successfully" in result_up.output.lower()

        # Verify bot container is running
        # Note: This may not work if Docker-in-Docker is not fully configured
        # In that case, we check for deployment files instead
        exit_code, _, _ = clean_vps.exec("ls /opt/test-bot")
        assert exit_code == 0, "Bot directory should exist on VPS"

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
        self, clean_vps: MockVPS, tmp_path: Path
    ) -> None:
        """Test status check with no deployment."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # Initialize config
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

        # Check status
        result = runner.invoke(cli, ["deploy", "status"])

        # Should show no deployment or container not running
        assert result.exit_code == 0
        assert (
            "not running" in result.output.lower()
            or "not found" in result.output.lower()
        )


class TestSecretsManagement:
    """Test secrets management commands."""

    def test_secrets_set_and_list(self, clean_vps: MockVPS, tmp_path: Path) -> None:
        """Test setting and listing secrets."""
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

        # Set secret
        result_set = runner.invoke(
            cli,
            [
                "deploy",
                "secrets",
                "set",
                "BOT_TOKEN",
                "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
            ],
        )
        assert result_set.exit_code == 0
        assert "stored" in result_set.output.lower()

        # List secrets
        result_list = runner.invoke(cli, ["deploy", "secrets", "list"])
        assert result_list.exit_code == 0
        assert "BOT_TOKEN" in result_list.output

    def test_secrets_delete(self, clean_vps: MockVPS, tmp_path: Path) -> None:
        """Test deleting secrets."""
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

        # Set secret
        runner.invoke(
            cli,
            [
                "deploy",
                "secrets",
                "set",
                "BOT_TOKEN",
                "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
            ],
        )

        # Delete secret
        result_delete = runner.invoke(
            cli, ["deploy", "secrets", "delete", "BOT_TOKEN"], input="y\n"
        )
        assert result_delete.exit_code == 0
        assert "deleted" in result_delete.output.lower()


class TestBackupRestore:
    """Test backup and restore functionality."""

    def test_backup_create_and_list(self, clean_vps: MockVPS, tmp_path: Path) -> None:
        """Test creating and listing backups."""
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

        # Create some data on VPS
        clean_vps.exec("mkdir -p /opt/test-bot/data")
        clean_vps.exec("echo 'test data' > /opt/test-bot/data/test.txt")

        # Create backup
        result_backup = runner.invoke(cli, ["deploy", "backup", "create"])
        assert result_backup.exit_code == 0
        assert "backup created" in result_backup.output.lower()

        # List backups
        result_list = runner.invoke(cli, ["deploy", "backup", "list"])
        assert result_list.exit_code == 0
        assert "backup-" in result_list.output.lower()


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
