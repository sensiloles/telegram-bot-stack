"""Tests for the 'new' command."""

from click.testing import CliRunner

from telegram_bot_stack.cli.main import cli


def test_new_basic_template(tmp_path, monkeypatch):
    """Test creating a bot from basic template."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(cli, ["new", "test-bot", "--template", "basic"])

    assert result.exit_code == 0
    assert (tmp_path / "test-bot").exists()
    assert (tmp_path / "test-bot" / "bot.py").exists()
    assert (tmp_path / "test-bot" / "README.md").exists()
    assert (
        tmp_path / "test-bot" / ".gitignore"
    ).exists(), ".gitignore should be created"


def test_new_counter_template(tmp_path, monkeypatch):
    """Test creating a bot from counter template."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(cli, ["new", "counter-bot", "--template", "counter"])

    assert result.exit_code == 0
    assert (tmp_path / "counter-bot").exists()
    assert (tmp_path / "counter-bot" / "bot.py").exists()
    assert (tmp_path / "counter-bot" / "README.md").exists()
    assert (
        tmp_path / "counter-bot" / ".gitignore"
    ).exists(), ".gitignore should be created"

    # Check counter-specific content
    bot_content = (tmp_path / "counter-bot" / "bot.py").read_text()
    assert "CounterBot" in bot_content
    assert "JSONStorage" in bot_content


def test_new_menu_template(tmp_path, monkeypatch):
    """Test creating a bot from menu template."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(cli, ["new", "menu-bot", "--template", "menu"])

    assert result.exit_code == 0
    assert (tmp_path / "menu-bot").exists()
    assert (tmp_path / "menu-bot" / "bot.py").exists()
    assert (
        tmp_path / "menu-bot" / ".gitignore"
    ).exists(), ".gitignore should be created"

    # Check menu-specific content
    bot_content = (tmp_path / "menu-bot" / "bot.py").read_text()
    assert "MenuBot" in bot_content
    assert "InlineKeyboardButton" in bot_content


def test_new_advanced_template(tmp_path, monkeypatch):
    """Test creating a bot from advanced template."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(cli, ["new", "advanced-bot", "--template", "advanced"])

    assert result.exit_code == 0
    assert (tmp_path / "advanced-bot").exists()
    assert (tmp_path / "advanced-bot" / "bot.py").exists()
    assert (
        tmp_path / "advanced-bot" / ".gitignore"
    ).exists(), ".gitignore should be created"

    # Check advanced-specific content
    bot_content = (tmp_path / "advanced-bot" / "bot.py").read_text()
    assert "AdvancedBot" in bot_content
    assert "SQLStorage" in bot_content
    assert "error_handler" in bot_content


def test_new_existing_directory(tmp_path, monkeypatch):
    """Test that new fails if directory exists."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    # Create directory
    (tmp_path / "existing-bot").mkdir()

    result = runner.invoke(cli, ["new", "existing-bot"])

    assert result.exit_code == 1
    assert "already exists" in result.output


def test_new_default_template(tmp_path, monkeypatch):
    """Test that default template is 'basic'."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(cli, ["new", "default-bot"])

    assert result.exit_code == 0
    assert (tmp_path / "default-bot" / "bot.py").exists()

    # Should use basic template by default
    bot_content = (tmp_path / "default-bot" / "bot.py").read_text()
    assert "EchoBot" in bot_content


def test_new_help():
    """Test new command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["new", "--help"])

    assert result.exit_code == 0
    assert "Create a new bot from a template" in result.output
    assert "basic" in result.output
    assert "counter" in result.output
    assert "menu" in result.output
    assert "advanced" in result.output
