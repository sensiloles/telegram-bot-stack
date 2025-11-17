# Migration Guide

Guide for migrating to `telegram-bot-stack` v0.1.0 from previous versions.

## Table of Contents

- [From Phase 0 (src/core)](#from-phase-0-srccore)
- [Package Structure Changes](#package-structure-changes)
- [Import Changes](#import-changes)
- [Storage Changes](#storage-changes)
- [Breaking Changes](#breaking-changes)
- [Migration Steps](#migration-steps)

---

## From Phase 0 (src/core)

If you were using the framework from `src/core/` directory (Phase 0), follow this guide to migrate to the new `telegram-bot-stack` package.

### What Changed?

**Phase 0 (Old):**

```
src/
└── core/
    ├── bot_base.py
    ├── storage.py          # Single storage class
    ├── user_manager.py
    └── admin_manager.py
```

**Phase 1 (New):**

```
telegram_bot_stack/         # Installable package
├── bot_base.py
├── user_manager.py
├── admin_manager.py
└── storage/                # Storage abstraction layer
    ├── base.py            # StorageBackend interface
    ├── json.py            # JSONStorage
    └── memory.py          # MemoryStorage
```

---

## Package Structure Changes

### Old Structure (Phase 0)

```python
# Old imports
from src.core.bot_base import BotBase
from src.core.storage import Storage
from src.core.user_manager import UserManager
from src.core.admin_manager import AdminManager
```

### New Structure (Phase 1)

```python
# New imports
from telegram_bot_stack import BotBase, UserManager, AdminManager
from telegram_bot_stack.storage import JSONStorage, MemoryStorage, create_storage
```

---

## Import Changes

### Bot Base Class

**Before:**

```python
from src.core.bot_base import BotBase
```

**After:**

```python
from telegram_bot_stack import BotBase
```

### Storage

**Before:**

```python
from src.core.storage import Storage

storage = Storage(base_dir="data")
```

**After:**

```python
from telegram_bot_stack.storage import JSONStorage

storage = JSONStorage(base_dir="data")
```

### User and Admin Managers

**Before:**

```python
from src.core.user_manager import UserManager
from src.core.admin_manager import AdminManager
```

**After:**

```python
from telegram_bot_stack import UserManager, AdminManager
```

---

## Storage Changes

The storage system has been refactored into a storage abstraction layer.

### Storage Class Renamed

The `Storage` class has been renamed to `JSONStorage` to reflect its implementation.

**Before:**

```python
from src.core.storage import Storage

storage = Storage(base_dir="data")
```

**After:**

```python
from telegram_bot_stack.storage import JSONStorage

storage = JSONStorage(base_dir="data")
```

### Storage Interface

All storage backends now implement the `StorageBackend` interface:

```python
from telegram_bot_stack.storage import StorageBackend

class StorageBackend(ABC):
    def save(self, key: str, data: Any) -> bool: ...
    def load(self, key: str, default: Any = None) -> Any: ...
    def exists(self, key: str) -> bool: ...
    def delete(self, key: str) -> bool: ...
```

### New Storage Backends

**MemoryStorage** - New in Phase 1:

```python
from telegram_bot_stack.storage import MemoryStorage

# In-memory storage (for testing)
storage = MemoryStorage()
```

**Factory Function** - New in Phase 1:

```python
from telegram_bot_stack.storage import create_storage

# Create JSON storage
storage = create_storage("json", base_dir="data")

# Create Memory storage
storage = create_storage("memory")
```

### Backward Compatibility

For backward compatibility, you can still use `Storage` as an alias:

```python
from telegram_bot_stack.storage import Storage

# Storage is an alias for JSONStorage
storage = Storage(base_dir="data")
```

⚠️ **Deprecation Notice:** The `Storage` alias may be removed in future versions. Use `JSONStorage` explicitly.

---

## Breaking Changes

### 1. Package Installation Required

**Before:** Framework code was in `src/core/` directory
**After:** Install as package: `pip install -e .`

**Migration:**

```bash
cd telegram-bot-stack
pip install -e .
```

### 2. Import Paths Changed

**Before:**

```python
from src.core.bot_base import BotBase
```

**After:**

```python
from telegram_bot_stack import BotBase
```

**Migration:** Update all imports to new paths (see [Import Changes](#import-changes))

### 3. Storage Class Renamed

**Before:**

```python
from src.core.storage import Storage
```

**After:**

```python
from telegram_bot_stack.storage import JSONStorage
# or use backward-compatible alias
from telegram_bot_stack.storage import Storage  # Deprecated
```

### 4. Test Configuration

**Before:** Tests measured coverage for `src/core`

```bash
pytest --cov=src/core
```

**After:** Tests measure coverage for `telegram_bot_stack`

```bash
pytest --cov=telegram_bot_stack
```

---

## Migration Steps

### Step 1: Install New Package

```bash
cd telegram-bot-stack
pip install -e .
```

### Step 2: Update Imports

Replace all `src.core.*` imports with `telegram_bot_stack.*`:

**Old bot code:**

```python
from src.core.bot_base import BotBase
from src.core.storage import Storage
from src.core.user_manager import UserManager
from src.core.admin_manager import AdminManager

storage = Storage(base_dir="data")
```

**New bot code:**

```python
from telegram_bot_stack import BotBase, UserManager, AdminManager
from telegram_bot_stack.storage import JSONStorage

storage = JSONStorage(base_dir="data")
```

### Step 3: Update Storage Usage (Optional)

Consider using the new storage abstraction:

```python
# Option 1: Use JSONStorage directly
from telegram_bot_stack.storage import JSONStorage
storage = JSONStorage(base_dir="data")

# Option 2: Use factory function
from telegram_bot_stack.storage import create_storage
storage = create_storage("json", base_dir="data")

# Option 3: Use MemoryStorage for testing
from telegram_bot_stack.storage import MemoryStorage
storage = MemoryStorage()
```

### Step 4: Update Tests

**Before:**

```python
# conftest.py
from src.core.storage import Storage

@pytest.fixture
def temp_storage(tmp_path):
    return Storage(tmp_path)
```

**After:**

```python
# conftest.py
from telegram_bot_stack.storage import MemoryStorage

@pytest.fixture
def temp_storage():
    # Use MemoryStorage for faster tests
    return MemoryStorage()
```

### Step 5: Test Your Bot

```bash
# Run tests
pytest

# Run your bot
python your_bot.py
```

---

## Example Migration

### Before (Phase 0)

```python
"""Old bot using src/core."""

from pathlib import Path
from src.core.bot_base import BotBase
from src.core.storage import Storage

class MyBot(BotBase):
    def get_welcome_message(self) -> str:
        return "Welcome!"

def main():
    storage = Storage(base_dir=Path("data"))
    bot = MyBot(storage=storage, bot_name="My Bot")
    # ... rest of setup

if __name__ == "__main__":
    main()
```

### After (Phase 1)

```python
"""New bot using telegram-bot-stack package."""

from pathlib import Path
from telegram_bot_stack import BotBase
from telegram_bot_stack.storage import JSONStorage

class MyBot(BotBase):
    def get_welcome_message(self) -> str:
        return "Welcome!"

def main():
    storage = JSONStorage(base_dir=Path("data"))
    bot = MyBot(storage=storage, bot_name="My Bot")
    # ... rest of setup

if __name__ == "__main__":
    main()
```

### Changes Summary

1. ✅ Imports updated to `telegram_bot_stack`
2. ✅ `Storage` → `JSONStorage`
3. ✅ Package installed via pip
4. ✅ No changes to bot logic or behavior

---

## Data Migration

### Storage Data Compatibility

✅ **Good News:** Storage format hasn't changed!

Your existing JSON data files remain compatible. No data migration needed.

**Location:** `data/` directory

- `bot_users.json` - User data (unchanged)
- `bot_admins.json` - Admin data (unchanged)
- Any custom data files (unchanged)

**Migration:** None required - your data continues to work!

---

## Testing Migration

### Test Fixtures

**Before:**

```python
@pytest.fixture
def temp_storage(tmp_path):
    from src.core.storage import Storage
    return Storage(tmp_path)
```

**After (Recommended):**

```python
@pytest.fixture
def temp_storage():
    from telegram_bot_stack.storage import MemoryStorage
    # Faster tests with in-memory storage
    return MemoryStorage()
```

**After (File-based tests):**

```python
@pytest.fixture
def temp_storage(tmp_path):
    from telegram_bot_stack.storage import JSONStorage
    return JSONStorage(tmp_path)
```

### Coverage Configuration

Update `pyproject.toml`:

**Before:**

```toml
[tool.pytest.ini_options]
addopts = ["--cov=src/core"]
```

**After:**

```toml
[tool.pytest.ini_options]
addopts = ["--cov=telegram_bot_stack"]
```

---

## New Features in Phase 1

### Storage Abstraction Layer

Choose the right storage for your needs:

```python
# Production: JSONStorage (persistent)
from telegram_bot_stack.storage import JSONStorage
storage = JSONStorage(base_dir="data")

# Testing: MemoryStorage (fast)
from telegram_bot_stack.storage import MemoryStorage
storage = MemoryStorage()

# Factory pattern
from telegram_bot_stack.storage import create_storage
storage = create_storage("json", base_dir="data")
```

### Example Bots

Three complete examples now included:

- `examples/echo_bot/` - Simplest bot
- `examples/counter_bot/` - State management
- `examples/quit_smoking_bot/` - Real-world app

### Comprehensive Documentation

- [Quick Start Guide](quickstart.md)
- [API Reference](api_reference.md)
- [Migration Guide](migration_guide.md) (this document)

---

## Troubleshooting

### Issue: "No module named 'telegram_bot_stack'"

**Cause:** Package not installed

**Solution:**

```bash
pip install -e .
```

### Issue: "No module named 'src.core'"

**Cause:** Old imports still in code

**Solution:** Update imports to `telegram_bot_stack.*` (see [Import Changes](#import-changes))

### Issue: Tests failing with coverage errors

**Cause:** Coverage measured for wrong package

**Solution:** Update coverage configuration:

```bash
pytest --cov=telegram_bot_stack
```

### Issue: Storage data not found

**Cause:** Storage path changed or incorrect

**Solution:** Check storage path:

```python
storage = JSONStorage(base_dir="data")  # Same as before
```

---

## Getting Help

If you encounter issues during migration:

1. 📝 Check [GitHub Issues](https://github.com/sensiloles/telegram-bot-stack/issues)
2. 📚 Read [API Reference](api_reference.md)
3. 💡 See [Examples](../examples/)
4. 💬 Ask in GitHub Discussions

---

## Future Migrations

### Staying Updated

When new versions are released:

1. Check `CHANGELOG.md` for breaking changes
2. Read migration guides for your version
3. Update dependencies: `pip install --upgrade telegram-bot-stack`
4. Test your bot after upgrading

### Deprecation Policy

- Deprecated features will be marked with warnings
- Deprecated features maintained for at least one minor version
- Breaking changes only in major versions (1.0, 2.0, etc.)

---

## Summary

✅ **Quick Migration Checklist:**

- [ ] Install package: `pip install -e .`
- [ ] Update imports: `src.core` → `telegram_bot_stack`
- [ ] Rename Storage: `Storage` → `JSONStorage`
- [ ] Update tests: `--cov=telegram_bot_stack`
- [ ] Test your bot: `python your_bot.py`
- [ ] Run test suite: `pytest`

**Estimated time:** 5-10 minutes for simple bots

**Data migration:** None required ✅

**Backward compatibility:** Excellent ✅

---

Happy migrating! 🚀
