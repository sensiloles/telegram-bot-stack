"""JSON file-based storage backend."""

import json
import logging
from pathlib import Path
from typing import Any, Optional, Union

from .base import StorageBackend

logger = logging.getLogger(__name__)


class JSONStorage(StorageBackend):
    """JSON file-based storage backend.

    This backend stores data in JSON files in a specified directory.
    Each key corresponds to a separate JSON file.

    Args:
        base_dir: Base directory for storage files. If None, uses current directory.

    Example:
        >>> storage = JSONStorage(base_dir="data")
        >>> storage.save("users", {"user1": {"name": "John"}})
        >>> storage.load("users")
        {"user1": {"name": "John"}}
    """

    def __init__(self, base_dir: Optional[Union[str, Path]] = None) -> None:
        """Initialize JSON storage with a base directory."""
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Initialized JSONStorage with base_dir: {self.base_dir}")

    def save(self, key: str, data: Any) -> bool:
        """Save data to JSON file.

        Args:
            key: Identifier for the data (will be used as filename)
            data: Data to save (must be JSON serializable)

        Returns:
            True if save was successful, False otherwise
        """
        filepath = self._get_filepath(key)
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug(f"Data saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving to {filepath}: {e}")
            return False

    def load(self, key: str, default: Any = None) -> Any:
        """Load data from JSON file.

        Args:
            key: Identifier for the data
            default: Default value to return if file doesn't exist or error occurs

        Returns:
            Loaded data or default value
        """
        filepath = self._get_filepath(key)
        if not filepath.exists():
            logger.debug(f"File {filepath} not found, using default value")
            return default if default is not None else []

        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
            logger.debug(f"Data loaded from {filepath}")
            return data
        except Exception as e:
            logger.error(f"Error loading from {filepath}: {e}")
            return default if default is not None else []

    def exists(self, key: str) -> bool:
        """Check if data file exists.

        Args:
            key: Identifier for the data

        Returns:
            True if data file exists, False otherwise
        """
        filepath = self._get_filepath(key)
        return filepath.exists()

    def delete(self, key: str) -> bool:
        """Delete data file.

        Args:
            key: Identifier for the data

        Returns:
            True if deletion was successful, False otherwise
        """
        filepath = self._get_filepath(key)
        try:
            if filepath.exists():
                filepath.unlink()
                logger.info(f"Deleted {filepath}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting {filepath}: {e}")
            return False

    def _get_filepath(self, key: str) -> Path:
        """Get full filepath for a given key.

        Args:
            key: Identifier for the data

        Returns:
            Full path to the file
        """
        # If key already has .json extension, use as is, otherwise add it
        if not key.endswith(".json"):
            key = f"{key}.json"
        return self.base_dir / key
