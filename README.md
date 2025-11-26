# Telegram Bot Stack

[![PyPI version](https://img.shields.io/pypi/v/telegram-bot-stack?color=blue)](https://pypi.org/project/telegram-bot-stack/)
[![Python](https://img.shields.io/pypi/pyversions/telegram-bot-stack)](https://pypi.org/project/telegram-bot-stack/)
[![License](https://img.shields.io/github/license/sensiloles/telegram-bot-stack)](https://github.com/sensiloles/telegram-bot-stack/blob/main/LICENSE)
[![Tests](https://img.shields.io/github/actions/workflow/status/sensiloles/telegram-bot-stack/tests.yml?branch=main&label=tests)](https://github.com/sensiloles/telegram-bot-stack/actions/workflows/tests.yml)
[![Coverage](https://img.shields.io/badge/coverage-84%25-brightgreen)](https://github.com/sensiloles/telegram-bot-stack)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A reusable Python framework for building production-ready Telegram bots with minimal code. Build bots 70% faster with built-in user management, admin system, storage abstraction, and comprehensive testing infrastructure.

## Features

- **BotBase Class** - Base class with common patterns, 70% less boilerplate
- **User Management** - Built-in registration and tracking
- **Admin System** - Multi-admin support with protection mechanisms
- **Storage Abstraction** - Multiple backends (JSON, Memory, SQL) with unified API
- **Rate Limiting** - Built-in `@rate_limit` decorator for spam protection
- **Scheduler Integration** - APScheduler for periodic tasks
- **Hook Pattern** - Override methods for custom behavior
- **CLI Tools** - Project scaffolding and development commands
- **Comprehensive Tests** - Full test suite with high code coverage (84%)
- **PyPI Package** - Install with `pip install telegram-bot-stack`

## Quick Start

### Create New Bot Project

```bash
# Install framework
pip install telegram-bot-stack

# Create new bot project with full dev environment
telegram-bot-stack init my-bot

# Navigate to project
cd my-bot

# Add your bot token (get it from @BotFather)
echo "BOT_TOKEN=your_token_here" > .env

# Run bot in development mode
telegram-bot-stack dev
```

**What you get:**

- Complete project structure
- Virtual environment configured
- Dependencies installed
- Linting setup (ruff, mypy, pre-commit hooks)
- Testing setup (pytest with fixtures)
- Git initialized with .gitignore

### Build Your Own Bot

```python
# my_bot.py
from telegram_bot_stack import BotBase, rate_limit
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

    @rate_limit(calls=5, period=60)  # 5 calls per minute per user
    async def search_command(self, update, context):
        """Example of rate-limited command."""
        await update.message.reply_text("Searching...")

if __name__ == "__main__":
    import asyncio
    bot = MyBot(
        storage=JSONStorage(Path("./data")),
        bot_name="My Bot",
        user_commands=["/start", "/status"],
        admin_commands=["/list_users", "/add_admin"]
    )
    asyncio.run(bot.run())
```

That's it! 70-80% less code than building from scratch.

## Installation

### From PyPI (Recommended)

```bash
# Install the latest stable version
pip install telegram-bot-stack

# Install with optional dependencies
pip install telegram-bot-stack[database]  # For SQL storage
pip install telegram-bot-stack[all]       # All optional features
```

### From GitHub

```bash
# Install latest development version
pip install git+https://github.com/sensiloles/telegram-bot-stack.git

# Install specific version/tag
pip install git+https://github.com/sensiloles/telegram-bot-stack.git@v1.1.1
```

### From Source (Development)

```bash
# Clone and install in development mode
git clone https://github.com/sensiloles/telegram-bot-stack.git
cd telegram-bot-stack
pip install -e ".[dev]"
```

## Example Bots

The framework includes example bots demonstrating different features:

1. **Echo Bot** (`examples/echo_bot/`) - Simplest example, echoes back messages
2. **Counter Bot** (`examples/counter_bot/`) - Per-user counter with persistence
3. **Reminder Bot** (`examples/reminder_bot/`) - Scheduled notifications with APScheduler
4. **Menu Bot** (`examples/menu_bot/`) - Interactive menus with inline keyboards
5. **Poll Bot** (`examples/poll_bot/`) - Voting system with SQL storage
6. **Quit Smoking Bot** (`examples/quit_smoking_bot/`) - Complete real-world application

### Running Examples

```bash
# Set your bot token
export BOT_TOKEN="your_token_here"

# Run any example bot
cd examples/echo_bot
python3 bot.py
```

## CLI Commands

```bash
# Initialize new project with full dev environment
telegram-bot-stack init <name> [--with-linting] [--with-testing] [--ide vscode] [--git]

# Create from template
telegram-bot-stack new <name> --template <type>  # basic, counter, menu, advanced

# Run in development mode with auto-reload
telegram-bot-stack dev [--reload]

# Validate configuration
telegram-bot-stack validate

# Deploy to VPS
telegram-bot-stack deploy up
```

See [CLI Documentation](docs/cli-specification.md) for complete reference.

## Testing

```bash
# Run all tests with coverage
python3 -m pytest

# Run specific test file
python3 -m pytest tests/core/test_storage.py

# Run with coverage report
python3 -m pytest --cov=telegram_bot_stack --cov-report=html
```

The framework includes comprehensive test coverage (84%) with:

- Unit tests for all core components
- Integration tests for complete workflows
- Async test support with pytest-asyncio
- CI/CD integration with GitHub Actions (Python 3.9-3.12)

## Architecture

The framework follows a layered architecture:

```
telegram_bot_stack/          # Core Framework (PyPI Package)
├── bot_base.py             # Base class with common patterns
├── user_manager.py         # Generic user management
├── admin_manager.py        # Generic admin system
├── decorators.py           # Rate limiting and utilities
├── storage/                # Storage abstraction layer
│   ├── base.py            # StorageBackend interface
│   ├── json.py            # JSONStorage (file-based)
│   ├── memory.py          # MemoryStorage (testing)
│   └── sql.py             # SQLStorage (production)
└── cli/                    # CLI tools for scaffolding
```

### Key Components

- **BotBase** - Common Telegram bot patterns with hooks for customization
- **Storage Abstraction** - Unified API for multiple backends (JSON, Memory, SQL)
- **UserManager** - User registration, removal, and data persistence
- **AdminManager** - Admin assignment with last admin protection
- **Decorators** - Rate limiting, command routing, and utilities

See [Architecture Documentation](docs/architecture.md) for detailed design documentation.

## Storage Backends

The framework supports multiple storage backends with a unified API:

```python
from telegram_bot_stack.storage import JSONStorage, MemoryStorage, SQLStorage
from pathlib import Path

# JSON Storage (file-based, simple setup)
storage = JSONStorage(Path("./data"))

# Memory Storage (fast, for testing)
storage = MemoryStorage()

# SQL Storage (PostgreSQL/SQLite, for production)
storage = SQLStorage(database_url="postgresql://user:pass@localhost/db")
```

See [Storage Guide](docs/storage_guide.md) for detailed information about storage backends.

## Requirements

- Python 3.9+ (Python 3.12 recommended)
- Telegram bot token from [@BotFather](https://t.me/BotFather)

Dependencies are automatically managed through `pyproject.toml`. Optional dependencies:

```bash
# Development tools (linting, testing, type checking)
pip install -e ".[dev]"

# GitHub Actions dependencies (for local workflow testing)
pip install -e ".[github-actions]"

# All optional dependencies
pip install -e ".[dev,github-actions]"
```

## Documentation

- **[Quickstart Guide](docs/quickstart.md)** - Detailed getting started guide
- **[Installation Guide](docs/installation.md)** - Installation options and setup
- **[CLI Specification](docs/cli-specification.md)** - Complete CLI command reference
- **[Architecture Guide](docs/architecture.md)** - Design documentation and patterns
- **[Storage Guide](docs/storage_guide.md)** - Storage backends and usage
- **[API Reference](docs/api_reference.md)** - Complete API documentation
- **[Deployment Guide](docs/deployment_guide.md)** - Production deployment instructions
- **[Migration Guide](docs/migration_guide.md)** - Upgrading between versions

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup and workflow
- Code style and conventions
- Testing requirements
- Pull request process

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- **PyPI:** https://pypi.org/project/telegram-bot-stack/
- **GitHub:** https://github.com/sensiloles/telegram-bot-stack
- **Issues:** https://github.com/sensiloles/telegram-bot-stack/issues
- **Documentation:** [docs/README.md](docs/README.md)

---

Built with ❤️ for the Telegram bot community
