"""Base storage backend interface for telegram-bot-stack."""

from abc import ABC, abstractmethod
from typing import Any


class StorageBackend(ABC):
    """Abstract base class for storage backends.

    All storage backends must implement this interface to ensure
    compatibility with the framework.
    """

    @abstractmethod
    def save(self, key: str, data: Any) -> bool:
        """Save data to storage.

        Args:
            key: Unique identifier for the data
            data: Data to save (must be serializable)

        Returns:
            True if save was successful, False otherwise
        """
        pass

    @abstractmethod
    def load(self, key: str, default: Any = None) -> Any:
        """Load data from storage.

        Args:
            key: Unique identifier for the data
            default: Default value to return if key doesn't exist

        Returns:
            Loaded data or default value
        """
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if data exists in storage.

        Args:
            key: Unique identifier for the data

        Returns:
            True if data exists, False otherwise
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete data from storage.

        Args:
            key: Unique identifier for the data

        Returns:
            True if deletion was successful, False otherwise
        """
        pass
