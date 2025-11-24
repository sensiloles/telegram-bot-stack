"""Advanced bot - demonstrates all best practices."""

import asyncio
import logging
import os
from typing import Optional

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters

from telegram_bot_stack import BotBase, SQLStorage

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class AdvancedBot(BotBase):
    """Advanced bot with all features and best practices.

    Features:
    - SQL storage for production
    - Custom commands
    - Message handlers
    - Error handling
    - Admin commands
    - User statistics
    """

    def get_welcome_message(self) -> str:
        """Return welcome message for new users."""
        return (
            "👋 Welcome to Advanced Bot!\n\n"
            "I demonstrate all features and best practices:\n"
            "• SQL storage for production\n"
            "• Custom commands\n"
            "• Error handling\n"
            "• Admin features\n"
            "• User statistics\n\n"
            "Commands:\n"
            "/start - Show this message\n"
            "/stats - Show your statistics\n"
            "/help - Get help\n\n"
            "Admin commands:\n"
            "/admin - Admin panel (admins only)\n"
            "/broadcast - Send message to all users (admins only)"
        )

    def register_handlers(self) -> None:
        """Register custom command handlers."""
        super().register_handlers()

        # Custom commands
        self.application.add_handler(CommandHandler("stats", self.stats_command))

        # Message handler for all text messages
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message)
        )

        # Error handler
        self.application.add_error_handler(self.error_handler)

    async def stats_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Show user statistics.

        Args:
            update: Telegram update
            context: Callback context
        """
        if not update.effective_user or not update.message:
            return

        user_id = update.effective_user.id

        # Get statistics from storage
        message_count = await self.storage.get_user_data(user_id, "message_count", 0)
        command_count = await self.storage.get_user_data(user_id, "command_count", 0)
        first_seen = await self.storage.get_user_data(user_id, "first_seen", "Unknown")

        # Check if user is admin
        is_admin = await self.admin_manager.is_admin(user_id)
        admin_status = "✅ Admin" if is_admin else "👤 User"

        await update.message.reply_text(
            f"📊 **Your Statistics**\n\n"
            f"Status: {admin_status}\n"
            f"Messages sent: {message_count}\n"
            f"Commands used: {command_count}\n"
            f"First seen: {first_seen}\n\n"
            f"Use /help to see available commands.",
            parse_mode="Markdown",
        )

    async def handle_text_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle text messages and update statistics.

        Args:
            update: Telegram update
            context: Callback context
        """
        if not update.effective_user or not update.message:
            return

        user_id = update.effective_user.id
        text = update.message.text

        # Update message count
        count = await self.storage.get_user_data(user_id, "message_count", 0)
        await self.storage.set_user_data(user_id, "message_count", count + 1)

        # Store first seen timestamp
        first_seen = await self.storage.get_user_data(user_id, "first_seen")
        if not first_seen:
            from datetime import datetime

            await self.storage.set_user_data(
                user_id, "first_seen", datetime.now().isoformat()
            )

        # Echo message with statistics
        await update.message.reply_text(
            f"📝 Message received!\n\n"
            f"You said: _{text}_\n\n"
            f"Total messages: {count + 1}\n"
            f"Use /stats to see detailed statistics.",
            parse_mode="Markdown",
        )

    async def handle_start(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /start command with statistics tracking.

        Args:
            update: Telegram update
            context: Callback context
        """
        if not update.effective_user:
            return

        user_id = update.effective_user.id

        # Track command usage
        count = await self.storage.get_user_data(user_id, "command_count", 0)
        await self.storage.set_user_data(user_id, "command_count", count + 1)

        # Call parent implementation
        await super().handle_start(update, context)

    async def error_handler(
        self, update: Optional[Update], context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle errors gracefully.

        Args:
            update: Telegram update (may be None)
            context: Callback context
        """
        # Log the error
        logger.error("Exception while handling an update:", exc_info=context.error)

        # Try to notify user
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "❌ An error occurred while processing your request.\n"
                    "Please try again later or contact support."
                )
            except Exception as e:
                logger.error(f"Failed to send error message to user: {e}")


def main() -> None:
    """Run the bot."""
    # Get bot token from environment
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN environment variable not set!")
        logger.info("Please create a .env file with your bot token:")
        logger.info("  echo 'BOT_TOKEN=your_token_here' > .env")
        return

    # Get admin IDs from environment (optional)
    admin_ids_str = os.getenv("ADMIN_IDS", "")
    admin_ids = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]

    # Initialize bot with SQL storage (production-ready)
    storage = SQLStorage(db_path="bot.db")
    bot = AdvancedBot(storage=storage, admin_ids=admin_ids)

    # Run bot
    logger.info("Starting advanced bot...")
    logger.info(f"Admins: {admin_ids if admin_ids else 'None configured'}")
    asyncio.run(bot.run())


if __name__ == "__main__":
    main()
