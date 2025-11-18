"""Counter Bot - Demonstrates state management with telegram-bot-stack.

This bot maintains a counter for each user, demonstrating how to use
the storage system for user-specific data.
"""

import logging
import os
import signal
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler
from telegram.ext._contexttypes import ContextTypes

from telegram_bot_stack import BotBase
from telegram_bot_stack.storage import JSONStorage

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class CounterBot(BotBase):
    """Bot that maintains a counter for each user.

    This bot demonstrates:
    - User-specific state management
    - Using storage for persistent data
    - Custom commands with business logic
    """

    def __init__(self, storage, bot_name="Counter Bot"):
        """Initialize counter bot with storage."""
        super().__init__(storage, bot_name)
        self.counters_key = "user_counters"

    def get_welcome_message(self) -> str:
        """Return custom welcome message."""
        return (
            "👋 Welcome to Counter Bot!\n\n"
            "I keep track of a counter for each user.\n\n"
            "Commands:\n"
            "/increment - Add 1 to your counter\n"
            "/decrement - Subtract 1 from your counter\n"
            "/count - Show your current count\n"
            "/reset - Reset your counter to 0"
        )

    def register_handlers(self):
        """Register command handlers."""
        # Register base handlers
        super().register_handlers()

        # Add counter-specific commands
        self.application.add_handler(CommandHandler("increment", self.increment))
        self.application.add_handler(CommandHandler("decrement", self.decrement))
        self.application.add_handler(CommandHandler("count", self.show_count))
        self.application.add_handler(CommandHandler("reset", self.reset_count))
        logger.info("Registered counter command handlers")

    def _get_counters(self) -> dict[int, int]:
        """Load all user counters from storage."""
        return self.storage.load(self.counters_key, {})

    def _save_counters(self, counters: dict[int, int]) -> bool:
        """Save all user counters to storage."""
        return self.storage.save(self.counters_key, counters)

    def _get_user_count(self, user_id: int) -> int:
        """Get counter value for a specific user."""
        counters = self._get_counters()
        return counters.get(str(user_id), 0)

    def _set_user_count(self, user_id: int, value: int) -> bool:
        """Set counter value for a specific user."""
        counters = self._get_counters()
        counters[str(user_id)] = value
        return self._save_counters(counters)

    async def increment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Increment user's counter."""
        user_id = update.effective_user.id
        current = self._get_user_count(user_id)
        new_value = current + 1

        if self._set_user_count(user_id, new_value):
            await update.message.reply_text(
                f"➕ Counter incremented!\nYour count: {current} → {new_value}"
            )
            logger.info(f"User {user_id} incremented counter to {new_value}")
        else:
            await update.message.reply_text("❌ Error saving counter value")

    async def decrement(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Decrement user's counter."""
        user_id = update.effective_user.id
        current = self._get_user_count(user_id)
        new_value = current - 1

        if self._set_user_count(user_id, new_value):
            await update.message.reply_text(
                f"➖ Counter decremented!\nYour count: {current} → {new_value}"
            )
            logger.info(f"User {user_id} decremented counter to {new_value}")
        else:
            await update.message.reply_text("❌ Error saving counter value")

    async def show_count(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's current counter value."""
        user_id = update.effective_user.id
        count = self._get_user_count(user_id)

        await update.message.reply_text(f"🔢 Your current count: {count}")
        logger.info(f"User {user_id} checked counter: {count}")

    async def reset_count(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reset user's counter to zero."""
        user_id = update.effective_user.id
        old_count = self._get_user_count(user_id)

        if self._set_user_count(user_id, 0):
            await update.message.reply_text(
                f"🔄 Counter reset!\nPrevious count: {old_count}\nNew count: 0"
            )
            logger.info(f"User {user_id} reset counter from {old_count}")
        else:
            await update.message.reply_text("❌ Error resetting counter")

    async def get_user_status(self, user_id: int) -> str:
        """Return user status with counter information."""
        count = self._get_user_count(user_id)
        return f"👤 User status: Active\n🔢 Your counter: {count}"


def main():
    """Run the bot."""
    # Get bot token from environment
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError(
            "BOT_TOKEN environment variable is required.\n"
            "Set it in .env file or export it: export BOT_TOKEN='your_token'"
        )

    # Create storage (data will be saved in examples/counter_bot/data/)
    data_dir = Path(__file__).parent / "data"
    storage = JSONStorage(base_dir=data_dir)
    logger.info(f"Storage initialized at: {data_dir}")

    # Create bot instance
    bot = CounterBot(storage=storage)

    # Create and configure application
    application = Application.builder().token(bot_token).build()
    bot.application = application

    # Register handlers
    bot.register_handlers()

    # Set bot commands in Telegram UI
    async def post_init_wrapper(app):
        await bot.set_bot_commands()

    application.post_init = post_init_wrapper

    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        application.stop_running()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run the bot
    logger.info("Press Ctrl+C to stop")
    logger.info("Starting Counter Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
