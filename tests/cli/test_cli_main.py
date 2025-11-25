"""Tests for CLI main entry point."""

from click.testing import CliRunner

from telegram_bot_stack.cli.main import cli


def test_cli_help():
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "Telegram Bot Stack" in result.output
    assert "init" in result.output
    assert "new" in result.output
    assert "dev" in result.output
    assert "validate" in result.output


def test_cli_version():
    """Test CLI version command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert "version" in result.output.lower()


def test_init_help():
    """Test init command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["init", "--help"])

    assert result.exit_code == 0
    assert "Initialize a new bot project" in result.output
    assert "--package-manager" in result.output
    assert "--with-linting" in result.output
    assert "--ide" in result.output


def test_new_help():
    """Test new command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["new", "--help"])

    assert result.exit_code == 0
    assert "Create a new bot from a template" in result.output
    assert "--template" in result.output


def test_dev_help():
    """Test dev command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["dev", "--help"])

    assert result.exit_code == 0
    assert "development mode" in result.output
    assert "--reload" in result.output


def test_validate_help():
    """Test validate command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["validate", "--help"])

    assert result.exit_code == 0
    assert "Validate bot configuration" in result.output
    assert "--strict" in result.output
