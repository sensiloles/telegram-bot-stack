# API Reference

Complete API documentation for `telegram-bot-stack` framework.

## Table of Contents

- [BotBase](#botbase)
- [Storage](#storage)
  - [StorageBackend](#storagebackend)
  - [JSONStorage](#jsonstorage)
  - [MemoryStorage](#memorystorage)
  - [create_storage()](#create_storage)
- [UserManager](#usermanager)
- [AdminManager](#adminmanager)

---

## BotBase

Base class for all Telegram bots. Provides user/admin management, command handling, and extensibility hooks.

### Constructor

```python
BotBase(
    storage: StorageBackend,
    bot_name: str = "Bot",
    user_commands: list[str] | None = None,
    admin_commands: list[str] | None = None
)
```

**Parameters:**

- `storage` (StorageBackend): Storage backend instance (JSONStorage or MemoryStorage)
- `bot_name` (str): Name of your bot (default: "Bot")
- `user_commands` (list[str] | None): List of user commands (default: `["/start", "/my_id"]`)
- `admin_commands` (list[str] | None): List of admin commands (default: includes user commands + admin-specific commands)

**Example:**

```python
from telegram_bot_stack import BotBase
from telegram_bot_stack.storage import JSONStorage

storage = JSONStorage(base_dir="data")
bot = BotBase(storage=storage, bot_name="My Bot")
```

### Methods

#### `register_handlers()`

Register command handlers with the Telegram application. Override to add custom handlers.

```python
def register_handlers(self) -> None:
    """Register all command handlers."""
    super().register_handlers()  # Register base handlers
    # Add your custom handlers here
```

#### `set_bot_commands(application)`

Set bot commands in Telegram UI. Called automatically during bot startup.

```python
async def set_bot_commands(self, application: Application) -> None:
    """Set bot commands visible in Telegram UI."""
```

### Hooks (Override These)

#### `get_welcome_message()`

Return custom welcome message shown when users send `/start`.

```python
def get_welcome_message(self) -> str:
    """Return welcome message for new users."""
    return "Welcome to My Bot!"
```

#### `get_user_status(user_id)`

Return custom status information for a user (shown in `/my_id` command).

```python
async def get_user_status(self, user_id: int) -> str:
    """Return status information for user."""
    return f"User {user_id} is active"
```

#### `on_user_registered(user_id)`

Called when a new user registers via `/start`.

```python
async def on_user_registered(self, user_id: int) -> None:
    """Called when new user registers."""
    logger.info(f"New user: {user_id}")
```

### Built-in Commands

#### User Commands

- `/start` - Register user and show welcome message
- `/my_id` - Show user ID and status

#### Admin Commands

- `/list_users` - List all registered users (admin only)
- `/list_admins` - List all administrators
- `/add_admin <user_id>` - Add new administrator (admin only)
- `/remove_admin <user_id>` - Remove administrator (admin only)
- `/decline_admin` - Decline own admin status

### Properties

- `application` (Application): python-telegram-bot Application instance
- `storage` (StorageBackend): Storage backend instance
- `user_manager` (UserManager): User management instance
- `admin_manager` (AdminManager): Admin management instance
- `bot_name` (str): Bot name
- `is_running` (bool): Whether bot is currently running

---

## Storage

Storage abstraction layer providing unified interface for different backends.

### StorageBackend

Abstract base class defining storage interface.

#### Methods

```python
from abc import ABC, abstractmethod
from typing import Any

class StorageBackend(ABC):
    @abstractmethod
    def save(self, key: str, data: Any) -> bool:
        """Save data under key. Returns True on success."""
        pass

    @abstractmethod
    def load(self, key: str, default: Any = None) -> Any:
        """Load data for key. Returns default if key doesn't exist."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key. Returns True if deleted, False if not found."""
        pass
```

### JSONStorage

File-based JSON storage backend. Data persists across bot restarts.

#### Constructor

```python
JSONStorage(base_dir: Path | str = "data")
```

**Parameters:**

- `base_dir` (Path | str): Directory for storing JSON files (default: "data")

**Example:**

```python
from telegram_bot_stack.storage import JSONStorage
from pathlib import Path

# Default data directory
storage = JSONStorage()

# Custom directory
storage = JSONStorage(base_dir="bot_data")

# Using Path object
storage = JSONStorage(base_dir=Path("data"))
```

#### Methods

All methods inherited from [StorageBackend](#storagebackend).

**Example Usage:**

```python
# Save data
storage.save("users", {"user1": {"name": "John"}})

# Load data
users = storage.load("users", default={})

# Check existence
if storage.exists("users"):
    print("Users data exists")

# Delete data
storage.delete("old_data")
```

### MemoryStorage

In-memory storage backend. Fast but data is lost when bot stops. Ideal for testing.

#### Constructor

```python
MemoryStorage()
```

**Example:**

```python
from telegram_bot_stack.storage import MemoryStorage

# Create in-memory storage
storage = MemoryStorage()

# Use same API as JSONStorage
storage.save("test", {"data": "value"})
data = storage.load("test")
```

#### Methods

All methods inherited from [StorageBackend](#storagebackend).

**Use Cases:**

- Unit testing (no file I/O overhead)
- Temporary data that doesn't need persistence
- Development and debugging

### create_storage()

Factory function to create storage backend instances.

```python
create_storage(backend: str = "json", **kwargs) -> StorageBackend
```

**Parameters:**

- `backend` (str): Backend type - "json" or "memory" (default: "json")
- `**kwargs`: Backend-specific options
  - For JSONStorage: `base_dir` (directory path)
  - For MemoryStorage: no options

**Returns:** StorageBackend instance

**Example:**

```python
from telegram_bot_stack.storage import create_storage

# JSON storage
storage = create_storage("json", base_dir="data")

# Memory storage
storage = create_storage("memory")

# Default (JSON)
storage = create_storage(base_dir="data")
```

---

## UserManager

Manages bot users - registration, removal, and queries.

### Constructor

```python
UserManager(storage: StorageBackend, storage_key: str = "bot_users")
```

**Parameters:**

- `storage` (StorageBackend): Storage backend instance
- `storage_key` (str): Key for storing user data (default: "bot_users")

**Example:**

```python
from telegram_bot_stack import UserManager
from telegram_bot_stack.storage import JSONStorage

storage = JSONStorage()
user_manager = UserManager(storage)
```

### Methods

#### `add_user(user_id, user_data)`

Add new user to the system.

```python
def add_user(self, user_id: int, user_data: dict) -> bool:
    """Add user with data. Returns True on success."""
```

**Example:**

```python
user_manager.add_user(
    user_id=123456,
    user_data={"username": "john_doe", "first_name": "John"}
)
```

#### `remove_user(user_id)`

Remove user from the system.

```python
def remove_user(self, user_id: int) -> bool:
    """Remove user. Returns True if removed, False if not found."""
```

#### `user_exists(user_id)`

Check if user is registered.

```python
def user_exists(self, user_id: int) -> bool:
    """Check if user exists."""
```

#### `get_all_users()`

Get all registered users.

```python
def get_all_users(self) -> dict[str, dict]:
    """Get all users as dict. Returns copy, modifications don't affect storage."""
```

**Example:**

```python
users = user_manager.get_all_users()
for user_id, user_data in users.items():
    print(f"User {user_id}: {user_data}")
```

#### `get_user_count()`

Get total number of registered users.

```python
def get_user_count(self) -> int:
    """Get total user count."""
```

---

## AdminManager

Manages bot administrators with protection mechanisms.

### Constructor

```python
AdminManager(storage: StorageBackend, storage_key: str = "bot_admins")
```

**Parameters:**

- `storage` (StorageBackend): Storage backend instance
- `storage_key` (str): Key for storing admin data (default: "bot_admins")

**Example:**

```python
from telegram_bot_stack import AdminManager
from telegram_bot_stack.storage import JSONStorage

storage = JSONStorage()
admin_manager = AdminManager(storage)
```

### Methods

#### `add_admin(user_id, user_data)`

Add new administrator.

```python
def add_admin(self, user_id: int, user_data: dict) -> bool:
    """Add admin with data. Returns True on success."""
```

**Example:**

```python
admin_manager.add_admin(
    user_id=123456,
    user_data={"username": "admin_user"}
)
```

#### `remove_admin(user_id)`

Remove administrator. **Cannot remove last admin** (protection mechanism).

```python
def remove_admin(self, user_id: int) -> bool:
    """
    Remove admin. Returns True if removed.
    Returns False if user is last admin (cannot remove last admin).
    """
```

#### `is_admin(user_id)`

Check if user is an administrator.

```python
def is_admin(self, user_id: int) -> bool:
    """Check if user is admin."""
```

#### `get_all_admins()`

Get all administrators.

```python
def get_all_admins(self) -> dict[str, dict]:
    """Get all admins as dict. Returns copy."""
```

#### `get_admin_count()`

Get total number of administrators.

```python
def get_admin_count(self) -> int:
    """Get admin count."""
```

#### `has_admins()`

Check if any administrators exist.

```python
def has_admins(self) -> bool:
    """Check if system has any admins."""
```

### Admin Protection

- **First user auto-admin:** First registered user automatically becomes admin
- **Last admin protection:** Cannot remove the last administrator
- **Ensures:** Bot always has at least one admin for management

---

## Type Hints

All public APIs include type hints for better IDE support:

```python
from telegram_bot_stack import BotBase, UserManager, AdminManager
from telegram_bot_stack.storage import (
    StorageBackend,
    JSONStorage,
    MemoryStorage,
    create_storage,
)
from typing import Any

# Type hints work automatically
storage: StorageBackend = create_storage("json")
users: dict[str, dict] = user_manager.get_all_users()
is_admin: bool = admin_manager.is_admin(123456)
```

---

## Advanced Usage

### Custom Storage Backend

Implement `StorageBackend` for custom storage (SQL, Redis, etc.):

```python
from telegram_bot_stack.storage import StorageBackend
from typing import Any

class RedisStorage(StorageBackend):
    """Redis storage implementation."""

    def __init__(self, redis_client):
        self.redis = redis_client

    def save(self, key: str, data: Any) -> bool:
        """Save to Redis."""
        import json
        try:
            self.redis.set(key, json.dumps(data))
            return True
        except Exception:
            return False

    def load(self, key: str, default: Any = None) -> Any:
        """Load from Redis."""
        import json
        value = self.redis.get(key)
        return json.loads(value) if value else default

    def exists(self, key: str) -> bool:
        """Check existence in Redis."""
        return self.redis.exists(key)

    def delete(self, key: str) -> bool:
        """Delete from Redis."""
        return self.redis.delete(key) > 0
```

### Multiple Storage Keys

Use different storage keys for different data types:

```python
from telegram_bot_stack import UserManager, AdminManager
from telegram_bot_stack.storage import JSONStorage

storage = JSONStorage()

# Separate managers with different keys
user_manager = UserManager(storage, storage_key="users")
admin_manager = AdminManager(storage, storage_key="admins")

# Custom data with custom keys
storage.save("bot_settings", {"theme": "dark"})
storage.save("analytics", {"user_count": 100})
```

---

## See Also

- [Quick Start Guide](quickstart.md) - Get started in minutes
- [Migration Guide](migration_guide.md) - Upgrade from older versions
- [Architecture](../ARCHITECTURE.md) - Design patterns and principles
- [Examples](../examples/) - Complete example bots

## Support

- 📝 [GitHub Issues](https://github.com/sensiloles/telegram-bot-stack/issues)
- 📚 [Documentation](../README.md)
- 💬 GitHub Discussions
