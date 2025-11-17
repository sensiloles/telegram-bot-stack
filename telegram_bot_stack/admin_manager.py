"""Generic admin management for telegram bots."""

import logging
from typing import List

from .storage import StorageBackend

logger = logging.getLogger(__name__)


class AdminManager:
    """Manages administrator privileges for bot users.

    This class provides admin management functionality including:
    - Admin addition and removal
    - Admin privilege checking
    - Admin listing and counting
    - Protection against removing the last admin

    Args:
        storage: Storage backend instance for persisting admin data
        storage_key: Key to use in storage for admin data (default: "bot_admins")

    Example:
        >>> from telegram_bot_stack.storage import JSONStorage
        >>> storage = JSONStorage(base_dir="data")
        >>> admin_manager = AdminManager(storage)
        >>> admin_manager.add_admin(12345)
        True
        >>> admin_manager.is_admin(12345)
        True
    """

    def __init__(self, storage: StorageBackend, storage_key: str = "bot_admins"):
        """Initialize admin manager with storage."""
        self.storage = storage
        self.storage_key = storage_key
        self.admins: List[int] = self._load_admins()

    def _load_admins(self) -> List[int]:
        """Load admin users from storage."""
        admins = self.storage.load(self.storage_key, [])
        if not admins:
            logger.warning(
                "Admins list is empty, first user to interact will become admin"
            )
        else:
            logger.info(f"Loaded {len(admins)} admins from storage")
        return admins

    def save_admins(self) -> bool:
        """Save admin users to storage.

        Returns:
            True if save was successful, False otherwise
        """
        return self.storage.save(self.storage_key, self.admins)

    def add_admin(self, user_id: int) -> bool:
        """Add a new admin if not already an admin.

        Args:
            user_id: Telegram user ID

        Returns:
            True if admin was added, False if already exists
        """
        if user_id not in self.admins:
            self.admins.append(user_id)
            self.save_admins()
            logger.info(f"New admin added: {user_id}")
            return True
        return False

    def remove_admin(self, user_id: int) -> bool:
        """Remove a user from admin list.

        Protection: Cannot remove the last admin to prevent lockout.

        Args:
            user_id: Telegram user ID

        Returns:
            True if admin was removed, False if not found or is the last admin
        """
        if user_id in self.admins:
            # Don't remove the last admin
            if len(self.admins) <= 1:
                logger.warning(f"Cannot remove the last admin: {user_id}")
                return False

            self.admins.remove(user_id)
            self.save_admins()
            logger.info(f"Admin removed: {user_id}")
            return True
        return False

    def is_admin(self, user_id: int) -> bool:
        """Check if user is an admin.

        Args:
            user_id: Telegram user ID

        Returns:
            True if user is an admin, False otherwise
        """
        return user_id in self.admins

    def get_all_admins(self) -> List[int]:
        """Get list of all admin users.

        Returns:
            Copy of the admins list
        """
        return self.admins.copy()

    def get_admin_count(self) -> int:
        """Get the number of admins.

        Returns:
            Number of admins
        """
        return len(self.admins)

    def has_admins(self) -> bool:
        """Check if there are any admins.

        Returns:
            True if there is at least one admin, False otherwise
        """
        return len(self.admins) > 0
