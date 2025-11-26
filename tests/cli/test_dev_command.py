"""Tests for the 'dev' command."""

from unittest.mock import patch

from click.testing import CliRunner

from telegram_bot_stack.cli.main import cli


def test_dev_no_bot_file(tmp_path, monkeypatch):
    """Test dev command fails when bot.py doesn't exist."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(cli, ["dev"])

    assert result.exit_code == 1
    assert "Bot file not found" in result.output


def test_dev_with_bot_file(tmp_path, monkeypatch):
    """Test dev command with bot.py present."""
    monkeypatch.chdir(tmp_path)

    # Create minimal bot.py
    bot_file = tmp_path / "bot.py"
    bot_file.write_text(
        """
import asyncio
print("Bot running")
asyncio.run(asyncio.sleep(0.1))
"""
    )

    runner = CliRunner()

    # Mock subprocess to avoid actually running the bot
    with patch("telegram_bot_stack.cli.commands.dev.subprocess.run") as mock_run:
        mock_run.side_effect = KeyboardInterrupt()

        result = runner.invoke(cli, ["dev", "--no-reload"])

        assert "Starting bot" in result.output
        mock_run.assert_called_once()


def test_dev_no_env_warning(tmp_path, monkeypatch):
    """Test dev command warns when .env is missing."""
    monkeypatch.chdir(tmp_path)

    # Create bot.py but no .env
    (tmp_path / "bot.py").write_text("print('test')")

    runner = CliRunner()

    with patch("telegram_bot_stack.cli.commands.dev.subprocess.run") as mock_run:
        mock_run.side_effect = KeyboardInterrupt()

        result = runner.invoke(cli, ["dev", "--no-reload"])

        assert ".env file not found" in result.output


def test_dev_custom_bot_file(tmp_path, monkeypatch):
    """Test dev command with custom bot file."""
    monkeypatch.chdir(tmp_path)

    # Create custom bot file
    custom_bot = tmp_path / "my_bot.py"
    custom_bot.write_text("print('custom bot')")

    runner = CliRunner()

    with patch("telegram_bot_stack.cli.commands.dev.subprocess.run") as mock_run:
        mock_run.side_effect = KeyboardInterrupt()

        result = runner.invoke(cli, ["dev", "--bot-file", "my_bot.py", "--no-reload"])

        assert "Starting bot" in result.output
        mock_run.assert_called_once()


def test_dev_reload_mode(tmp_path, monkeypatch):
    """Test dev command with reload enabled."""
    monkeypatch.chdir(tmp_path)

    # Create bot.py
    (tmp_path / "bot.py").write_text("print('test')")

    runner = CliRunner()

    # Mock watchdog to avoid actual file watching
    with patch("telegram_bot_stack.cli.commands.dev._run_with_reload") as mock_reload:
        mock_reload.side_effect = KeyboardInterrupt()

        result = runner.invoke(cli, ["dev", "--reload"])

        # Verify _run_with_reload was called
        mock_reload.assert_called_once()


def test_dev_help():
    """Test dev command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["dev", "--help"])

    assert result.exit_code == 0
    assert "Run bot in development mode" in result.output
    assert "--reload" in result.output
    assert "--bot-file" in result.output
