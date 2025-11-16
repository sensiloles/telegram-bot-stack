"""Pytest configuration and shared fixtures."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core.admin_manager import AdminManager
from src.core.storage import Storage
from src.core.user_manager import UserManager


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_storage(tmp_path: Path) -> Storage:
    """Create temporary storage for testing.

    Args:
        tmp_path: Pytest's temporary directory fixture

    Returns:
        Storage instance with temporary directory
    """
    return Storage(tmp_path)


@pytest.fixture
def user_manager(temp_storage: Storage) -> UserManager:
    """Create UserManager with temporary storage.

    Args:
        temp_storage: Temporary storage fixture

    Returns:
        UserManager instance
    """
    return UserManager(temp_storage, "test_users")


@pytest.fixture
def admin_manager(temp_storage: Storage) -> AdminManager:
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
