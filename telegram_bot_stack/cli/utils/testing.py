"""Testing setup utilities."""

from pathlib import Path

import click


def create_test_structure(project_path: Path, bot_name: str) -> None:
    """Create test directory structure with fixtures and sample tests.

    Args:
        project_path: Path to the project directory
        bot_name: Name of the bot (for test imports)
    """
    tests_dir = project_path / "tests"
    tests_dir.mkdir(exist_ok=True)

    # Create __init__.py
    (tests_dir / "__init__.py").write_text('"""Tests for the bot."""\n')

    # Create conftest.py with fixtures
    conftest_content = '''"""Pytest configuration and fixtures."""

import pytest

from telegram_bot_stack import MemoryStorage


@pytest.fixture
def storage():
    """Test storage fixture."""
    return MemoryStorage()


@pytest.fixture
def bot(storage):
    """Test bot fixture."""
    from bot import Bot

    return Bot(storage=storage)


@pytest.fixture
def mock_update(mocker):
    """Mock Telegram Update fixture."""
    update = mocker.MagicMock()
    update.effective_user.id = 12345
    update.effective_user.first_name = "Test User"
    update.effective_chat.id = 12345
    return update


@pytest.fixture
def mock_context(mocker):
    """Mock Telegram Context fixture."""
    context = mocker.MagicMock()
    return context
'''

    (tests_dir / "conftest.py").write_text(conftest_content)

    # Create sample test file
    test_bot_content = '''"""Tests for the bot."""

import pytest


def test_bot_initialization(bot):
    """Test that bot initializes correctly."""
    assert bot is not None
    assert bot.storage is not None


def test_welcome_message(bot):
    """Test welcome message."""
    message = bot.get_welcome_message()
    assert message is not None
    assert isinstance(message, str)
    assert len(message) > 0


@pytest.mark.asyncio
async def test_start_command(bot, mock_update, mock_context):
    """Test /start command."""
    await bot.start(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()
'''

    (tests_dir / "test_bot.py").write_text(test_bot_content)

    # Create pytest.ini
    pytest_ini_content = """[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = -v --strict-markers
"""

    (project_path / "pytest.ini").write_text(pytest_ini_content)

    click.secho("  ✅ Created test structure", fg="green")
