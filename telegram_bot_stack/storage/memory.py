"""In-memory storage backend for testing."""

import logging
from copy import deepcopy
from typing import Any, Dict

from .base import StorageBackend

logger = logging.getLogger(__name__)


class MemoryStorage(StorageBackend):
    """In-memory storage backend for testing.

    This backend stores data in memory using a dictionary.
    Data is not persisted between runs and is lost when the process exits.

    This is useful for:
    - Unit testing (no file I/O overhead)
    - Temporary data that doesn't need persistence
    - Development and debugging

    Example:
        >>> storage = MemoryStorage()
        >>> storage.save("users", {"user1": {"name": "John"}})
        >>> storage.load("users")
        {"user1": {"name": "John"}}
    """

    def __init__(self):
        """Initialize empty in-memory storage."""
        self._data: Dict[str, Any] = {}
        logger.debug("Initialized MemoryStorage")

    def save(self, key: str, data: Any) -> bool:
        """Save data to memory.

        Args:
            key: Identifier for the data
            data: Data to save (will be deep copied)

        Returns:
            Always True (memory operations don't fail)
        """
        try:
            # Deep copy to avoid external mutations
            self._data[key] = deepcopy(data)
            logger.debug(f"Data saved to memory with key: {key}")
            return True
        except Exception as e:
            logger.error(f"Error saving to memory with key {key}: {e}")
            return False

    def load(self, key: str, default: Any = None) -> Any:
        """Load data from memory.

        Args:
            key: Identifier for the data
            default: Default value to return if key doesn't exist

        Returns:
            Loaded data (deep copied) or default value
        """
        if key not in self._data:
            logger.debug(f"Key {key} not found in memory, using default value")
            return default if default is not None else []

        try:
            # Deep copy to avoid external mutations
            data = deepcopy(self._data[key])
            logger.debug(f"Data loaded from memory with key: {key}")
            return data
        except Exception as e:
            logger.error(f"Error loading from memory with key {key}: {e}")
            return default if default is not None else []

    def exists(self, key: str) -> bool:
        """Check if data exists in memory.

        Args:
            key: Identifier for the data

        Returns:
            True if key exists, False otherwise
        """
        return key in self._data

    def delete(self, key: str) -> bool:
        """Delete data from memory.

        Args:
            key: Identifier for the data

        Returns:
            True if deletion was successful, False if key didn't exist
        """
        if key in self._data:
            del self._data[key]
            logger.debug(f"Deleted key from memory: {key}")
            return True
        logger.debug(f"Key {key} not found in memory, nothing to delete")
        return False

    def clear(self) -> None:
        """Clear all data from memory.

        This is useful for resetting state between tests.
        """
        self._data.clear()
        logger.debug("Cleared all data from memory")
