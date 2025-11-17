# Telegram Bot Stack

A reusable Python framework for building production-ready Telegram bots with minimal code. Includes user management, admin system, storage abstraction, and comprehensive testing infrastructure.

> 🎯 **Example:** The `src/quit_smoking/` directory contains a complete quit-smoking tracking bot built with this framework.

## 📍 Quick Navigation (For Agents)

**New to this project?**

1. 🎯 **Current Status:** [`.github/PROJECT_STATUS.md`](.github/PROJECT_STATUS.md) - Phase, progress, what to do next
2. 📖 **Master Plan:** [`PACKAGE_CONVERSION_PLAN_RU.md`](PACKAGE_CONVERSION_PLAN_RU.md) (lines 761-1928) - Complete roadmap
3. 🔧 **Workflow Rules:** [`.cursorrules`](.cursorrules) - Git, testing, conventions

**Quick Links:**

- [Features](#-features) - What this bot does
- [Quick Start](#-quick-start) - Setup in 3 steps
- [Testing](#-testing) - Run tests, coverage
- [Architecture](#-architecture-overview) - Code structure
- [Development](#-development) - Dev environment

**Check Status:**

```bash
# Current phase and open issues
cat .github/PROJECT_STATUS.md

# List open issues
python3 .github/workflows/scripts/read_issues.py --list --state open
```

---

## 🤖 New: Cloud Agent Issue Automation

**Automated Issue Management** - Create, label, and break down GitHub Issues automatically!

🎤 **Voice/Text Commands** • 🏷️ **Smart Labeling** • 📋 **Task Breakdown** • ✅ **Acceptance Criteria** • 🔍 **Context Analysis**

👉 **[Learn More about Cloud Agent](.github/docs/cloud-agent/README.md)**

---

## 🌟 Features

### 🎯 Core Framework Features

- 🏗️ **BotBase Class**: Inherit and customize - 70% less boilerplate code
- 👥 **User Management**: Built-in user registration and tracking
- 🔐 **Admin System**: Multi-admin support with protection mechanisms
- 💾 **Storage Abstraction**: Multiple backends (JSON, Memory) with unified API
- 📅 **Scheduler Integration**: APScheduler for periodic tasks
- 🎯 **Hook Pattern**: Override methods for custom behavior
- 🧪 **Comprehensive Tests**: 131 tests with 80% coverage
- 📦 **PyPI Package**: Install via `pip install telegram-bot-stack` (coming soon)

### 🛡️ Production-Grade Infrastructure

- 🐳 **Docker-Ready**: Advanced production containerization with entrypoint
- ⚡ **Optimized Caching**: Docker layer caching for faster rebuilds
- 🧹 **Auto Image Cleanup**: Automatic removal of dangling Docker images for this project only
- 🔧 **Unified Management**: Single-command interface via `manager.py`
- 📊 **Health Monitoring**: Real-time health checks and continuous monitoring
- 🔄 **Log Management**: Automatic log rotation and archiving
- 🔄 **Auto-Recovery**: Process management and graceful restarts
- 🛠️ **Environment Setup**: Automated initialization and permission management
- 📦 **Modern Packaging**: pyproject.toml-based dependency management

## 🚀 Quick Start

### Installation

#### Option 1: Install from GitHub (Recommended)

```bash
# Install latest version directly from GitHub
pip install git+https://github.com/sensiloles/telegram-bot-stack.git

# Install specific version
pip install git+https://github.com/sensiloles/telegram-bot-stack.git@v0.1.0
```

#### Option 2: Install from Source

```bash
# Clone and install in development mode
git clone https://github.com/sensiloles/telegram-bot-stack.git
cd telegram-bot-stack
pip install -e .
```

#### Option 3: PyPI (Coming Soon)

```bash
# Will be available after public release
pip install telegram-bot-stack
```

> 📝 **Note:** For private/internal use, see [Private Installation Guide](docs/private_installation.md)

### Option 1: Run Example Bots

```bash
# Set your bot token
export TELEGRAM_BOT_TOKEN="your_token_here"

# Run Echo Bot (simplest example)
cd examples/echo_bot
python3 bot.py

# Run Counter Bot (state management example)
cd examples/counter_bot
python3 bot.py

# Run Quit Smoking Bot (real-world example)
cd examples/quit_smoking_bot
python3 bot.py
```

### Option 2: Build Your Own Bot

```python
# my_bot.py
from telegram_bot_stack import BotBase
from telegram_bot_stack.storage import JSONStorage
from pathlib import Path

class MyBot(BotBase):
    """Your custom bot - override hooks for custom behavior."""

    def get_welcome_message(self) -> str:
        """Override to provide custom welcome message."""
        return "Welcome to My Custom Bot!"

    async def get_user_status(self, user_id: int) -> str:
        """Override to provide custom status."""
        return "Your custom status message!"

    async def on_user_registered(self, user_id: int):
        """Called when new user registers."""
        print(f"New user: {user_id}")

if __name__ == "__main__":
    import asyncio
    bot = MyBot(
        storage=Storage(Path("./data")),
        bot_name="My Bot",
        user_commands=["/start", "/status"],
        admin_commands=["/list_users", "/add_admin"]
    )
    asyncio.run(bot.run())
```

**That's it!** 70-80% less code than building from scratch.

## 👨‍💻 Development

For development setup, VS Code configuration, and detailed build instructions, see:

**📚 [Development Guide](DEVELOPMENT.md)** - Complete development environment setup, IDE configuration, and troubleshooting.

## 🧪 Testing

The project includes comprehensive test coverage for all core components with 80%+ code coverage.

### Running Tests

```bash
# Run all tests with coverage
python3 -m pytest

# Run specific test file
python3 -m pytest tests/core/test_storage.py

# Run with verbose output
python3 -m pytest -v

# Run with coverage report
python3 -m pytest --cov=telegram_bot_stack --cov-report=html
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures
├── core/                          # Core component tests
│   ├── test_storage.py           # Storage abstraction tests (100+ tests)
│   ├── test_user_manager.py      # User management tests (100% coverage)
│   ├── test_admin_manager.py     # Admin management tests (100% coverage)
│   └── test_bot_base.py          # Bot base class tests (68% coverage)
└── integration/                   # Integration tests
    └── test_full_flow.py         # End-to-end workflow tests
```

### Coverage Report

| Component             | Coverage | Status                     |
| --------------------- | -------- | -------------------------- |
| `storage/json.py`     | 83%      | ✅ Excellent               |
| `storage/memory.py`   | 80%      | ✅ Excellent               |
| `storage/__init__.py` | 100%     | ✅ Excellent               |
| `user_manager.py`     | 100%     | ✅ Excellent               |
| `admin_manager.py`    | 100%     | ✅ Excellent               |
| `bot_base.py`         | 68%      | ⚠️ Good                    |
| **Overall Package**   | **80%**  | ✅ **Meets 80% threshold** |

### Test Features

- ✅ **131 tests** covering core functionality
- ✅ **Async test support** with pytest-asyncio
- ✅ **Integration tests** for complete workflows
- ✅ **Error handling tests** for robustness
- ✅ **Fixtures** for test isolation and reusability
- ✅ **Mock support** for Telegram API testing
- ✅ **CI/CD integration** with GitHub Actions

### Continuous Integration

Tests run automatically on every push and pull request via GitHub Actions:

- ✅ Tests on Python 3.9, 3.10, 3.11, 3.12
- ✅ Code linting with Ruff
- ✅ Type checking with mypy
- ✅ Coverage reporting
- ✅ Automated coverage threshold checks

See [`.github/workflows/tests.yml`](.github/workflows/tests.yml) for CI/CD configuration.

### Adding New Tests

1. Create test file in appropriate directory (`tests/core/` or `tests/integration/`)
2. Import fixtures from `conftest.py`
3. Use descriptive test names: `test_<feature>_<scenario>`
4. Run tests locally before committing
5. Ensure coverage remains above 80%

## 🏗️ Architecture Overview

> 📖 **Detailed Architecture Documentation:** See [`ARCHITECTURE.md`](ARCHITECTURE.md) for comprehensive design documentation, data flow diagrams, and extension patterns.

### Package Structure

The framework is now available as a standalone package `telegram-bot-stack`:

```
telegram-bot-stack/
├── telegram_bot_stack/          # 📦 PyPI Package (installable)
│   ├── __init__.py             # Public API exports
│   ├── bot_base.py             # Base class with common patterns
│   ├── user_manager.py         # Generic user management
│   ├── admin_manager.py        # Generic admin system
│   └── storage/                # Storage abstraction layer
│       ├── base.py             # StorageBackend interface
│       ├── json.py             # JSONStorage (file-based)
│       └── memory.py           # MemoryStorage (for testing)
│
├── examples/                    # 📚 Example Bots
│   ├── echo_bot/               # Simplest example (5-10 lines)
│   ├── counter_bot/            # State management example
│   └── quit_smoking_bot/       # Real-world application
│
├── tests/                       # 🧪 Test Suite
│   ├── core/                   # Unit tests (131 tests)
│   └── integration/            # End-to-end tests
│
└── src/                         # 🎯 Legacy Application Layer
    ├── core/                   # (To be removed - replaced by package)
    └── quit_smoking/           # Original bot implementation
```

### Key Components

**BotBase** (`telegram_bot_stack.bot_base.BotBase`)

- Common Telegram bot patterns (user/admin management, commands)
- Command registration and routing
- Graceful shutdown handling
- **Hooks for customization:**
  - `on_user_registered(user_id)` - Called when new user registers
  - `get_user_status(user_id)` - Override to provide custom status
  - `get_welcome_message()` - Override for custom welcome message

**Storage Abstraction** (`telegram_bot_stack.storage`)

- **StorageBackend interface** - Unified API for all storage backends
- **JSONStorage** - File-based storage (production ready)
- **MemoryStorage** - In-memory storage (fast, for testing)
- **Factory function** - `create_storage("json", base_dir="data")`

**UserManager** (`telegram_bot_stack.user_manager.UserManager`)

- User registration and removal
- User existence checks
- Data persistence via Storage
- **100% test coverage**

**AdminManager** (`telegram_bot_stack.admin_manager.AdminManager`)

- Admin assignment and removal
- Auto-assign first user as admin
- Last admin protection (can't remove last admin)
- **100% test coverage**

### Example Bots

**Echo Bot** (`examples/echo_bot/`) - Simplest Example

- 5-10 lines of code
- Echoes back user messages
- Demonstrates minimal framework usage

**Counter Bot** (`examples/counter_bot/`) - State Management

- Per-user counter with persistence
- Demonstrates storage API usage
- Custom commands (increment, decrement, reset)

**Quit Smoking Bot** (`examples/quit_smoking_bot/`) - Real-World Example

- Complete tracking application
- Custom business logic (prize fund calculation)
- Integration with custom managers
- Demonstrates hook customization

### Design Principles

1. **Separation of Concerns**: Framework (telegram_bot_stack) vs Application (examples)
2. **Inheritance over Composition**: BotBase provides foundation
3. **Dependency Injection**: Storage backend injected into components
4. **Hook Pattern**: Subclasses override hooks for customization
5. **Single Responsibility**: Each component has one clear purpose
6. **Storage Abstraction**: Unified interface for multiple backends

### Installation & Usage

```python
# Install from source (PyPI package coming soon)
pip install -e .

# Use the framework
from telegram_bot_stack import BotBase
from telegram_bot_stack.storage import JSONStorage

class MyBot(BotBase):
    def get_welcome_message(self) -> str:
        return "Welcome to My Bot!"

# Simple, clean API ready for PyPI!
```

## 📖 Example: Quit Smoking Bot

The `src/quit_smoking/` directory contains a complete example bot built with the framework.

### Features of Example Bot

- 📊 **Progress Tracking**: Monitor smoke-free period (years, months, days)
- 💰 **Prize Fund System**: Growing monthly reward (5,000₽ → 100,000₽)
- 📅 **Monthly Notifications**: Automated motivational messages
- 💭 **Motivational Quotes**: Random inspirational quotes
- 👥 **Admin System**: Inherited from framework

### Configuration

The example bot tracks progress from a predefined start date. Configure in `src/config.py`:

```python
START_YEAR = 2025
START_MONTH = 1
NOTIFICATION_DAY = 23
NOTIFICATION_HOUR = 21
NOTIFICATION_MINUTE = 58
```

### Running the Example

```bash
# Setup with your bot token
python3 manager.py setup --token "YOUR_TOKEN"

# Start the example bot
python3 manager.py start

# Check status
python3 manager.py status
```

## 🤖 Bot Commands

### User Commands

- `/start` - Register with the bot and get welcome message
- `/status` - View current smoke-free progress and prize fund
- `/my_id` - Get your Telegram user ID

### Admin Commands

- `/notify_all` - Manually send notifications to all users
- `/list_users` - View all registered users
- `/list_admins` - View all administrators
- `/add_admin USER_ID` - Add a new administrator
- `/remove_admin USER_ID` - Remove an administrator
- `/decline_admin` - Decline your own admin privileges

## 🛠️ Management Commands

### Primary Interface (manager.py)

```bash
# 📦 Setup & Configuration
python3 manager.py setup                    # Basic setup
python3 manager.py setup --token TOKEN      # Setup with bot token

# 🚀 Service Management
python3 manager.py start                    # Start the bot
python3 manager.py start --monitoring       # Start with health monitoring
python3 manager.py start --rebuild          # Start with container rebuild
python3 manager.py stop                     # Stop the bot
python3 manager.py restart                  # Restart the bot

# 📊 Monitoring & Status
python3 manager.py status                   # Show comprehensive status
python3 manager.py logs                     # Show recent logs
python3 manager.py logs --follow            # Follow logs in real-time

# 🧹 Maintenance
python3 manager.py clean                    # Basic cleanup
python3 manager.py clean --deep             # Remove all data and images
```

### Convenient Shortcuts (Makefile)

```bash
# 🎯 Setup & Installation
make setup          # Initial project setup
make install        # Complete setup and start with monitoring

# 🚀 Service Management
make start          # Start the bot
make stop           # Stop the bot
make restart        # Restart the bot

# 📊 Status & Monitoring
make status         # Show comprehensive bot status with diagnostics
make logs           # Show logs
make logs-follow    # Follow logs in real-time

# 🧹 Maintenance
make clean          # Clean up containers and images
make clean-deep     # Deep cleanup (removes containers, images, logs)
make build          # Build Docker image
```

## ⚙️ Configuration

### Environment Variables (.env)

| Variable      | Required | Default | Description                            |
| ------------- | -------- | ------- | -------------------------------------- |
| `BOT_TOKEN`   | ✅       | -       | Your Telegram bot token from BotFather |
| `SYSTEM_NAME` | ✅       | -       | System name for containers and logging |

**Example `.env` file:**

```bash
# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here

# System Configuration
SYSTEM_NAME=quit-smoking-bot

```

### Bot Configuration (src/config.py)

```python
# Start date components
START_YEAR = 2025
START_MONTH = 1

# Notification schedule - 23rd of each month at 21:58
NOTIFICATION_DAY = 23
NOTIFICATION_HOUR = 21
NOTIFICATION_MINUTE = 58

# Prize fund settings
MONTHLY_AMOUNT = 5000       # amount in rubles
PRIZE_FUND_INCREASE = 5000  # increase amount per month
MAX_PRIZE_FUND = 100000     # maximum prize fund amount
```

## 🏗️ Project Structure

```
quit-smoking-bot/
├── src/                       # Bot implementation
│   ├── core/                 # ✨ Reusable framework components
│   │   ├── __init__.py      # Core module exports
│   │   ├── bot_base.py      # Base bot class with common patterns
│   │   ├── user_manager.py  # Generic user management
│   │   ├── admin_manager.py # Generic admin system
│   │   └── storage.py       # Storage abstraction layer
│   ├── quit_smoking/         # 🚭 Quit smoking specific logic
│   │   ├── __init__.py      # Module exports
│   │   ├── bot.py           # QuitSmokingBot implementation
│   │   ├── status_manager.py # Progress tracking and prize calculation
│   │   └── quotes_manager.py # Motivational quotes manager
│   ├── bot.py               # Main entry point
│   ├── config.py            # Configuration settings
│   └── utils.py             # Utility functions
├── docker/                   # 🐳 Production Docker configuration
│   ├── Dockerfile           # Container definition
│   ├── docker-compose.yml   # Production-ready orchestration
│   ├── entrypoint.py        # 🚀 Production initialization script
│   └── README.md            # Docker documentation → [see details](docker/README.md)
├── scripts/                  # Advanced management system
│   ├── actions.py           # Core bot operations
│   ├── docker_utils.py      # Docker integration
│   ├── health.py            # Health monitoring
│   ├── environment.py       # Environment management
│   ├── service.py           # Service management
│   ├── errors.py            # Error handling
│   ├── output.py            # Output formatting
│   ├── args.py              # Argument parsing
│   ├── system.py            # System utilities
│   ├── conflicts.py         # Conflict detection
│   └── __init__.py          # Package initialization
├── data/                     # Persistent data (auto-created)
│   ├── bot_users.json       # Registered users
│   ├── bot_admins.json      # Administrator list
│   └── quotes.json          # Motivational quotes
├── logs/                     # Application logs (auto-created)
├── manager.py               # 🎯 Primary management interface
├── Makefile                # Convenient command shortcuts
├── pyproject.toml          # Python project configuration and dependencies
└── README.md              # This file
```

### Architecture Overview

The project now follows a **layered architecture** to support future framework extraction:

- **`src/core/`** - Reusable telegram bot components:

  - `BotBase` - Base class with common bot patterns (user/admin management, command handling, shutdown)
  - `UserManager` - Generic user registration and tracking
  - `AdminManager` - Generic admin privilege management
  - `Storage` - JSON-based storage abstraction

- **`src/quit_smoking/`** - Bot-specific business logic:
  - `QuitSmokingBot` - Inherits from `BotBase`, adds quit smoking tracking
  - `StatusManager` - Tracks smoke-free period and calculates prize fund
  - `QuotesManager` - Manages motivational quotes

This separation makes it easy to:

- Identify reusable vs. bot-specific code
- Extract `core/` into a framework later
- Maintain and test components independently
- Create new bots by inheriting from `BotBase`

## 📚 Local Usage

### Running Locally (without Docker)

#### **✅ Recommended Local Setup:**

```bash
# 1. Setup virtual environment
source venv/bin/activate

# 2. Install dependencies
pip install -e .

# 3. Start bot (using token from .env or command line)
python3 src/bot.py --token "YOUR_BOT_TOKEN_HERE"
# OR (if BOT_TOKEN is in .env)
python3 src/bot.py

# OR use convenient command (requires .env with BOT_TOKEN):
make start-local

# 4. Stop bot when needed
# Ctrl+C (in terminal) OR use convenient command:
make stop-local
```

#### **🔧 Alternative Methods:**

```bash
# As Python module
python3 -m src.bot --token "TOKEN"

# Via installed package entry point
pip install -e .
quit-smoking-bot
```

#### **🚨 Common Issues & Solutions:**

If you get `'Updater' object has no attribute '_polling_cleanup_cb'`:

```bash
# Fix: Update python-telegram-bot
pip install -U "python-telegram-bot>=22.0"

# If issues persist, recreate environment:
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

**Note**: Local running uses the project directory for logs and data, while Docker uses `/app/` paths.

### Docker Monitoring

```bash
# Quick start with monitoring
python3 manager.py start --monitoring

# View logs in real-time (includes entrypoint initialization logs)
python3 manager.py logs --follow

# Check detailed status
python3 manager.py status --detailed

# View health monitoring logs
docker exec quit-smoking-bot cat /app/logs/health.log

# Shell into container
docker exec -it quit-smoking-bot bash

# Restart with rebuild after changes (optimized for caching)
python3 manager.py restart --rebuild
```

**Docker Optimization**: The Docker setup is optimized for layer caching. When code hasn't changed, existing images are reused automatically, making rebuilds much faster.

📖 **For detailed Docker configuration and advanced usage**, see [docker/README.md](docker/README.md)

### Adding Motivational Quotes

Create or edit `data/quotes.json`:

```json
[
  "Every day without cigarettes is a victory over yourself.",
  "Your health is your wealth - you're investing wisely.",
  "Each smoke-free day adds time to your life."
]
```

## 🚀 Deployment

### Production Deployment

```bash
# On your server
git clone <your-repo-url>
cd quit-smoking-bot

# Complete setup with bot token
python3 manager.py setup --token "YOUR_BOT_TOKEN"

# Start with monitoring and logging
python3 manager.py start --monitoring
```

### Updates

```bash
git pull
python3 manager.py restart --rebuild
```

**Efficient Updates**: Thanks to Docker layer caching, updates that don't change dependencies will reuse existing layers, making deployments much faster.

### Production Monitoring

```bash
# Comprehensive status check
python3 manager.py status

# Monitor logs continuously
python3 manager.py logs --follow

# Comprehensive status and diagnostics
make status
```

## 👥 Admin Management

### First Admin Setup

The first user to interact with the bot (using `/start`) automatically becomes an administrator.

### Adding More Admins

1. Users must first register with `/start`
2. Existing admin uses `/add_admin USER_ID`
3. New admin receives notification with decline option
4. Commands are automatically updated in Telegram UI

### Admin Features

- Send manual notifications to all users
- View user and admin lists
- Add/remove administrators
- Access to all user commands plus admin-specific ones

## 🔧 Customization

### Changing the Start Date

Edit `src/config.py`:

```python
START_YEAR = 2025      # Your quit year
START_MONTH = 1        # Your quit month
NOTIFICATION_DAY = 23  # Day of month for notifications
```

### Modifying Prize Fund

Edit `src/config.py`:

```python
MONTHLY_AMOUNT = 5000       # Starting amount
PRIZE_FUND_INCREASE = 5000  # Monthly increase
MAX_PRIZE_FUND = 100000     # Maximum amount
```

### Timezone Configuration

Timezone is configured in code (`src/config.py`):

```python
from zoneinfo import ZoneInfo

BOT_TIMEZONE = ZoneInfo("Europe/Moscow")  # Change as needed
```

## 📋 Requirements

- Python 3.9+
- Docker and Docker Compose
- Telegram bot token from [@BotFather](https://t.me/BotFather)

### Dependencies Management

This project uses modern Python packaging with `pyproject.toml`:

- **Main dependencies**: Defined in `pyproject.toml` for bot functionality
- **Development tools**: Optional group `dev` for linting, testing, type checking
- **GitHub Actions**: Optional group `github-actions` for workflow automation
- **Local usage**: Run without Docker using `python3 src/bot.py`
- **No requirements.txt files**: All managed through pyproject.toml

Install optional dependencies as needed:

```bash
# Development tools
pip install -e ".[dev]"

# GitHub Actions dependencies (for local testing)
pip install -e ".[github-actions]"

# All optional dependencies
pip install -e ".[dev,github-actions]"
```

## 🔍 Troubleshooting

### Bot won't start

```bash
# Check detailed status and diagnostics
python3 manager.py status --detailed

# View logs for errors
python3 manager.py logs

# Run comprehensive diagnostics
make status-full

# Common issues:
# 1. BOT_TOKEN not set - use: python3 manager.py setup --token "TOKEN"
# 2. Docker not running - check Docker service
# 3. Invalid configuration - check .env file
```

### Docker issues

```bash
# Deep cleanup and rebuild
python3 manager.py clean --deep
python3 manager.py start --rebuild

# Or use convenient shortcut
make clean-deep
make start
```

**Performance Tip**: If builds seem slow, the Docker layer cache might be corrupted. Use `docker system prune -f` to clear unused images and restart fresh.

### Local usage issues

```bash
# Run locally to debug
python3 src/bot.py

# Start local bot (alternative to python3 src/bot.py)
make start-local

# Stop local bot
make stop-local
# OR press Ctrl+C in terminal with running bot

# Check status and diagnostics
make status
make status-full
```

### Notifications not working

- Check timezone configuration in `src/config.py`
- Verify notification schedule in `src/config.py`
- Check logs for scheduler errors: `python3 manager.py logs --follow`
- Run diagnostics: `make status` (comprehensive diagnostics included)

## 🛡️ Compatibility & Troubleshooting

### Preventing Version Conflicts

This guide helps prevent dependency conflicts between Docker and local development.

### 🚨 Common Issues

#### `Updater` object has no attribute `_polling_cleanup_cb`

**Cause**: Old python-telegram-bot version (20.8) with `__slots__` restrictions.

**Fix**:

```bash
pip install -U "python-telegram-bot>=22.0"
```

#### "No token provided" despite .env file exists

**Cause**: Missing `load_dotenv()` in bot code - .env file not loaded automatically.

**Fix**: Already fixed in `src/bot.py` with:

```python
from dotenv import load_dotenv
load_dotenv()  # Loads .env file automatically
```

### ✅ Prevention Strategy

#### 1. Version Management

**pyproject.toml** (Source of Truth):

```toml
dependencies = [
    "python-telegram-bot[job-queue]>=22.3,<23.0",  # ✅ Latest stable
    "APScheduler>=3.11.0,<4.0",
    "python-dotenv>=1.1.0",
]
```

#### 2. Development Workflow

```bash
# 🔄 Before each development session
source venv/bin/activate
pip install -e .  # Sync with pyproject.toml

# 🧪 Test both environments
python3 src/bot.py --help  # Local test
make start                 # Docker test
```

#### 3. Environment Isolation

**Local Development**:

- Uses `venv/` virtual environment
- Dependencies from `pyproject.toml`
- Data/logs in project directory

**Docker Production**:

- Uses container environment
- Same `pyproject.toml` dependencies
- Data/logs in `/app/`

### 🔧 Troubleshooting Commands

#### Check Versions

```bash
# Python version
python3 --version

# PTB version
python3 -c "import telegram; print(telegram.__version__)"

# All packages
pip list | grep -E "(telegram|scheduler)"
```

#### Reset Environment

```bash
# Complete reset
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

#### Version Conflicts

```bash
# Force update
pip install -U --force-reinstall "python-telegram-bot>=22.0"

# Check conflicts
pip check
```

### 📋 Pre-Deploy Checklist

- [ ] Local bot starts without errors
- [ ] Docker bot starts without errors
- [ ] Both use same PTB version
- [ ] Dependencies updated in pyproject.toml
- [ ] Virtual environment recreated if needed

### 🚀 Quick Compatibility Commands

```bash
# ✅ Environment check (automated)
python3 manager.py check-env

# 🔧 Manual checks
make check-env         # Complete environment compatibility check
make check-versions    # Check dependency versions only
make test-local        # Test local bot startup
make start-local       # Start bot locally (needs .env)
make stop-local        # Stop locally running bot
make test-both-envs    # Test both environments
make fix-deps         # Fix dependency issues

# 🚀 Development workflow
make python-setup      # Setup environment (uses manager.py dev-setup)
python3 manager.py dev-setup  # Direct setup command
make start-local       # Start bot locally (needs .env with BOT_TOKEN)
make stop-local        # Stop local bot

# 🐳 Docker production
make start
```

### 📞 Emergency Recovery

If bot is completely broken:

```bash
# 1. Reset everything
rm -rf venv/
git stash  # Save current changes

# 2. Fresh start
python3 -m venv venv
source venv/bin/activate
pip install -e .

# 3. Test
python3 src/bot.py --help

# 4. Restore changes
git stash pop
```

## 🤝 Contributing

### Using Cloud Agent for Issues

This project uses **Cloud Agent** for automated issue management:

1. **Create an Issue** using templates at [Issues → New](../../issues/new/choose)
2. **Auto-Labeling** - Labels are applied automatically based on content
3. **Use Slash Commands** in comments:
   - `/breakdown` - Break into subtasks
   - `/accept` - Generate acceptance criteria
   - `/estimate` - Get time estimate
   - `/relate` - Find related files

📚 **[Full Cloud Agent Guide](.github/docs/cloud-agent/GUIDE.md)**

### Standard Contributing Process

1. Fork the repository
2. Create your feature branch
3. Test with `python3 src/bot.py`
4. Deploy with `make start`
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**Stay strong in your smoke-free journey! 🚭💪**
