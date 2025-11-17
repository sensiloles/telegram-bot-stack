"""Quit Smoking Bot - Real-world example using telegram-bot-stack.

This bot tracks your smoke-free period and calculates a growing prize fund.
It demonstrates real-world bot implementation with custom business logic.
"""

import logging
import os
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler
from telegram.ext._contexttypes import ContextTypes

from telegram_bot_stack import BotBase
from telegram_bot_stack.storage import JSONStorage

from .config import BOT_NAME, WELCOME_MESSAGE
from .quotes_manager import QuotesManager
from .status_manager import StatusManager

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class QuitSmokingBot(BotBase):
    """Quit smoking tracking bot built with telegram-bot-stack.

    This bot demonstrates:
    - Extending BotBase with custom functionality
    - Custom business logic (prize fund calculation)
    - Integration with custom managers
    - Overriding framework hooks
    """

    def __init__(self, storage, bot_name=BOT_NAME):
        """Initialize quit smoking bot with storage."""
        super().__init__(
            storage=storage,
            bot_name=bot_name,
            user_commands=["/start", "/status", "/my_id"],
            admin_commands=[
                "/list_users",
                "/list_admins",
                "/add_admin",
                "/remove_admin",
                "/decline_admin",
                "/status",
                "/my_id",
            ],
        )

        # Initialize quit smoking specific managers
        data_dir = Path(__file__).parent / "data"
        self.quotes_manager = QuotesManager(
            storage, quotes_file=data_dir / "quotes.json"
        )
        self.status_manager = StatusManager(self.quotes_manager)

    # Override hooks from BotBase

    def get_welcome_message(self) -> str:
        """Return custom welcome message for quit smoking bot."""
        return WELCOME_MESSAGE.format(bot_name=self.bot_name)

    async def get_user_status(self, user_id: int) -> str:
        """Return quit smoking status for user."""
        return self.status_manager.get_status_info(str(user_id))

    def register_handlers(self):
        """Register command handlers including custom status command."""
        # Register base handlers
        super().register_handlers()

        # Add quit smoking specific commands
        self.application.add_handler(CommandHandler("status", self.status))
        logger.info("Registered status command handler")

    # Quit smoking specific commands

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send current non-smoking status when the command /status is issued."""
        user_id = update.effective_user.id

        # Get status info with a quote
        status_info = self.status_manager.get_status_info("status")

        # Send status message
        await update.message.reply_text(status_info)
        logger.info(f"Status sent to user {user_id}")


def main():
    """Run the bot."""
    # Get bot token from environment
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN environment variable is required.\n"
            "Set it in .env file or export it: export TELEGRAM_BOT_TOKEN='your_token'"
        )

    # Create storage (data will be saved in examples/quit_smoking_bot/data/)
    data_dir = Path(__file__).parent / "data"
    storage = JSONStorage(base_dir=data_dir)
    logger.info(f"Storage initialized at: {data_dir}")

    # Create bot instance
    bot = QuitSmokingBot(storage=storage)

    # Create and configure application
    application = Application.builder().token(bot_token).build()
    bot.application = application

    # Register handlers
    bot.register_handlers()

    # Set bot commands in Telegram UI
    application.post_init = bot.set_bot_commands

    # Run the bot
    logger.info("Starting Quit Smoking Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
