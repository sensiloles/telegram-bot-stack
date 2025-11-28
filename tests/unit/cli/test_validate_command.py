"""Tests for validate command."""

from pathlib import Path

from click.testing import CliRunner

from telegram_bot_stack.cli.main import cli


def test_validate_no_bot_file(tmp_path):
    """Test validate fails when bot.py doesn't exist."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["validate"])

        assert "bot.py not found" in result.output


def test_validate_no_env_file(tmp_path):
    """Test validate warns when .env doesn't exist."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Create bot.py
        Path("bot.py").write_text("# bot")

        result = runner.invoke(cli, ["validate"])

        assert ".env file not found" in result.output


def test_validate_no_bot_token(tmp_path):
    """Test validate fails when BOT_TOKEN not set."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Create bot.py and .env
        Path("bot.py").write_text("# bot")
        Path(".env").write_text("")

        result = runner.invoke(cli, ["validate"])

        assert "BOT_TOKEN not set" in result.output


def test_validate_success(tmp_path, monkeypatch):
    """Test validate succeeds with proper setup."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Create bot.py with proper imports
        Path("bot.py").write_text(
            """
from telegram_bot_stack import BotBase, MemoryStorage

class Bot(BotBase):
    pass
"""
        )
        Path(".env").write_text("BOT_TOKEN=123456:ABC-DEF")

        # Set BOT_TOKEN in environment
        monkeypatch.setenv(
            "BOT_TOKEN", "123456:ABC-DEF1234567890abcdefghijklmnopqrstuvwxyz"
        )

        result = runner.invoke(cli, ["validate"])

        assert "bot.py found" in result.output
        assert ".env file found" in result.output


def test_validate_strict_mode(tmp_path):
    """Test validate exits with error in strict mode."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["validate", "--strict"])

        assert result.exit_code == 1
