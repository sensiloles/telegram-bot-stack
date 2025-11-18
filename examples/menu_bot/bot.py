#!/usr/bin/env python3
"""Menu Bot - Demonstrates inline keyboards with telegram-bot-stack.

This bot shows interactive menus using inline keyboards, demonstrating:
- Inline keyboard creation
- Callback query handling
- Button navigation
- State management with keyboards
- Pagination

Features:
- Main menu with multiple options
- Settings menu with toggles
- List navigation with pagination
- Confirmation dialogs
- Dynamic keyboard updates
"""

import logging
import os
import sys
from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from telegram_bot_stack import BotBase
from telegram_bot_stack.storage import create_storage

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class MenuBot(BotBase):
    """Menu bot with inline keyboards."""

    def __init__(self, token: str, storage, admin_ids: List[int]):
        """Initialize menu bot.

        Args:
            token: Telegram bot token
            storage: Storage backend
            admin_ids: List of admin user IDs
        """
        super().__init__(token=token, storage=storage, admin_ids=admin_ids)

        # Storage keys
        self.SETTINGS_KEY = "user_settings"
        self.ITEMS_KEY = "items"

        # Initialize sample items for pagination demo
        self._initialize_items()

    def _initialize_items(self):
        """Initialize sample items if not exist."""
        items = self.storage.load(self.ITEMS_KEY, default=[])
        if not items:
            items = [f"Item {i}" for i in range(1, 51)]  # 50 items
            self.storage.save(self.ITEMS_KEY, items)

    def register_handlers(self):
        """Register bot command handlers."""
        super().register_handlers()

        # Menu commands
        self.application.add_handler(CommandHandler("menu", self.show_main_menu))
        self.application.add_handler(CommandHandler("settings", self.show_settings))
        self.application.add_handler(CommandHandler("items", self.show_items))

        # Callback query handler for button presses
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))

    def get_welcome_message(self) -> str:
        """Get welcome message for new users."""
        return (
            "Welcome to Menu Bot! 🎛️\n\n"
            "I demonstrate interactive menus using inline keyboards.\n\n"
            "Available commands:\n"
            "/menu - Show main menu\n"
            "/settings - Show settings menu\n"
            "/items - Browse items with pagination\n"
            "/help - Show this message"
        )

    # Settings Management

    def _get_user_settings(self, user_id: int) -> dict:
        """Get user settings from storage."""
        all_settings = self.storage.load(self.SETTINGS_KEY, default={})
        return all_settings.get(
            str(user_id),
            {
                "notifications": True,
                "dark_mode": False,
                "language": "en",
            },
        )

    def _save_user_settings(self, user_id: int, settings: dict) -> bool:
        """Save user settings to storage."""
        all_settings = self.storage.load(self.SETTINGS_KEY, default={})
        all_settings[str(user_id)] = settings
        return self.storage.save(self.SETTINGS_KEY, all_settings)

    # Keyboard Builders

    def _build_main_menu(self) -> InlineKeyboardMarkup:
        """Build main menu keyboard."""
        keyboard = [
            [InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings")],
            [InlineKeyboardButton("📋 Browse Items", callback_data="menu_items")],
            [InlineKeyboardButton("ℹ️ About", callback_data="menu_about")],
            [InlineKeyboardButton("❓ Help", callback_data="menu_help")],
        ]
        return InlineKeyboardMarkup(keyboard)

    def _build_settings_menu(self, user_id: int) -> InlineKeyboardMarkup:
        """Build settings menu keyboard."""
        settings = self._get_user_settings(user_id)

        # Toggle buttons with current state
        notif_icon = "🔔" if settings["notifications"] else "🔕"
        theme_icon = "🌙" if settings["dark_mode"] else "☀️"

        keyboard = [
            [
                InlineKeyboardButton(
                    f"{notif_icon} Notifications: {'ON' if settings['notifications'] else 'OFF'}",
                    callback_data="toggle_notifications",
                )
            ],
            [
                InlineKeyboardButton(
                    f"{theme_icon} Dark Mode: {'ON' if settings['dark_mode'] else 'OFF'}",
                    callback_data="toggle_dark_mode",
                )
            ],
            [
                InlineKeyboardButton(
                    f"🌐 Language: {settings['language'].upper()}",
                    callback_data="toggle_language",
                )
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")],
        ]
        return InlineKeyboardMarkup(keyboard)

    def _build_items_menu(self, page: int = 0) -> InlineKeyboardMarkup:
        """Build items list with pagination.

        Args:
            page: Current page number (0-indexed)
        """
        items = self.storage.load(self.ITEMS_KEY, default=[])
        items_per_page = 5
        total_pages = (len(items) + items_per_page - 1) // items_per_page

        # Ensure page is within bounds
        page = max(0, min(page, total_pages - 1))

        # Get items for current page
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        page_items = items[start_idx:end_idx]

        # Build keyboard
        keyboard = []

        # Item buttons
        for i, item in enumerate(page_items):
            item_idx = start_idx + i
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"{item_idx + 1}. {item}", callback_data=f"item_{item_idx}"
                    )
                ]
            )

        # Navigation buttons
        nav_buttons = []
        if page > 0:
            nav_buttons.append(
                InlineKeyboardButton("⬅️ Prev", callback_data=f"page_{page - 1}")
            )
        nav_buttons.append(
            InlineKeyboardButton(
                f"📄 {page + 1}/{total_pages}", callback_data="page_info"
            )
        )
        if page < total_pages - 1:
            nav_buttons.append(
                InlineKeyboardButton("➡️ Next", callback_data=f"page_{page + 1}")
            )

        keyboard.append(nav_buttons)
        keyboard.append(
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
        )

        return InlineKeyboardMarkup(keyboard)

    def _build_confirmation_menu(self, action: str) -> InlineKeyboardMarkup:
        """Build confirmation dialog keyboard."""
        keyboard = [
            [
                InlineKeyboardButton("✅ Yes", callback_data=f"confirm_{action}"),
                InlineKeyboardButton("❌ No", callback_data="cancel"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)

    # Command Handlers

    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main menu."""
        user_id = update.effective_user.id

        # Check if user is registered
        if not self.user_manager.user_exists(user_id):
            await update.message.reply_text(
                "Please register first with /start command."
            )
            return

        keyboard = self._build_main_menu()
        await update.message.reply_text(
            "🎛️ Main Menu\n\nChoose an option:",
            reply_markup=keyboard,
        )

    async def show_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show settings menu."""
        user_id = update.effective_user.id

        # Check if user is registered
        if not self.user_manager.user_exists(user_id):
            await update.message.reply_text(
                "Please register first with /start command."
            )
            return

        keyboard = self._build_settings_menu(user_id)
        await update.message.reply_text(
            "⚙️ Settings\n\nAdjust your preferences:",
            reply_markup=keyboard,
        )

    async def show_items(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show items list with pagination."""
        user_id = update.effective_user.id

        # Check if user is registered
        if not self.user_manager.user_exists(user_id):
            await update.message.reply_text(
                "Please register first with /start command."
            )
            return

        keyboard = self._build_items_menu(page=0)
        await update.message.reply_text(
            "📋 Browse Items\n\nSelect an item:",
            reply_markup=keyboard,
        )

    # Callback Handler

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button presses from inline keyboards."""
        query = update.callback_query
        user_id = update.effective_user.id

        # Answer callback query to remove loading state
        await query.answer()

        callback_data = query.data

        # Main menu navigation
        if callback_data == "menu_settings":
            keyboard = self._build_settings_menu(user_id)
            await query.edit_message_text(
                "⚙️ Settings\n\nAdjust your preferences:",
                reply_markup=keyboard,
            )

        elif callback_data == "menu_items":
            keyboard = self._build_items_menu(page=0)
            await query.edit_message_text(
                "📋 Browse Items\n\nSelect an item:",
                reply_markup=keyboard,
            )

        elif callback_data == "menu_about":
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🔙 Back to Menu", callback_data="back_to_menu"
                        )
                    ]
                ]
            )
            await query.edit_message_text(
                "ℹ️ About Menu Bot\n\n"
                "This bot demonstrates inline keyboards with telegram-bot-stack.\n\n"
                "Features:\n"
                "• Interactive menus\n"
                "• Settings with toggles\n"
                "• Pagination\n"
                "• Confirmation dialogs\n\n"
                "Built with telegram-bot-stack framework.",
                reply_markup=keyboard,
            )

        elif callback_data == "menu_help":
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🔙 Back to Menu", callback_data="back_to_menu"
                        )
                    ]
                ]
            )
            await query.edit_message_text(
                "❓ Help\n\n"
                "Available commands:\n"
                "/menu - Show main menu\n"
                "/settings - Show settings menu\n"
                "/items - Browse items with pagination\n"
                "/help - Show this message\n\n"
                "Use the buttons to navigate through menus.",
                reply_markup=keyboard,
            )

        elif callback_data == "back_to_menu":
            keyboard = self._build_main_menu()
            await query.edit_message_text(
                "🎛️ Main Menu\n\nChoose an option:",
                reply_markup=keyboard,
            )

        # Settings toggles
        elif callback_data == "toggle_notifications":
            settings = self._get_user_settings(user_id)
            settings["notifications"] = not settings["notifications"]
            self._save_user_settings(user_id, settings)

            keyboard = self._build_settings_menu(user_id)
            await query.edit_message_reply_markup(reply_markup=keyboard)

        elif callback_data == "toggle_dark_mode":
            settings = self._get_user_settings(user_id)
            settings["dark_mode"] = not settings["dark_mode"]
            self._save_user_settings(user_id, settings)

            keyboard = self._build_settings_menu(user_id)
            await query.edit_message_reply_markup(reply_markup=keyboard)

        elif callback_data == "toggle_language":
            settings = self._get_user_settings(user_id)
            # Cycle through languages
            languages = ["en", "ru", "es", "de"]
            current_idx = languages.index(settings["language"])
            settings["language"] = languages[(current_idx + 1) % len(languages)]
            self._save_user_settings(user_id, settings)

            keyboard = self._build_settings_menu(user_id)
            await query.edit_message_reply_markup(reply_markup=keyboard)

        # Pagination
        elif callback_data.startswith("page_"):
            if callback_data == "page_info":
                # Just show a notification
                await query.answer("Page information", show_alert=False)
            else:
                # Navigate to page
                page = int(callback_data.split("_")[1])
                keyboard = self._build_items_menu(page=page)
                await query.edit_message_reply_markup(reply_markup=keyboard)

        # Item selection
        elif callback_data.startswith("item_"):
            item_idx = int(callback_data.split("_")[1])
            items = self.storage.load(self.ITEMS_KEY, default=[])
            item = items[item_idx]

            keyboard = self._build_confirmation_menu(f"delete_{item_idx}")
            await query.edit_message_text(
                f"📦 Item Details\n\n"
                f"Name: {item}\n"
                f"Index: {item_idx + 1}\n\n"
                f"Do you want to delete this item?",
                reply_markup=keyboard,
            )

        # Confirmation
        elif callback_data.startswith("confirm_"):
            action = callback_data.replace("confirm_", "")

            if action.startswith("delete_"):
                item_idx = int(action.split("_")[1])
                items = self.storage.load(self.ITEMS_KEY, default=[])

                if 0 <= item_idx < len(items):
                    deleted_item = items.pop(item_idx)
                    self.storage.save(self.ITEMS_KEY, items)

                    await query.edit_message_text(
                        f"✅ Item '{deleted_item}' deleted successfully!\n\n"
                        f"Use /items to browse remaining items."
                    )
                else:
                    await query.edit_message_text("❌ Item not found.")

        elif callback_data == "cancel":
            keyboard = self._build_items_menu(page=0)
            await query.edit_message_text(
                "📋 Browse Items\n\nSelect an item:",
                reply_markup=keyboard,
            )


def main():
    """Run the menu bot."""
    # Get configuration from environment
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN environment variable not set")
        sys.exit(1)

    admin_id = os.getenv("ADMIN_ID")
    if not admin_id:
        logger.error("ADMIN_ID environment variable not set")
        sys.exit(1)

    # Determine storage backend
    storage_backend = os.getenv("STORAGE_BACKEND", "json")
    base_dir = os.getenv("STORAGE_DIR", "data")

    logger.info(f"Using storage backend: {storage_backend}")

    # Create storage
    storage = create_storage(storage_backend, base_dir=base_dir)

    # Create and run bot
    bot = MenuBot(token=token, storage=storage, admin_ids=[int(admin_id)])

    try:
        logger.info("Starting Menu Bot...")
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")


if __name__ == "__main__":
    main()
