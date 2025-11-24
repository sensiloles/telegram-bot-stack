"""Simple echo bot - basic template."""

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


class EchoBot(BotBase):
    """Simple echo bot that repeats user messages."""

    def get_welcome_message(self) -> str:
        """Return welcome message for new users."""
        return (
            "👋 Hello! I'm a simple echo bot.\n\n"
            "Send me any message and I'll echo it back!\n\n"
            "Commands:\n"
            "/start - Show this message\n"
            "/help - Get help"
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

    # Initialize bot with memory storage
    storage = MemoryStorage()
    bot = EchoBot(storage=storage)

    # Run bot
    logger.info("Starting echo bot...")
    asyncio.run(bot.run())


if __name__ == "__main__":
    main()
