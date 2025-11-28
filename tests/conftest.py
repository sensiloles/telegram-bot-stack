"""Pytest configuration and shared fixtures."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from telegram_bot_stack.admin_manager import AdminManager
from telegram_bot_stack.storage import MemoryStorage
from telegram_bot_stack.user_manager import UserManager

# Register integration test plugins
pytest_plugins = ["tests.integration.fixtures.mock_vps"]


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-e2e",
        action="store_true",
        default=False,
        help="Run E2E tests (requires Mock VPS with Docker-in-Docker)",
    )


def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "e2e: mark test as E2E test (requires Mock VPS, Docker-in-Docker)"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to skip E2E tests by default."""
    if config.getoption("--run-e2e"):
        # --run-e2e given in cli: do not skip E2E tests
        return

    skip_e2e = pytest.mark.skip(reason="E2E tests skipped (use --run-e2e to run)")
    for item in items:
        # Skip all tests in tests/e2e/ directory
        if "tests/e2e/" in str(item.fspath):
            item.add_marker(skip_e2e)
        # Also skip tests marked with @pytest.mark.e2e
        elif "e2e" in item.keywords:
            item.add_marker(skip_e2e)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_storage() -> MemoryStorage:
    """Create temporary storage for testing.

    Uses MemoryStorage for fast tests without file I/O.

    Returns:
        MemoryStorage instance
    """
    return MemoryStorage()


@pytest.fixture
def user_manager(temp_storage: MemoryStorage) -> UserManager:
    """Create UserManager with temporary storage.

    Args:
        temp_storage: Temporary storage fixture

    Returns:
        UserManager instance
    """
    return UserManager(temp_storage, "test_users")


@pytest.fixture
def admin_manager(temp_storage: MemoryStorage) -> AdminManager:
    """Create AdminManager with temporary storage.

    Args:
        temp_storage: Temporary storage fixture

    Returns:
        AdminManager instance
    """
    return AdminManager(temp_storage, "test_admins")


@pytest.fixture
def mock_telegram_update():
    """Create mock Telegram update for testing.

    Returns:
        Mock update object with common attributes
    """
    update = MagicMock()
    update.effective_user.id = 12345
    update.effective_user.first_name = "Test User"
    update.message.reply_text = AsyncMock()
    update.message.text = "/start"
    return update


@pytest.fixture
def mock_telegram_context():
    """Create mock Telegram context for testing.

    Returns:
        Mock context object with common attributes
    """
    context = MagicMock()
    context.args = []
    context.bot = MagicMock()
    context.bot.send_message = AsyncMock()
    return context


@pytest.fixture
def sample_user_data():
    """Sample user data for testing.

    Returns:
        Dictionary with user data
    """
    return {
        "user_id": 12345,
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "is_active": True,
    }


@pytest.fixture
def sample_admin_data():
    """Sample admin data for testing.

    Returns:
        List of admin user IDs
    """
    return [12345, 67890, 11111]
