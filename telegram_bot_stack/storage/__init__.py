"""Storage abstraction layer for telegram-bot-stack.

This module provides a unified interface for different storage backends.
Supported backends:
- JSONStorage: File-based JSON storage (default)
- MemoryStorage: In-memory storage for testing
- SQLStorage: SQL database storage (SQLite/PostgreSQL)

Example:
    >>> from telegram_bot_stack.storage import create_storage, JSONStorage
    >>>
    >>> # Using factory function
    >>> storage = create_storage("json", base_dir="data")
    >>>
    >>> # Or directly instantiate
    >>> storage = JSONStorage(base_dir="data")
    >>> storage.save("users", {"user1": {"name": "John"}})
    >>>
    >>> # SQL storage
    >>> storage = create_storage("sqlite", database_url="sqlite:///bot.db")
"""

import logging
from typing import Any

from .base import StorageBackend
from .json import JSONStorage
from .memory import MemoryStorage

logger = logging.getLogger(__name__)

# Try to import SQLStorage (optional dependency)
try:
    from .sql import SQLStorage

    _SQL_AVAILABLE = True
except ImportError:
    _SQL_AVAILABLE = False
    SQLStorage = None  # type: ignore
    logger.debug(
        "SQLStorage not available. Install with: pip install telegram-bot-stack[database]"
    )

__all__ = [
    "StorageBackend",
    "JSONStorage",
    "MemoryStorage",
    "SQLStorage",
    "create_storage",
    "Storage",
]


def create_storage(backend: str = "json", **kwargs: Any) -> StorageBackend:
    """Factory function to create storage backends.

    Args:
        backend: Storage backend type ("json", "memory", "sqlite", or "postgres")
        **kwargs: Backend-specific configuration options
            For JSONStorage:
                - base_dir: Base directory for JSON files
            For MemoryStorage:
                - (no options)
            For SQLStorage:
                - database_url: SQLAlchemy database URL (required)
                - echo: Enable SQL query logging (default: False)
                - pool_size: Connection pool size (default: 5)
                - max_overflow: Max overflow connections (default: 10)

    Returns:
        Configured storage backend instance

    Raises:
        ValueError: If backend type is not supported
        ImportError: If SQL backend is requested but dependencies not installed

    Example:
        >>> # Create JSON storage
        >>> storage = create_storage("json", base_dir="data")
        >>>
        >>> # Create memory storage for testing
        >>> storage = create_storage("memory")
        >>>
        >>> # Create SQLite storage
        >>> storage = create_storage("sqlite", database_url="sqlite:///bot.db")
        >>>
        >>> # Create PostgreSQL storage
        >>> storage = create_storage(
        ...     "postgres",
        ...     database_url="postgresql://user:pass@localhost/bot_db"
        ... )
    """
    backend = backend.lower()

    if backend == "json":
        return JSONStorage(**kwargs)
    elif backend == "memory":
        if kwargs:
            logger.warning(f"MemoryStorage ignores kwargs: {kwargs}")
        return MemoryStorage()
    elif backend in ("sqlite", "postgres", "postgresql", "sql"):
        if not _SQL_AVAILABLE:
            raise ImportError(
                "SQLStorage requires additional dependencies. "
                "Install with: pip install telegram-bot-stack[database]"
            )

        # Handle database_url for convenience shortcuts
        if backend == "sqlite" and "database_url" not in kwargs:
            # Default SQLite database
            kwargs["database_url"] = "sqlite:///bot.db"
        elif backend in ("postgres", "postgresql") and "database_url" not in kwargs:
            raise ValueError(
                "PostgreSQL backend requires 'database_url' parameter. "
                "Example: database_url='postgresql://user:pass@localhost/bot_db'"
            )

        return SQLStorage(**kwargs)
    else:
        supported = "'json', 'memory'"
        if _SQL_AVAILABLE:
            supported += ", 'sqlite', 'postgres'"
        raise ValueError(
            f"Unsupported storage backend: {backend}. Supported backends: {supported}"
        )


# Backward compatibility: alias JSONStorage as Storage
Storage = JSONStorage
