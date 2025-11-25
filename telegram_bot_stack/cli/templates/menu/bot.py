"""Menu bot - demonstrates interactive inline keyboards."""

import asyncio
import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from telegram_bot_stack import BotBase, MemoryStorage

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class MenuBot(BotBase):
    """Bot with interactive inline keyboard menus."""

    def get_welcome_message(self) -> str:
        """Return welcome message for new users."""
        return (
            "👋 Welcome to Menu Bot!\n\n"
            "I demonstrate interactive menus using inline keyboards.\n\n"
            "Commands:\n"
            "/start - Show this message\n"
            "/menu - Show main menu\n"
            "/help - Get help"
        )

    def register_handlers(self) -> None:
        """Register custom handlers."""
        super().register_handlers()

        # Add callback query handler for button clicks
        self.application.add_handler(CallbackQueryHandler(self.button_callback))

    async def handle_start(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /start command with menu.

        Args:
            update: Telegram update
            context: Callback context
        """
        if not update.message:
            return

        # Show welcome message with menu
        keyboard = [
            [
                InlineKeyboardButton("📚 Features", callback_data="features"),
                InlineKeyboardButton("ℹ️ About", callback_data="about"),
            ],
            [
                InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
                InlineKeyboardButton("❓ Help", callback_data="help"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            self.get_welcome_message(),
            reply_markup=reply_markup,
        )

    async def button_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle button clicks.

        Args:
            update: Telegram update
            context: Callback context
        """
        query = update.callback_query
        if not query:
            return

        # Answer callback query to remove loading state
        await query.answer()

        # Handle different button actions
        if query.data == "features":
            await self._show_features(query)
        elif query.data == "about":
            await self._show_about(query)
        elif query.data == "settings":
            await self._show_settings(query)
        elif query.data == "help":
            await self._show_help(query)
        elif query.data == "back":
            await self._show_main_menu(query)

    async def _show_features(self, query) -> None:
        """Show features menu."""
        keyboard = [
            [
                InlineKeyboardButton("✨ Feature 1", callback_data="feature_1"),
                InlineKeyboardButton("🚀 Feature 2", callback_data="feature_2"),
            ],
            [InlineKeyboardButton("« Back", callback_data="back")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "📚 **Features**\n\n"
            "This bot demonstrates:\n"
            "• Interactive inline keyboards\n"
            "• Menu navigation\n"
            "• Callback query handling\n"
            "• Dynamic message updates",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )

    async def _show_about(self, query) -> None:
        """Show about information."""
        keyboard = [[InlineKeyboardButton("« Back", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "ℹ️ **About**\n\n"
            "Menu Bot v1.0\n\n"
            "Built with telegram-bot-stack\n"
            "A professional framework for Telegram bots.",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )

    async def _show_settings(self, query) -> None:
        """Show settings menu."""
        keyboard = [
            [
                InlineKeyboardButton("🔔 Notifications", callback_data="notif"),
                InlineKeyboardButton("🌐 Language", callback_data="lang"),
            ],
            [InlineKeyboardButton("« Back", callback_data="back")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "⚙️ **Settings**\n\nConfigure your preferences:",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )

    async def _show_help(self, query) -> None:
        """Show help information."""
        keyboard = [[InlineKeyboardButton("« Back", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "❓ **Help**\n\n"
            "**Commands:**\n"
            "/start - Show main menu\n"
            "/menu - Show main menu\n"
            "/help - Show this help\n\n"
            "**Navigation:**\n"
            "• Click buttons to navigate\n"
            "• Use « Back to return\n"
            "• Use /start to reset",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )

    async def _show_main_menu(self, query) -> None:
        """Show main menu."""
        keyboard = [
            [
                InlineKeyboardButton("📚 Features", callback_data="features"),
                InlineKeyboardButton("ℹ️ About", callback_data="about"),
            ],
            [
                InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
                InlineKeyboardButton("❓ Help", callback_data="help"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            self.get_welcome_message(),
            reply_markup=reply_markup,
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
    bot = MenuBot(storage=storage)

    # Run bot
    logger.info("Starting menu bot...")
    asyncio.run(bot.run())


if __name__ == "__main__":
    main()
