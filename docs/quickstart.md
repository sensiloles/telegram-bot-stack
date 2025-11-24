# Quick Start Guide

Get started with telegram-bot-stack in less than 5 minutes!

## Installation

```bash
pip install telegram-bot-stack
```

## Method 1: Using CLI (Recommended)

The fastest way to create a new bot with complete development environment:

### Step 1: Initialize Project

```bash
telegram-bot-stack init my-awesome-bot
```

This creates a complete bot project with:
- ✅ Virtual environment
- ✅ Dependencies installed
- ✅ Linting configured (ruff, mypy, pre-commit)
- ✅ Testing configured (pytest)
- ✅ IDE settings (VS Code)
- ✅ Git initialized

### Step 2: Configure Bot Token

```bash
cd my-awesome-bot
echo "BOT_TOKEN=your_token_here" > .env
```

Get your token from [@BotFather](https://t.me/BotFather)

### Step 3: Run Your Bot

```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
python bot.py
```

That's it! Your bot is running. 🎉

## Method 2: Manual Setup

If you prefer manual setup:

### Step 1: Create Project Structure

```bash
mkdir my-bot
cd my-bot
```

### Step 2: Create `bot.py`

```python
"""Simple echo bot."""

import asyncio
import logging
import os

from telegram_bot_stack import BotBase, MemoryStorage

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class MyBot(BotBase):
    """My awesome bot."""

    def get_welcome_message(self) -> str:
        """Return welcome message for new users."""
        return (
            "👋 Welcome! I'm your awesome bot.\\n\\n"
            "Available commands:\\n"
            "/start - Show this message\\n"
            "/help - Get help"
        )


def main() -> None:
    """Run the bot."""
    # Get bot token from environment
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN environment variable not set!")
        return

    # Initialize bot with storage
    storage = MemoryStorage()
    bot = MyBot(storage=storage)

    # Run bot
    logger.info("Starting bot...")
    asyncio.run(bot.run())


if __name__ == "__main__":
    main()
```

### Step 3: Create `.env` File

```bash
echo "BOT_TOKEN=your_token_here" > .env
```

### Step 4: Install Dependencies

```bash
pip install telegram-bot-stack python-dotenv
```

### Step 5: Run Your Bot

```bash
python bot.py
```

## CLI Commands

### Initialize New Project

```bash
# Full setup with all features
telegram-bot-stack init my-bot

# Minimal setup
telegram-bot-stack init my-bot --no-linting --no-testing --no-git

# With specific IDE
telegram-bot-stack init my-bot --ide pycharm

# With specific package manager
telegram-bot-stack init my-bot --package-manager poetry
```

### Create from Template

```bash
# Create from basic template
telegram-bot-stack new my-bot --template basic

# Available templates: basic, counter, menu, advanced
telegram-bot-stack new analytics-bot --template advanced
```

### Development Mode

```bash
# Run with auto-reload
telegram-bot-stack dev --reload

# Run specific file
telegram-bot-stack dev --bot-file my_bot.py
```

### Validate Configuration

```bash
# Check configuration
telegram-bot-stack validate

# Strict mode (exit with error if validation fails)
telegram-bot-stack validate --strict
```

## Next Steps

- 📖 Read the [Architecture Guide](architecture.md)
- 🔧 Learn about [Storage Options](storage_guide.md)
- 📚 Check the [API Reference](api_reference.md)
- 🚀 See [Examples](../examples/)

## Common Issues

### Bot Token Not Found

```
Error: BOT_TOKEN environment variable not set!
```

**Solution:** Create a `.env` file with your bot token:
```bash
echo "BOT_TOKEN=your_token_here" > .env
```

### Import Errors

```
ModuleNotFoundError: No module named 'telegram_bot_stack'
```

**Solution:** Install the package:
```bash
pip install telegram-bot-stack
```

### Permission Denied (Virtual Environment)

```
Permission denied: venv/bin/activate
```

**Solution:** Activate virtual environment:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Getting Help

- 📖 [Documentation](https://github.com/sensiloles/telegram-bot-stack)
- 🐛 [Report Issues](https://github.com/sensiloles/telegram-bot-stack/issues)
- 💬 [Discussions](https://github.com/sensiloles/telegram-bot-stack/discussions)
