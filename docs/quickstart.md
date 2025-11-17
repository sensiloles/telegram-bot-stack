# Quick Start Guide

Get started with `telegram-bot-stack` in minutes! This guide will walk you through creating your first bot.

## Installation

### Option 1: Install from GitHub (Recommended)

```bash
# Install latest version directly from GitHub
pip install git+https://github.com/sensiloles/telegram-bot-stack.git

# Or install specific version
pip install git+https://github.com/sensiloles/telegram-bot-stack.git@v0.1.0
```

**Advantages:**
- ✅ No cloning needed
- ✅ Works like normal pip package
- ✅ Easy to specify versions via git tags

### Option 2: Install from Source

```bash
# Clone and install in development mode
git clone https://github.com/sensiloles/telegram-bot-stack.git
cd telegram-bot-stack
pip install -e .
```

**Use this when:**
- You want to modify the framework
- You need editable installation for development

### Option 3: Install from PyPI (Coming Soon)

```bash
pip install telegram-bot-stack
```

**Status:** Available after public release to PyPI

> 📝 **For private installations:** See [Private Installation Guide](private_installation.md) for GitHub Packages, self-hosted PyPI, and other options

## Prerequisites

1. **Python 3.9+** installed on your system
2. **Telegram Bot Token** from [@BotFather](https://t.me/BotFather)

### Getting a Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the bot token (looks like `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Your First Bot

Let's create a simple echo bot that repeats everything you say!

### Step 1: Create Bot File

Create a new file `my_bot.py`:

```python
"""My First Bot - Echoes user messages."""

import logging
import os
from pathlib import Path

from telegram import Update
from telegram.ext import Application, MessageHandler, filters
from telegram.ext._contexttypes import ContextTypes

from telegram_bot_stack import BotBase
from telegram_bot_stack.storage import JSONStorage

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class MyBot(BotBase):
    """Simple bot that echoes messages."""

    def get_welcome_message(self) -> str:
        """Custom welcome message."""
        return "👋 Welcome! I will echo your messages!"

    def register_handlers(self):
        """Register message handlers."""
        super().register_handlers()

        # Echo text messages
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo)
        )

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Echo the user's message."""
        await update.message.reply_text(f"You said: {update.message.text}")


def main():
    """Run the bot."""
    # Get token from environment
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable required!")

    # Create storage
    storage = JSONStorage(base_dir=Path("data"))

    # Create bot
    bot = MyBot(storage=storage, bot_name="My Bot")

    # Create application
    application = Application.builder().token(token).build()
    bot.application = application

    # Register handlers
    bot.register_handlers()

    # Set commands in Telegram UI
    application.post_init = bot.set_bot_commands

    # Run bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
```

### Step 2: Set Your Bot Token

```bash
# Linux/Mac
export TELEGRAM_BOT_TOKEN="your_token_here"

# Windows
set TELEGRAM_BOT_TOKEN=your_token_here

# Or create .env file
echo "TELEGRAM_BOT_TOKEN=your_token_here" > .env
```

### Step 3: Run Your Bot

```bash
python my_bot.py
```

### Step 4: Test Your Bot

1. Open Telegram
2. Find your bot by username
3. Send `/start` to register
4. Send any message - the bot will echo it back!

## Built-in Features

Your bot automatically has these features:

### User Commands

- `/start` - Register and get welcome message
- `/my_id` - Get your Telegram user ID

### Admin Commands

The first user becomes admin and gets additional commands:

- `/list_users` - List all registered users
- `/list_admins` - List all admins
- `/add_admin <user_id>` - Promote user to admin
- `/remove_admin <user_id>` - Demote admin
- `/decline_admin` - Decline your own admin status

## Next Steps

### Customize Your Bot

Override these methods to customize behavior:

```python
class MyBot(BotBase):
    def get_welcome_message(self) -> str:
        """Custom welcome message."""
        return "Welcome to My Bot!"

    async def get_user_status(self, user_id: int) -> str:
        """Custom status for /my_id command."""
        return f"User {user_id} status: Active"

    async def on_user_registered(self, user_id: int):
        """Called when new user registers."""
        logger.info(f"New user registered: {user_id}")
```

### Use Different Storage Backends

```python
# JSON Storage (default, persistent)
from telegram_bot_stack.storage import JSONStorage
storage = JSONStorage(base_dir="data")

# Memory Storage (fast, for testing)
from telegram_bot_stack.storage import MemoryStorage
storage = MemoryStorage()

# Using factory function
from telegram_bot_stack.storage import create_storage
storage = create_storage("json", base_dir="data")
```

### Add Custom Commands

```python
from telegram.ext import CommandHandler

class MyBot(BotBase):
    def register_handlers(self):
        """Register custom commands."""
        super().register_handlers()

        # Add your custom commands
        self.application.add_handler(CommandHandler("hello", self.hello))

    async def hello(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Say hello."""
        await update.message.reply_text("Hello from custom command!")
```

## Example Bots

Check out complete example bots in the `examples/` directory:

- **echo_bot** - Simplest bot (5-10 lines of code)
- **counter_bot** - User-specific counter with state management
- **quit_smoking_bot** - Real-world tracking application

## Common Issues

### Issue: "No module named 'telegram_bot_stack'"

**Solution:** Install the package:

```bash
pip install -e .
```

### Issue: "ValueError: TELEGRAM_BOT_TOKEN environment variable required"

**Solution:** Set your bot token:

```bash
export TELEGRAM_BOT_TOKEN="your_token_here"
```

### Issue: Bot doesn't respond

**Solutions:**

1. Check that bot is running (no errors in console)
2. Verify bot token is correct
3. Make sure you sent `/start` first
4. Check bot privacy settings with @BotFather

## What's Next?

- 📖 Read the [API Reference](api_reference.md) for detailed documentation
- 🏗️ Check [Architecture Guide](../ARCHITECTURE.md) for design patterns
- 🔧 See [Development Guide](../DEVELOPMENT.md) for contributing
- 💡 Browse [examples/](../examples/) for more complex bots

## Getting Help

- 📝 [GitHub Issues](https://github.com/sensiloles/telegram-bot-stack/issues)
- 📚 [Full Documentation](../README.md)
- 💬 Ask questions in GitHub Discussions

Happy bot building! 🤖✨
