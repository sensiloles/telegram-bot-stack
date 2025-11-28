"""Tests for deployment CLI commands."""

import os
from pathlib import Path

from click.testing import CliRunner

from telegram_bot_stack.cli.main import cli
from tests.integration.conftest import get_cli_output

TEST_BOT_NAME = "test-bot"


class TestDeployInitCommand:
    """Test 'deploy init' command."""

    def test_init_command_execution(self, tmp_path: Path) -> None:
        """Test deploy init command can be executed."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # Command will try to connect via SSH and fail gracefully
        result = runner.invoke(
            cli,
            [
                "deploy",
                "init",
                "--host",
                "invalid.test.example.com",
                "--user",
                "root",
                "--ssh-key",
                "~/.ssh/id_rsa",
                "--bot-name",
                TEST_BOT_NAME,
            ],
        )

        # Should fail SSH but not crash
        output = get_cli_output(result, runner)
        assert "SSH" in output or "failed" in output.lower() or result.exit_code == 0


class TestDeployUpCommand:
    """Test 'deploy up' command."""

    def test_up_without_config(self, tmp_path: Path) -> None:
        """Test deploy up fails gracefully without config."""
        os.chdir(tmp_path)
        runner = CliRunner()

        result = runner.invoke(cli, ["deploy", "up"])
        output = get_cli_output(result, runner)

        # Should show error about missing config
        assert "not found" in output.lower() or "configuration" in output.lower()


class TestDeployStatusCommand:
    """Test 'deploy status' command."""

    def test_status_without_config(self, tmp_path: Path) -> None:
        """Test deploy status without config."""
        os.chdir(tmp_path)
        runner = CliRunner()

        result = runner.invoke(cli, ["deploy", "status"])
        output = get_cli_output(result, runner)

        # Should handle missing config gracefully
        assert "not found" in output.lower() or "configuration" in output.lower()


class TestDeployDownCommand:
    """Test 'deploy down' command."""

    def test_down_without_config(self, tmp_path: Path) -> None:
        """Test deploy down without config."""
        os.chdir(tmp_path)
        runner = CliRunner()

        result = runner.invoke(cli, ["deploy", "down"])
        output = get_cli_output(result, runner)

        # Should handle missing config gracefully
        assert "not found" in output.lower() or "configuration" in output.lower()
