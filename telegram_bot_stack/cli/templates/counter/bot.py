"""Counter bot - demonstrates state management."""

import asyncio
import logging
import os

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from telegram_bot_stack import BotBase, JSONStorage

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class CounterBot(BotBase):
    """Bot that counts messages per user."""

    def get_welcome_message(self) -> str:
        """Return welcome message for new users."""
        return (
            "👋 Welcome to Counter Bot!\n\n"
            "I'll count your messages and remember your count.\n\n"
            "Commands:\n"
            "/start - Show this message\n"
            "/count - Show your message count\n"
            "/reset - Reset your counter\n"
            "/help - Get help"
        )

    def register_handlers(self) -> None:
        """Register custom command handlers."""
        super().register_handlers()

        # Add custom handlers
        self.application.add_handler(CommandHandler("count", self.count_command))
        self.application.add_handler(CommandHandler("reset", self.reset_command))

    async def count_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Show user's message count.

        Args:
            update: Telegram update
            context: Callback context
        """
        if not update.effective_user:
            return

        user_id = update.effective_user.id

        # Get count from storage
        count = await self.storage.get_user_data(user_id, "message_count", 0)

        await update.message.reply_text(
            f"📊 You've sent {count} message(s) to me!\n\n"
            f"Use /reset to reset your counter."
        )

    async def reset_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Reset user's message count.

        Args:
            update: Telegram update
            context: Callback context
        """
        if not update.effective_user:
            return

        user_id = update.effective_user.id

        # Reset count in storage
        await self.storage.set_user_data(user_id, "message_count", 0)

        await update.message.reply_text(
            "🔄 Your counter has been reset to 0!\n\n"
            "Send me any message to start counting again."
        )

    async def handle_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle incoming messages and increment counter.

        Args:
            update: Telegram update
            context: Callback context
        """
        if not update.effective_user or not update.message:
            return

        user_id = update.effective_user.id

        # Get current count
        count = await self.storage.get_user_data(user_id, "message_count", 0)

        # Increment count
        count += 1
        await self.storage.set_user_data(user_id, "message_count", count)

        # Send response
        await update.message.reply_text(
            f"✅ Message #{count} received!\n\nUse /count to see your total."
        )


def main() -> None:
    """Run the bot."""
    # Get bot token from environment
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN environment variable not set!")
        logger.info("Please create a .env file with your bot token:")
        logger.info("  echo 'BOT_TOKEN=your_token_here' > .env")
        return

    # Initialize bot with JSON storage (persists data)
    storage = JSONStorage(data_dir="data")
    bot = CounterBot(storage=storage)

    # Run bot
    logger.info("Starting counter bot...")
    asyncio.run(bot.run())


if __name__ == "__main__":
    main()
