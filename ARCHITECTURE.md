# Architecture Overview

## 🏗️ Project Structure

The telegram-bot-stack project follows a clear separation between **reusable framework components** and **bot-specific application logic**.

```
telegram-bot-stack/
├── src/
│   ├── core/              # 🎯 Reusable Framework (future PyPI package)
│   │   ├── bot_base.py    # Base bot class with common patterns
│   │   ├── storage.py     # Storage abstraction layer (JSON)
│   │   ├── user_manager.py    # User registration and management
│   │   └── admin_manager.py   # Admin system with protection
│   │
│   └── quit_smoking/      # 📱 Example Bot Implementation
│       ├── bot.py         # QuitSmokingBot (inherits BotBase)
│       ├── status_manager.py  # Quit smoking tracking logic
│       └── quotes_manager.py  # Motivational quotes
│
├── tests/
│   ├── core/              # Framework component tests
│   └── integration/       # End-to-end tests
│
└── data/                  # Runtime data storage (JSON files)
```

## 🎯 Design Philosophy

### Separation of Concerns

**Framework Layer (`src/core/`):**

- Generic, reusable components
- No bot-specific logic
- Fully tested (100% coverage for storage/managers)
- Ready for extraction into standalone package

**Application Layer (`src/quit_smoking/`):**

- Bot-specific business logic
- Inherits from framework
- Minimal boilerplate code
- Focus on unique features

### Benefits

1. **Code Reusability:** Framework components can be used by any Telegram bot
2. **Maintainability:** Clear boundaries between generic and specific code
3. **Testability:** Framework components are independently testable
4. **Extensibility:** Easy to add new bots using the same framework

## 🧩 Core Components

### 1. BotBase Class

**Purpose:** Base class providing common bot functionality

**Key Features:**

- User and admin management integration
- Common command handlers (`/start`, `/my_id`, admin commands)
- Graceful shutdown handling
- Command registration helpers
- Hook pattern for customization

**Hooks for Customization:**

```python
class BotBase:
    async def on_user_registered(self, user_id: int) -> None:
        """Called when a new user registers. Override for custom logic."""
        pass

    async def get_user_status(self, user_id: int) -> str:
        """Return custom status message. Override for bot-specific status."""
        return "👤 User status: Active"

    def get_welcome_message(self) -> str:
        """Return custom welcome message. Override for bot-specific greeting."""
        return f"Welcome to {self.bot_name}!"
```

**Usage Example:**

```python
from src.core import BotBase, Storage

class MyBot(BotBase):
    def __init__(self):
        storage = Storage("./data")
        super().__init__(
            storage=storage,
            bot_name="My Custom Bot",
            user_commands=["/start", "/help", "/status"],
            admin_commands=["/list_users", "/broadcast"]
        )

    def get_welcome_message(self) -> str:
        return "🎉 Welcome to My Custom Bot!"

    async def get_user_status(self, user_id: int) -> str:
        # Custom status logic
        return f"User {user_id} is active"
```

### 2. Storage Class

**Purpose:** Abstraction layer for data persistence

**Current Implementation:** JSON files
**Future Plans:** SQL, Redis, MongoDB support

**Key Features:**

- Simple key-value interface
- Automatic directory creation
- Error handling and logging
- Type-safe operations

**API:**

```python
class Storage:
    def save(self, key: str, data: Any) -> bool:
        """Save data to storage."""

    def load(self, key: str, default: Any = None) -> Any:
        """Load data from storage with default fallback."""

    def exists(self, key: str) -> bool:
        """Check if key exists in storage."""

    def delete(self, key: str) -> bool:
        """Delete data from storage."""
```

**Usage Example:**

```python
storage = Storage("./data")

# Save data
storage.save("users", [123456, 789012])

# Load data
users = storage.load("users", default=[])

# Check existence
if storage.exists("config"):
    config = storage.load("config")

# Delete data
storage.delete("temp_data")
```

### 3. UserManager Class

**Purpose:** User registration and tracking

**Key Features:**

- Add/remove users
- Check user existence
- Get user count and list
- Automatic persistence via Storage

**API:**

```python
class UserManager:
    def add_user(self, user_id: int) -> bool:
        """Add new user. Returns True if added, False if already exists."""

    def remove_user(self, user_id: int) -> bool:
        """Remove user. Returns True if removed, False if not found."""

    def user_exists(self, user_id: int) -> bool:
        """Check if user is registered."""

    def get_all_users(self) -> List[int]:
        """Get list of all registered users."""

    def get_user_count(self) -> int:
        """Get total number of registered users."""
```

**Usage Example:**

```python
user_manager = UserManager(storage, "bot_users")

# Register new user
if user_manager.add_user(123456):
    print("User registered!")

# Check user
if user_manager.user_exists(123456):
    print("User is registered")

# Get statistics
print(f"Total users: {user_manager.get_user_count()}")
```

### 4. AdminManager Class

**Purpose:** Admin system with protection mechanisms

**Key Features:**

- Add/remove admins
- Last admin protection (cannot remove last admin)
- Admin verification
- Automatic persistence via Storage

**Protection Mechanisms:**

- Cannot remove the last admin (ensures bot always has an admin)
- First user is automatically assigned as admin
- Admins can decline their own admin rights (if not last admin)

**API:**

```python
class AdminManager:
    def add_admin(self, admin_id: int) -> bool:
        """Add new admin. Returns True if added, False if already admin."""

    def remove_admin(self, admin_id: int) -> bool:
        """Remove admin. Returns False if last admin (protection)."""

    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""

    def get_all_admins(self) -> List[int]:
        """Get list of all admins."""

    def get_admin_count(self) -> int:
        """Get total number of admins."""

    def has_admins(self) -> bool:
        """Check if any admins exist."""
```

**Usage Example:**

```python
admin_manager = AdminManager(storage, "bot_admins")

# Add admin
if admin_manager.add_admin(123456):
    print("Admin added!")

# Check admin status
if admin_manager.is_admin(123456):
    print("User is admin")

# Try to remove last admin (will fail)
if not admin_manager.remove_admin(123456):
    print("Cannot remove last admin!")
```

## 🔄 Data Flow

### User Registration Flow

```
User sends /start
    ↓
BotBase.start() handler
    ↓
UserManager.add_user()
    ↓
Storage.save("bot_users")
    ↓
[If first user] AdminManager.add_admin()
    ↓
BotBase.on_user_registered() hook
    ↓
[Subclass custom logic]
    ↓
Welcome message sent
```

### Admin Management Flow

```
Admin sends /add_admin <user_id>
    ↓
BotBase.add_admin() handler
    ↓
Check if requester is admin
    ↓
Check if target user is registered
    ↓
AdminManager.add_admin()
    ↓
Storage.save("bot_admins")
    ↓
Confirmation message sent
```

### Data Persistence Flow

```
Application Operation
    ↓
Manager Method (UserManager/AdminManager)
    ↓
Update in-memory state
    ↓
Storage.save()
    ↓
JSON file written to disk
    ↓
Operation complete
```

## 🎨 Extension Patterns

### Creating a New Bot

**Step 1:** Create bot class inheriting from BotBase

```python
from src.core import BotBase, Storage

class MyCustomBot(BotBase):
    def __init__(self):
        storage = Storage("./data")
        super().__init__(
            storage=storage,
            bot_name="My Bot",
            user_commands=["/start", "/help"],
            admin_commands=["/broadcast"]
        )
```

**Step 2:** Override hooks for custom behavior

```python
    def get_welcome_message(self) -> str:
        return "Welcome to My Custom Bot! 🎉"

    async def get_user_status(self, user_id: int) -> str:
        # Custom status logic
        return "Your custom status here"

    async def on_user_registered(self, user_id: int) -> None:
        # Send welcome email, initialize user data, etc.
        logger.info(f"New user {user_id} registered!")
```

**Step 3:** Add custom commands

```python
    def register_handlers(self, application):
        """Register custom command handlers."""
        super().register_handlers(application)

        # Add custom commands
        application.add_handler(CommandHandler("custom", self.custom_command))

    async def custom_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /custom command."""
        await update.message.reply_text("Custom command response!")
```

### Adding Custom Storage Backend

**Future Enhancement:** Storage abstraction allows for multiple backends

```python
# Example: SQL Storage (future)
class SQLStorage(Storage):
    def save(self, key: str, data: Any) -> bool:
        # SQL implementation
        pass

    def load(self, key: str, default: Any = None) -> Any:
        # SQL implementation
        pass

# Usage
storage = SQLStorage(connection_string="postgresql://...")
bot = MyBot(storage)
```

## 📊 Testing Strategy

### Unit Tests

**Location:** `tests/core/`

**Coverage:**

- Storage: 100% coverage
- UserManager: 100% coverage
- AdminManager: 100% coverage
- BotBase: 68% coverage (async handlers)

**Strategy:**

- Test each component in isolation
- Use temporary directories for storage tests
- Mock external dependencies (Telegram API)

### Integration Tests

**Location:** `tests/integration/`

**Coverage:**

- Full user registration flow
- Admin management flow
- Data persistence across bot restarts
- Edge cases and error handling

**Strategy:**

- Test components working together
- Verify data persistence
- Test bot lifecycle (startup/shutdown)

## 🔒 Security Considerations

### Token Management

- Bot tokens stored in `.env` file (not committed)
- Environment variable validation at startup
- Secure token handling in production

### Admin Protection

- Last admin cannot be removed (system integrity)
- Admin commands require admin verification
- First user automatically becomes admin

### Data Persistence

- JSON files stored in `data/` directory
- Directory permissions managed by system
- No sensitive data in version control

## 🚀 Performance Characteristics

### Startup Time

- Fast initialization (~0.5s on modern hardware)
- Lazy loading of components
- Efficient JSON parsing

### Memory Usage

- Minimal memory footprint
- In-memory user/admin lists (efficient for small-medium bots)
- Storage operations are file-based (no memory bloat)

### Scalability

**Current Implementation:**

- Suitable for bots with <10,000 users
- JSON storage is simple but not optimal for large scale

**Future Enhancements:**

- SQL backend for larger user bases
- Redis for high-performance caching
- Horizontal scaling support

## 🔮 Future Roadmap

### Phase 1: Minimal Viable Framework

- Extract `src/core/` into standalone package
- Publish to PyPI as `telegram-bot-stack`
- Create additional example bots

### Phase 2: Storage Abstraction Layer

- SQL backend support (PostgreSQL, MySQL)
- Redis backend support
- MongoDB backend support
- Unified storage interface

### Phase 3: Advanced Features

- Webhook support (in addition to polling)
- Middleware system for request processing
- Plugin architecture for extensions
- Advanced admin features (roles, permissions)

## 📚 References

- **Master Plan:** `PACKAGE_CONVERSION_PLAN_RU.md`
- **Project Status:** `.github/PROJECT_STATUS.md`
- **Testing Guide:** `README.md` (Testing section)
- **API Documentation:** Inline docstrings in source code

---

**Last Updated:** 2024-11-16
**Version:** Phase 0.3 (Validation)
