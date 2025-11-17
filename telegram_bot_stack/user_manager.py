"""Generic user management for telegram bots."""

import logging
from typing import List

from .storage import StorageBackend

logger = logging.getLogger(__name__)


class UserManager:
    """Manages user registration and tracking.

    This class provides user management functionality including:
    - User registration
    - User existence checking
    - User removal
    - User listing and counting

    Args:
        storage: Storage backend instance for persisting user data
        storage_key: Key to use in storage for user data (default: "bot_users")

    Example:
        >>> from telegram_bot_stack.storage import JSONStorage
        >>> storage = JSONStorage(base_dir="data")
        >>> user_manager = UserManager(storage)
        >>> user_manager.add_user(12345)
        True
        >>> user_manager.user_exists(12345)
        True
    """

    def __init__(self, storage: StorageBackend, storage_key: str = "bot_users"):
        """Initialize user manager with storage."""
        self.storage = storage
        self.storage_key = storage_key
        self.users: List[int] = self._load_users()

    def _load_users(self) -> List[int]:
        """Load registered users from storage."""
        users = self.storage.load(self.storage_key, [])
        if users:
            logger.info(f"Loaded {len(users)} users from storage")
        return users

    def save_users(self) -> bool:
        """Save registered users to storage.

        Returns:
            True if save was successful, False otherwise
        """
        return self.storage.save(self.storage_key, self.users)

    def add_user(self, user_id: int) -> bool:
        """Add a new user if not already registered.

        Args:
            user_id: Telegram user ID

        Returns:
            True if user was added, False if already exists
        """
        if user_id not in self.users:
            self.users.append(user_id)
            self.save_users()
            logger.info(f"New user added: {user_id}")
            return True
        return False

    def remove_user(self, user_id: int) -> bool:
        """Remove a user from the registered users list.

        Args:
            user_id: Telegram user ID

        Returns:
            True if user was removed, False if not found
        """
        if user_id in self.users:
            self.users.remove(user_id)
            self.save_users()
            logger.info(f"User removed: {user_id}")
            return True
        return False

    def user_exists(self, user_id: int) -> bool:
        """Check if user exists in the registered users list.

        Args:
            user_id: Telegram user ID

        Returns:
            True if user is registered, False otherwise
        """
        return user_id in self.users

    def get_all_users(self) -> List[int]:
        """Get list of all registered users.

        Returns:
            Copy of the users list
        """
        return self.users.copy()

    def get_user_count(self) -> int:
        """Get the number of registered users.

        Returns:
            Number of registered users
        """
        return len(self.users)
