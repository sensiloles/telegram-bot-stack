"""Storage abstraction layer for telegram-bot-stack.

This module provides a unified interface for different storage backends.
Supported backends:
- JSONStorage: File-based JSON storage (default)
- MemoryStorage: In-memory storage for testing

Example:
    >>> from telegram_bot_stack.storage import create_storage, JSONStorage
    >>>
    >>> # Using factory function
    >>> storage = create_storage("json", base_dir="data")
    >>>
    >>> # Or directly instantiate
    >>> storage = JSONStorage(base_dir="data")
    >>> storage.save("users", {"user1": {"name": "John"}})
"""

import logging
from typing import Any

from .base import StorageBackend
from .json import JSONStorage
from .memory import MemoryStorage

logger = logging.getLogger(__name__)

__all__ = [
    "StorageBackend",
    "JSONStorage",
    "MemoryStorage",
    "create_storage",
    "Storage",
]


def create_storage(backend: str = "json", **kwargs: Any) -> StorageBackend:
    """Factory function to create storage backends.

    Args:
        backend: Storage backend type ("json" or "memory")
        **kwargs: Backend-specific configuration options
            For JSONStorage:
                - base_dir: Base directory for JSON files
            For MemoryStorage:
                - (no options)

    Returns:
        Configured storage backend instance

    Raises:
        ValueError: If backend type is not supported

    Example:
        >>> # Create JSON storage
        >>> storage = create_storage("json", base_dir="data")
        >>>
        >>> # Create memory storage for testing
        >>> storage = create_storage("memory")
    """
    backend = backend.lower()

    if backend == "json":
        return JSONStorage(**kwargs)
    elif backend == "memory":
        if kwargs:
            logger.warning(f"MemoryStorage ignores kwargs: {kwargs}")
        return MemoryStorage()
    else:
        raise ValueError(
            f"Unsupported storage backend: {backend}. "
            f"Supported backends: 'json', 'memory'"
        )


# Backward compatibility: alias JSONStorage as Storage
Storage = JSONStorage
