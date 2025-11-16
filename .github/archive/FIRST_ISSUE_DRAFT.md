# [Refactor] Phase 0.1: Extract Reusable Components into src/core/

## 🎯 Feature Description

Prepare the quit-smoking-bot codebase for framework extraction by refactoring common components into a dedicated `src/core/` directory. This is **Phase 0.1** of the package conversion plan outlined in `PACKAGE_CONVERSION_PLAN_RU.md`.

**Goal:** Separate reusable framework components from bot-specific business logic to enable future extraction into `telegram-bot-stack` package.

## 💡 Motivation

**Current Problem:**

- Business logic (quit smoking tracking) is mixed with infrastructure code (user management, admin system)
- No clear separation between reusable patterns and bot-specific features
- Difficult to identify which code can be extracted into a framework

**After This Refactor:**

- Clear separation: `src/core/` (reusable) vs `src/quit_smoking/` (bot-specific)
- Code reduction by ~30% through better abstractions
- Foundation for creating universal telegram-bot-stack framework
- Easier testing and maintenance

## 📋 Proposed Implementation

### Current Structure

```
src/
├── bot.py           # All logic in one class
├── users.py         # User management + admins mixed
├── status.py        # Bot-specific logic (quit smoking)
├── quotes.py        # Quotes
└── config.py        # Configuration
```

### New Structure

```
src/
├── core/                      # ✨ NEW: Reusable components (future framework)
│   ├── __init__.py
│   ├── bot_base.py           # Base class with common patterns
│   ├── user_manager.py       # Generic user management
│   ├── admin_manager.py      # Generic admin system
│   └── storage.py            # Storage abstraction (JSON)
│
├── quit_smoking/             # ✨ NEW: Bot-specific logic
│   ├── __init__.py
│   ├── bot.py               # Inherits from bot_base.py
│   ├── status_manager.py    # Quit smoking tracking
│   └── quotes_manager.py    # Motivational quotes
│
└── config.py                # Configuration (stays)
```

### Components to Extract

#### 1. UserManager (`src/core/user_manager.py`)

Extract from `src/users.py`:

- `add_user(user_id)` - Generic user registration
- `remove_user(user_id)` - Generic user removal
- `get_all_users()` - Get user list
- `user_exists(user_id)` - Check if user exists
- JSON file handling for `bot_users.json`

#### 2. AdminManager (`src/core/admin_manager.py`)

Extract from `src/users.py`:

- `add_admin(user_id)` - Add administrator
- `remove_admin(user_id)` - Remove administrator
- `is_admin(user_id)` - Check admin status
- `get_all_admins()` - Get admin list
- JSON file handling for `bot_admins.json`
- Auto-assign first user as admin logic

#### 3. Storage (`src/core/storage.py`)

Create new abstraction layer:

```python
class Storage:
    """Generic storage abstraction for bot data."""

    def save(self, key: str, data: dict) -> bool:
        """Save data to JSON file."""

    def load(self, key: str) -> dict:
        """Load data from JSON file."""

    def exists(self, key: str) -> bool:
        """Check if data exists."""

    def delete(self, key: str) -> bool:
        """Delete data file."""
```

#### 4. BotBase (`src/core/bot_base.py`)

Create base class with common patterns:

- Initialize user_manager, admin_manager, storage
- Built-in command handlers: `/start`, `/status`, `/my_id`
- Built-in admin commands: `/list_users`, `/list_admins`, `/add_admin`, `/remove_admin`
- Graceful shutdown handling
- Signal handling (SIGTERM, SIGINT)
- Hooks for customization:
  - `on_user_registered(user_id)` - Called when new user registers
  - `get_user_status(user_id)` - Override to provide custom status
  - `on_notification_time()` - Override for scheduled notifications

#### 5. QuitSmokingBot (`src/quit_smoking/bot.py`)

Refactor to inherit from BotBase:

```python
from src.core.bot_base import BotBase
from src.quit_smoking.status_manager import StatusManager
from src.quit_smoking.quotes_manager import QuotesManager

class QuitSmokingBot(BotBase):
    """Quit smoking tracking bot - inherits common functionality."""

    def __init__(self, config):
        super().__init__(config)
        self.status_manager = StatusManager(config)
        self.quotes_manager = QuotesManager()

    async def get_user_status(self, user_id):
        """Override to provide quit smoking status."""
        return self.status_manager.get_status()

    async def on_notification_time(self):
        """Override to send motivational quotes."""
        return self.quotes_manager.get_random_quote()
```

## ⚡ Impact

**Users:**

- No visible changes - all features continue working
- Improved reliability through better code structure

**Developers:**

- Clearer code organization
- Easier to understand what's reusable vs bot-specific
- Foundation for framework extraction
- Better testability

**System:**

- **Code reduction**: ~30% less code through abstraction
- Same performance (no architectural changes)
- Easier future maintenance
- Clear path to multi-bot architecture

## 🔗 Related Issues

- Part of `PACKAGE_CONVERSION_PLAN_RU.md` - Phase 0: Refactoring (1-2 weeks)
- Prerequisite for Phase 0.2: Creating tests (#TBD)
- Prerequisite for Phase 1: Minimal Viable Framework (#TBD)

## 📦 Deliverables

**Code:**

- [ ] Create `src/core/` directory structure
- [ ] Implement `UserManager` class
- [ ] Implement `AdminManager` class
- [ ] Implement `Storage` abstraction
- [ ] Implement `BotBase` class
- [ ] Create `src/quit_smoking/` directory
- [ ] Refactor `QuitSmokingBot` to inherit from `BotBase`
- [ ] Move `status.py` → `status_manager.py` into `quit_smoking/`
- [ ] Move `quotes.py` → `quotes_manager.py` into `quit_smoking/`
- [ ] Update all imports throughout the codebase

**Testing:**

- [ ] Verify all existing bot features work
- [ ] Test user registration flow
- [ ] Test admin commands
- [ ] Test status command with new structure
- [ ] Test notifications still work

**Documentation:**

- [ ] Update README.md with new structure explanation
- [ ] Add inline documentation to new classes
- [ ] Update development guide with architecture overview

## ✅ Success Criteria

**Must Have:**

1. ✅ `QuitSmokingBot` successfully inherits from `BotBase`
2. ✅ Code reduced by at least 30%
3. ✅ All existing features work identically
4. ✅ Clear separation: core (reusable) vs quit_smoking (specific)
5. ✅ No breaking changes for users

**Verification:**

```bash
# Bot should start and work normally
python3 src/bot.py

# All commands should work:
/start      # User registration
/status     # Quit smoking status
/my_id      # User ID
/list_users # Admin only
/add_admin  # Admin only
```

## 🎨 Technical Notes

**Backward Compatibility:**

- Keep same data directory structure (`data/`)
- Keep same JSON file formats (`bot_users.json`, `bot_admins.json`)
- No changes to `pyproject.toml` dependencies
- Same Docker configuration

**Best Practices:**

- Follow existing code style (ruff, mypy)
- Use type hints for all new code
- Keep English comments and docstrings
- Maintain existing security patterns (non-root Docker, no secrets in git)

**Testing Strategy:**

- Manual testing first (ensure nothing breaks)
- Automated tests in Phase 0.2
- Keep testing simple for MVP

## 📚 References

- **Plan Document**: `PACKAGE_CONVERSION_PLAN_RU.md` (lines 761-848)
- **Current Code**: `src/bot.py`, `src/users.py`, `src/status.py`
- **Target Architecture**: See plan document section "Целевая архитектура"

---

**Priority:** High
**Component:** refactor, component:bot, component:cli
**Estimated Time:** 3-5 days
**Complexity:** Medium-Complex

**Note:** This is a preparatory refactor. No new features are added, but code organization significantly improves. This refactor is required before we can extract components into `telegram-bot-stack` framework.
