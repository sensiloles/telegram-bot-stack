"""Echo Bot - Simplest possible telegram bot using telegram-bot-stack.

This bot echoes back any message it receives. It demonstrates the
minimal code required to build a functional bot with the framework.
"""

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


class EchoBot(BotBase):
    """Simple echo bot that repeats user messages.

    This bot demonstrates:
    - Minimal subclass of BotBase
    - Custom message handler
    - Basic bot functionality
    """

    def get_welcome_message(self) -> str:
        """Return custom welcome message."""
        return (
            "👋 Welcome to Echo Bot!\n\n"
            "I will repeat everything you say to me.\n"
            "Just send me any message and I'll echo it back!"
        )

    def register_handlers(self):
        """Register command and message handlers."""
        # Register base handlers (start, my_id, admin commands)
        super().register_handlers()

        # Add custom echo handler for text messages
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo_message)
        )
        logger.info("Registered echo message handler")

    async def echo_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Echo back the user's message."""
        user_message = update.message.text
        await update.message.reply_text(f"🔊 You said: {user_message}")
        logger.info(f"Echoed message from user {update.effective_user.id}")


def main():
    """Run the bot."""
    # Get bot token from environment
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN environment variable is required.\n"
            "Set it in .env file or export it: export TELEGRAM_BOT_TOKEN='your_token'"
        )

    # Create storage (data will be saved in examples/echo_bot/data/)
    data_dir = Path(__file__).parent / "data"
    storage = JSONStorage(base_dir=data_dir)
    logger.info(f"Storage initialized at: {data_dir}")

    # Create bot instance
    bot = EchoBot(storage=storage, bot_name="Echo Bot")

    # Create and configure application
    application = Application.builder().token(bot_token).build()
    bot.application = application

    # Register handlers
    bot.register_handlers()

    # Set bot commands in Telegram UI
    application.post_init = bot.set_bot_commands

    # Run the bot
    logger.info("Starting Echo Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
