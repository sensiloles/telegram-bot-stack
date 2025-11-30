"""telegram-bot-stack: Reusable framework for building Telegram bots.

This package provides a solid foundation for building Telegram bots with
common patterns and best practices built-in.

Key Features:
    - User and admin management out of the box
    - Multiple storage backends (JSON, Memory)
    - Command handling infrastructure
    - Graceful shutdown handling
    - Easy customization through hooks

Quick Start:
    >>> from telegram_bot_stack import BotBase
    >>> from telegram_bot_stack.storage import JSONStorage
    >>>
    >>> # Create storage and bot
    >>> storage = JSONStorage(base_dir="data")
    >>> bot = BotBase(storage, bot_name="My Bot")
    >>>
    >>> # Customize behavior by overriding hooks
    >>> class MyBot(BotBase):
    ...     def get_welcome_message(self) -> str:
    ...         return "Welcome to My Custom Bot!"

For more information, see the documentation at:
https://github.com/sensiloles/telegram-bot-stack
"""

from .admin_manager import AdminManager
from .bot_base import BotBase
from .decorators import rate_limit
from .storage import (
    JSONStorage,
    MemoryStorage,
    Storage,
    StorageBackend,
    create_storage,
)
from .user_manager import UserManager

__version__ = "1.34.5"
__author__ = "telegram-bot-stack contributors"
__license__ = "Business Source License 1.1"
__all__ = [
    # Core classes
    "BotBase",
    "UserManager",
    "AdminManager",
    # Decorators
    "rate_limit",
    # Storage
    "StorageBackend",
    "JSONStorage",
    "MemoryStorage",
    "Storage",
    "create_storage",
    # Metadata
    "__version__",
]
