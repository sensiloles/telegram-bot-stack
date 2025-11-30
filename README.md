# Telegram Bot Stack

[![PyPI version](https://img.shields.io/pypi/v/telegram-bot-stack?color=blue)](https://pypi.org/project/telegram-bot-stack/)
[![Python](https://img.shields.io/pypi/pyversions/telegram-bot-stack)](https://pypi.org/project/telegram-bot-stack/)
[![License: BSL 1.1](https://img.shields.io/badge/license-BSL%201.1-blue.svg)](https://github.com/sensiloles/telegram-bot-stack/blob/main/LICENSE)
[![Tests](https://img.shields.io/github/actions/workflow/status/sensiloles/telegram-bot-stack/unit-tests.yml?branch=main&label=tests)](https://github.com/sensiloles/telegram-bot-stack/actions/workflows/unit-tests.yml)
[![Coverage](https://codecov.io/gh/sensiloles/telegram-bot-stack/branch/main/graph/badge.svg)](https://codecov.io/gh/sensiloles/telegram-bot-stack)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A reusable Python framework for building production-ready Telegram bots with minimal code. **From idea to production in 10 minutes.**

## What is Telegram Bot Stack?

Telegram Bot Stack eliminates boilerplate code and provides everything you need to build Telegram bots. Instead of writing hundreds of lines for user management, admin systems, and storage, you focus on your bot's unique features.

**Build bots in minutes, not hours.**

## Features

### 1. CLI Tools - From Idea to Code in 5 Minutes

Create a complete bot project with one command. Get a fully configured development environment with virtual environment, dependencies, linting, testing, and Git setup.

```bash
# Create new bot project
telegram-bot-stack init my-bot

# Start development with auto-reload
cd my-bot
telegram-bot-stack dev --reload
```

**What you get:**

- Complete project structure
- Virtual environment configured
- All dependencies installed
- Linting and testing setup
- Git initialized
- IDE configuration (VS Code/PyCharm)

**Create from templates:**

```bash
# Choose from 4 templates
telegram-bot-stack new my-bot --template basic    # Minimal bot
telegram-bot-stack new my-bot --template counter  # With state management
telegram-bot-stack new my-bot --template menu     # Interactive menus
telegram-bot-stack new my-bot --template advanced # Production-ready
```

### 2. BotBase Class - Inherit Ready-Made Functionality

The foundation of every bot. Inherit from `BotBase` and get all common patterns out of the box - user management, admin system, storage, and more. Write 70% less code.

```python
from telegram_bot_stack import BotBase
from telegram_bot_stack.storage import JSONStorage
from pathlib import Path

class MyBot(BotBase):
    def get_welcome_message(self) -> str:
        return "Welcome to My Bot!"

# That's it! You get:
# - User registration and tracking
# - Admin system with protection
# - Storage abstraction
# - Rate limiting
# - Command handling
bot = MyBot(
    storage=JSONStorage(Path("./data")),
    bot_name="My Bot"
)
```

**What you get by inheriting BotBase:**

- Automatic user registration on `/start`
- Built-in admin system with multi-admin support
- Storage abstraction (JSON, SQL, Memory)
- Rate limiting decorator
- Command routing and handling
- Hook pattern for easy customization

**Customize with hooks:**

```python
class MyBot(BotBase):
    def get_welcome_message(self) -> str:
        return "Custom welcome message"

    async def on_user_registered(self, user_id: int):
        # Called when new user registers
        print(f"New user: {user_id}")

    async def get_user_status(self, user_id: int) -> str:
        return f"User {user_id} is active"
```

### 3. One-Command Deployment - From Code to Production

Deploy your bot to VPS in one command. Full automation: SSH setup, Docker installation, container management, health checks, backups, and rollback.

```bash
# Initialize deployment (first time)
telegram-bot-stack deploy init

# Deploy to VPS
telegram-bot-stack deploy up
```

**What you get:**

- Automatic SSH setup and authentication
- Docker installation and configuration
- Container management (start, stop, update)
- Health checks and auto-recovery
- Automatic backups before updates
- Rollback to previous versions
- Secrets management (encrypted storage)
- Multi-bot support on one VPS
- Deployment history tracking

**Deployment commands:**

```bash
telegram-bot-stack deploy up      # Deploy/update bot
telegram-bot-stack deploy status  # Check status and health
telegram-bot-stack deploy logs    # View logs
telegram-bot-stack deploy update  # Update bot code
telegram-bot-stack deploy rollback # Rollback to previous version
telegram-bot-stack deploy down    # Stop bot
```

**Production features:**

- Health checks with auto-recovery
- Automatic backups before updates
- Rollback mechanism for failed deployments
- Encrypted secrets management
- Already-running detection
- Multi-bot isolation on one VPS

### 4. Built-in User Management

Automatic user registration and tracking. No need to implement user databases yourself.

```python
class MyBot(BotBase):
    async def on_user_registered(self, user_id: int):
        # Called automatically when new user sends /start
        print(f"New user registered: {user_id}")

    async def get_user_status(self, user_id: int) -> str:
        # Custom status message per user
        return f"User {user_id} is active"
```

**What you get:**

- Automatic user registration on `/start`
- User data persistence
- User tracking and management
- Built-in `/my_id` command

### 5. Admin System

Multi-admin support with protection mechanisms. Assign admins, manage permissions, all built-in.

```python
bot = MyBot(
    storage=JSONStorage(Path("./data")),
    bot_name="My Bot",
    admin_commands=["/list_users", "/add_admin", "/remove_admin"]
)

# Admins can use admin commands
# Last admin is protected from removal
# All admin operations are logged
```

**What you get:**

- Multi-admin support
- Last admin protection
- Admin-only commands
- Built-in `/add_admin` and `/remove_admin` commands

### 6. Storage Abstraction

Choose your storage backend - JSON files, in-memory, or SQL databases. Switch between them with one line.

```python
# JSON Storage (simple, file-based)
from telegram_bot_stack.storage import JSONStorage
storage = JSONStorage(Path("./data"))

# SQL Storage (production, PostgreSQL/SQLite)
from telegram_bot_stack.storage import SQLStorage
storage = SQLStorage(database_url="postgresql://user:pass@localhost/db")

# Memory Storage (testing)
from telegram_bot_stack.storage import MemoryStorage
storage = MemoryStorage()

# Same API for all backends!
bot = MyBot(storage=storage, bot_name="My Bot")
```

**What you get:**

- Unified API across all backends
- Easy switching between storage types
- Production-ready SQL support
- Simple JSON for development

### 7. Rate Limiting

Protect your bot from spam with built-in rate limiting decorator.

```python
from telegram_bot_stack import rate_limit

class MyBot(BotBase):
    @rate_limit(calls=5, period=60)  # 5 calls per minute per user
    async def search_command(self, update, context):
        await update.message.reply_text("Searching...")
```

**What you get:**

- Per-user rate limiting
- Automatic spam protection
- Configurable limits
- Built-in decorator

## Quick Start

### From Idea to Production in 10 Minutes

**Step 1: Create Bot (5 minutes)**

```bash
# Install framework
pip install telegram-bot-stack

# Create new bot project
telegram-bot-stack init my-bot
cd my-bot

# Add your bot token
echo "BOT_TOKEN=your_token_here" > .env

# Run bot locally
telegram-bot-stack dev
```

**Step 2: Customize Your Bot**

```python
# bot.py - Your bot inherits all functionality
from telegram_bot_stack import BotBase
from telegram_bot_stack.storage import JSONStorage
from pathlib import Path

class MyBot(BotBase):
    def get_welcome_message(self) -> str:
        return "Welcome! I'm your custom bot."

# BotBase provides: user management, admin system, storage, rate limiting
```

**Step 3: Deploy to Production (1 command)**

```bash
# Initialize deployment (first time)
telegram-bot-stack deploy init

# Deploy to VPS
telegram-bot-stack deploy up
```

**That's it!** Your bot is now live in production with health checks, backups, and rollback capability.

### Minimal Bot Example

```python
from telegram_bot_stack import BotBase
from telegram_bot_stack.storage import JSONStorage
from pathlib import Path

class EchoBot(BotBase):
    def get_welcome_message(self) -> str:
        return "I echo your messages!"

if __name__ == "__main__":
    import asyncio
    bot = EchoBot(
        storage=JSONStorage(Path("./data")),
        bot_name="Echo Bot"
    )
    asyncio.run(bot.run())
```

**That's it!** You have a fully functional bot with user management, admin system, and storage.

## Example Bots

The framework includes complete example bots:

1. **Echo Bot** - Simplest example, echoes messages
2. **Counter Bot** - Per-user counter with persistence
3. **Reminder Bot** - Scheduled notifications
4. **Menu Bot** - Interactive menus with keyboards
5. **Poll Bot** - Voting system with SQL storage
6. **Quit Smoking Bot** - Complete real-world application

Run any example:

```bash
cd examples/echo_bot
export BOT_TOKEN="your_token"
python3 bot.py
```

---

## Framework Information

### Installation

**From PyPI (Recommended):**

```bash
pip install telegram-bot-stack

# With optional dependencies
pip install telegram-bot-stack[database]  # SQL storage
pip install telegram-bot-stack[all]       # All features
```

**From GitHub:**

```bash
pip install git+https://github.com/sensiloles/telegram-bot-stack.git
```

**From Source (Development):**

```bash
git clone https://github.com/sensiloles/telegram-bot-stack.git
cd telegram-bot-stack
pip install -e ".[dev]"
```

### CLI Commands

**Development:**

```bash
# Initialize new project
telegram-bot-stack init <name> [--with-linting] [--with-testing]

# Create from template
telegram-bot-stack new <name> --template <type>  # basic, counter, menu, advanced

# Development mode with auto-reload
telegram-bot-stack dev [--reload]

# Validate configuration
telegram-bot-stack validate

# Diagnose issues
telegram-bot-stack doctor
```

**Deployment:**

```bash
# Initialize deployment
telegram-bot-stack deploy init

# Deploy to VPS
telegram-bot-stack deploy up

# Check status and health
telegram-bot-stack deploy status

# View logs
telegram-bot-stack deploy logs [--follow]

# Update bot
telegram-bot-stack deploy update

# Rollback to previous version
telegram-bot-stack deploy rollback

# Stop bot
telegram-bot-stack deploy down
```

See [CLI Documentation](docs/cli-specification.md) for complete reference.

### Architecture

The framework follows a layered architecture:

```
telegram_bot_stack/          # Core Framework
├── bot_base.py             # Base class with common patterns
├── user_manager.py         # User management
├── admin_manager.py        # Admin system
├── decorators.py           # Rate limiting
├── storage/                # Storage abstraction
│   ├── json.py            # JSON backend
│   ├── memory.py          # Memory backend
│   └── sql.py             # SQL backend
└── cli/                    # CLI tools
    ├── commands/           # CLI commands
    └── templates/          # Bot templates
```

See [Architecture Documentation](docs/architecture.md) for detailed design.

### Testing

```bash
# Run all tests
python3 -m pytest

# With coverage
python3 -m pytest --cov=telegram_bot_stack --cov-report=html

# Test on all Python versions (3.9-3.12)
make test-all-versions
```

The framework includes comprehensive test coverage (84%) with unit tests, integration tests, and CI/CD integration.

### Requirements

- Python 3.9+ (Python 3.12 recommended)
- Telegram bot token from [@BotFather](https://t.me/BotFather)
- For deployment: VPS with Ubuntu 20.04+ / Debian 11+ / CentOS 8+

### Documentation

- **[Quickstart Guide](docs/quickstart.md)** - Detailed getting started guide
- **[Installation Guide](docs/installation.md)** - Installation options
- **[CLI Specification](docs/cli-specification.md)** - Complete CLI reference
- **[Deployment Guide](docs/deployment_guide.md)** - Production deployment
- **[Architecture Guide](docs/architecture.md)** - Design documentation
- **[Storage Guide](docs/storage_guide.md)** - Storage backends
- **[API Reference](docs/api_reference.md)** - Complete API docs

### Platform Support

- **Linux** - Full support ✅
- **macOS** - Full support (Intel + Apple Silicon) ✅
- **Windows** - Full support (PowerShell, cmd, Git Bash) ✅

See [Windows Setup Guide](docs/windows-setup.md) for Windows-specific instructions.

### Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup and workflow
- Code style and conventions
- Testing requirements
- Pull request process

### License

**Business Source License 1.1 (BSL 1.1)**

- ✅ Free for personal, educational, and small business projects (up to 10 bots)
- ✅ Free for open-source projects
- ✅ Converts to Apache 2.0 on January 1, 2029
- ⚠️ Commercial use beyond limits requires a license

See [LICENSE](LICENSE) for complete terms.

### Links

- **PyPI:** https://pypi.org/project/telegram-bot-stack/
- **GitHub:** https://github.com/sensiloles/telegram-bot-stack
- **Issues:** https://github.com/sensiloles/telegram-bot-stack/issues
- **Documentation:** [docs/README.md](docs/README.md)

---

Built with ❤️ for the Telegram bot community
