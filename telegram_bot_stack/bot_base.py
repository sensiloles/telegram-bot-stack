"""Base bot class with common patterns for telegram bots."""

import asyncio
import logging
import time
from typing import Optional

from telegram import (
    BotCommand,
    BotCommandScopeChat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.error import Conflict
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from .admin_manager import AdminManager
from .storage import StorageBackend
from .user_manager import UserManager

logger = logging.getLogger(__name__)


class BotBase:
    """Base class for telegram bots with common functionality.

    This class provides a solid foundation for building Telegram bots with:
    - User and admin management
    - Common command handlers (/start, /my_id, admin commands)
    - Graceful shutdown handling
    - Command registration helpers
    - Customization hooks for bot-specific behavior

    Subclasses should override hooks to customize behavior:
    - on_user_registered(user_id): Called when new user registers
    - get_user_status(user_id): Return custom status message
    - get_welcome_message(): Return custom welcome message
    - register_handlers(): Add custom command handlers

    Args:
        storage: Storage backend instance for persisting data
        bot_name: Name of the bot for welcome messages
        user_commands: List of user command strings (e.g., ["/start", "/help"])
        admin_commands: List of admin command strings (e.g., ["/list_users"])

    Example:
        >>> from telegram_bot_stack import BotBase
        >>> from telegram_bot_stack.storage import JSONStorage
        >>>
        >>> storage = JSONStorage(base_dir="data")
        >>> bot = BotBase(storage, bot_name="My Bot")
    """

    def __init__(
        self,
        storage: StorageBackend,
        bot_name: str = "Telegram Bot",
        user_commands: list = None,
        admin_commands: list = None,
    ):
        """Initialize bot base with storage and configuration."""
        self.storage = storage
        self.bot_name = bot_name
        self.user_manager = UserManager(storage, "bot_users")
        self.admin_manager = AdminManager(storage, "bot_admins")
        self.application: Optional[Application] = None
        self._running = False
        self._shutdown_event = asyncio.Event()
        self._consecutive_conflicts = 0
        self._ever_had_success = False  # Track if bot ever successfully polled
        self._start_time = None  # Track when bot started
        self._last_conflict_time = None  # Track last conflict time

        # Default commands if not provided
        self.user_commands = user_commands or ["/start", "/my_id"]
        self.admin_commands = (
            admin_commands
            or [
                "/list_users",
                "/list_admins",
                "/add_admin",
                "/remove_admin",
                "/decline_admin",
            ]
            + self.user_commands
        )

    # Hooks for customization (override in subclass)

    async def on_user_registered(self, user_id: int) -> None:
        """Hook called when a new user registers.

        Override this in subclass to add custom logic.

        Args:
            user_id: Telegram user ID of the new user
        """
        pass

    async def get_user_status(self, user_id: int) -> str:
        """Hook to provide custom user status message.

        Override this in subclass to return bot-specific status.

        Args:
            user_id: Telegram user ID

        Returns:
            Status message string
        """
        return "👤 User status: Active"

    def get_welcome_message(self) -> str:
        """Hook to provide custom welcome message.

        Override this in subclass to return bot-specific welcome.

        Returns:
            Welcome message string
        """
        return (
            f"👋 Welcome to {self.bot_name}!\n\n"
            f"I'm a helpful bot. Use /my_id to see your user ID."
        )

    # Built-in command handlers

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command - register user and show welcome message."""
        user_id = update.effective_user.id

        # If this is the first user ever and no admins exist, make them admin
        if not self.admin_manager.has_admins():
            self.admin_manager.add_admin(user_id)
            logger.info(f"First user {user_id} set as admin")
            await update.message.reply_text(
                self.get_welcome_message()
                + "\n\n"
                + "You have been set as the first administrator of the bot."
            )
        else:
            await update.message.reply_text(self.get_welcome_message())

        # Add user to the list if not already there
        is_new_user = self.user_manager.add_user(user_id)
        if is_new_user:
            await self.on_user_registered(user_id)

    async def my_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /my_id command - show user their Telegram ID."""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name

        await update.message.reply_text(
            f"Your user ID: {user_id}\n"
            f"Name: {user_name}\n\n"
            "You can share this ID with an admin if you need admin privileges."
        )
        logger.info(f"User {user_id} requested their ID")

    async def list_users(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /list_users command - list all registered users (admin only)."""
        user_id = update.effective_user.id

        if not self.admin_manager.is_admin(user_id):
            await update.message.reply_text(
                "You don't have permission to use this command."
            )
            return

        users = self.user_manager.get_all_users()
        if not users:
            await update.message.reply_text("No registered users yet.")
            return

        users_text = "List of users:\n"
        for i, uid in enumerate(users, 1):
            users_text += f"{i}. {uid}\n"

        await update.message.reply_text(users_text)

    async def list_admins(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /list_admins command - list all admins (admin only)."""
        user_id = update.effective_user.id

        if not self.admin_manager.is_admin(user_id):
            await update.message.reply_text(
                "You don't have permission to use this command."
            )
            return

        admins = self.admin_manager.get_all_admins()
        if not admins:
            await update.message.reply_text("The admin list is empty.")
            return

        admins_text = "List of administrators:\n"
        for i, uid in enumerate(admins, 1):
            admins_text += f"{i}. {uid}\n"

        await update.message.reply_text(admins_text)

    async def add_admin(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /add_admin command - add a new admin (admin only)."""
        user_id = update.effective_user.id
        admin_name = update.effective_user.first_name

        if not self.admin_manager.is_admin(user_id):
            await update.message.reply_text(
                "You don't have permission to use this command."
            )
            logger.warning(f"Unauthorized add_admin attempt by user {user_id}")
            return

        # Check if we have a user ID as an argument
        if not context.args or len(context.args) != 1:
            await update.message.reply_text(
                "Please provide a user ID to add as admin.\nUsage: /add_admin USER_ID"
            )
            return

        try:
            new_admin_id = int(context.args[0])

            # Check if user exists in our database
            if not self.user_manager.user_exists(new_admin_id):
                await update.message.reply_text(
                    f"User ID {new_admin_id} is not registered with the bot. "
                    f"The user must use /start command first."
                )
                return

            # Check if already an admin
            if self.admin_manager.is_admin(new_admin_id):
                await update.message.reply_text(
                    f"User ID {new_admin_id} is already an admin."
                )
                return

            # Add the new admin
            if self.admin_manager.add_admin(new_admin_id):
                await update.message.reply_text(
                    f"User ID {new_admin_id} has been added as an admin."
                )
                logger.info(f"New admin {new_admin_id} added by admin {user_id}")

                # Create inline keyboard for declining admin rights
                keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Decline Admin Rights", callback_data="decline_admin"
                            )
                        ]
                    ]
                )

                # Create admin capabilities list
                admin_capabilities = "\n".join(
                    [
                        f"• {cmd} - Admin command"
                        for cmd in self.admin_commands
                        if cmd not in self.user_commands
                    ]
                )

                # Prepare notification message
                admin_message = (
                    f"🔔 You have been given administrator privileges by {admin_name} (ID: {user_id}).\n\n"
                    f"As an admin, you can now use these additional commands:\n"
                    f"{admin_capabilities}\n\n"
                    f"If you don't want to be an admin, you can decline these privileges using the button below "
                    f"or by using the /decline_admin command."
                )

                # Notify the new admin
                try:
                    await context.bot.send_message(
                        chat_id=new_admin_id, text=admin_message, reply_markup=keyboard
                    )

                    # Update commands in Telegram UI for the new admin
                    await self.update_commands_for_user(new_admin_id)
                except Exception as e:
                    logger.error(f"Failed to notify new admin {new_admin_id}: {e}")
            else:
                await update.message.reply_text(
                    f"Failed to add user ID {new_admin_id} as admin."
                )
        except ValueError:
            await update.message.reply_text(
                "Invalid user ID. Please provide a numeric user ID."
            )

    async def remove_admin(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /remove_admin command - remove an admin (admin only)."""
        user_id = update.effective_user.id
        admin_name = update.effective_user.first_name

        if not self.admin_manager.is_admin(user_id):
            await update.message.reply_text(
                "You don't have permission to use this command."
            )
            logger.warning(f"Unauthorized remove_admin attempt by user {user_id}")
            return

        # Check if we have a user ID as an argument
        if not context.args or len(context.args) != 1:
            await update.message.reply_text(
                "Please provide a user ID to remove from admins.\nUsage: /remove_admin USER_ID"
            )
            return

        try:
            admin_id_to_remove = int(context.args[0])

            # Check if trying to remove themselves
            if admin_id_to_remove == user_id:
                await update.message.reply_text(
                    "You cannot remove yourself from admins. Use /decline_admin instead."
                )
                return

            # Check if the user is an admin
            if not self.admin_manager.is_admin(admin_id_to_remove):
                await update.message.reply_text(
                    f"User ID {admin_id_to_remove} is not an admin."
                )
                return

            # Remove the admin
            if self.admin_manager.remove_admin(admin_id_to_remove):
                await update.message.reply_text(
                    f"User ID {admin_id_to_remove} has been removed from admins."
                )
                logger.info(f"Admin {admin_id_to_remove} removed by admin {user_id}")

                # Notify the removed admin
                try:
                    await context.bot.send_message(
                        chat_id=admin_id_to_remove,
                        text=f"Your administrator privileges have been revoked by {admin_name} (ID: {user_id}).",
                    )

                    # Update commands in Telegram UI for the removed admin
                    await self.update_commands_for_user(
                        admin_id_to_remove, is_admin=False
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to notify removed admin {admin_id_to_remove}: {e}"
                    )
            else:
                await update.message.reply_text(
                    f"Failed to remove user ID {admin_id_to_remove} from admins. "
                    f"Cannot remove the last admin."
                )
        except ValueError:
            await update.message.reply_text(
                "Invalid user ID. Please provide a numeric user ID."
            )

    async def decline_admin(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /decline_admin command - allow user to decline admin privileges."""
        user_id = update.effective_user.id

        if not self.admin_manager.is_admin(user_id):
            await update.message.reply_text("You are not an admin.")
            return

        # Check if this is the last admin
        if self.admin_manager.get_admin_count() <= 1:
            await update.message.reply_text(
                "You are the last administrator and cannot decline your privileges. "
                "Make someone else an admin first."
            )
            return

        # Remove admin privileges
        if self.admin_manager.remove_admin(user_id):
            await update.message.reply_text(
                "You have successfully declined your administrator privileges."
            )
            logger.info(f"Admin {user_id} declined their admin privileges")

            # Update commands in Telegram UI
            await self.update_commands_for_user(user_id, is_admin=False)
        else:
            await update.message.reply_text(
                "Failed to decline administrator privileges."
            )

    async def handle_callback_query(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle callback queries from inline keyboards."""
        query = update.callback_query
        user_id = query.from_user.id

        await query.answer()

        if query.data == "decline_admin":
            # Check if this is the last admin
            if (
                self.admin_manager.get_admin_count() <= 1
                and self.admin_manager.is_admin(user_id)
            ):
                await query.message.reply_text(
                    "You are the last administrator and cannot decline your privileges. "
                    "Make someone else an admin first."
                )
                return

            # Check if the user is an admin
            if not self.admin_manager.is_admin(user_id):
                await query.message.reply_text("You are not an admin.")
                return

            # Remove admin privileges
            if self.admin_manager.remove_admin(user_id):
                await query.message.reply_text(
                    "You have successfully declined your administrator privileges."
                )
                logger.info(
                    f"Admin {user_id} declined their admin privileges via inline button"
                )

                # Update commands in Telegram UI
                await self.update_commands_for_user(user_id, is_admin=False)
            else:
                await query.message.reply_text(
                    "Failed to decline administrator privileges."
                )

    async def update_commands_for_user(self, user_id: int, is_admin: bool = True):
        """Update the available commands for a specific user in Telegram UI.

        Args:
            user_id: Telegram user ID
            is_admin: Whether the user is an admin (True) or regular user (False)
        """
        try:
            if is_admin:
                # Set admin commands for the user
                admin_commands = [
                    BotCommand(command.lstrip("/"), "Admin command")
                    for command in self.admin_commands
                ]

                await self.application.bot.set_my_commands(
                    admin_commands, scope=BotCommandScopeChat(chat_id=user_id)
                )
                logger.info(f"Updated commands for admin {user_id}")
            else:
                # Set normal user commands
                user_commands = [
                    BotCommand(command.lstrip("/"), "User command")
                    for command in self.user_commands
                ]

                await self.application.bot.set_my_commands(
                    user_commands, scope=BotCommandScopeChat(chat_id=user_id)
                )
                logger.info(f"Updated commands for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to update commands for user {user_id}: {e}")

    # Bot lifecycle methods

    async def base_error_handler(
        self, update: Optional[Update], context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle errors from the telegram bot.

        This is a base error handler that catches common errors like Conflict.
        Uses "first come, first served" logic - the bot that successfully
        starts polling first keeps running, others shutdown gracefully.
        """
        error = context.error

        # Check if we should mark bot as successfully established
        # Criteria: Running for 10+ seconds AND no conflicts in last 5 seconds
        if (
            self._start_time
            and not self._ever_had_success
            and time.time() - self._start_time >= 10
        ):
            # Check if we haven't had conflicts recently (5+ seconds ago or never)
            if (
                self._last_conflict_time is None
                or time.time() - self._last_conflict_time >= 5
            ):
                self._ever_had_success = True
                logger.info("✅ Bot successfully established polling connection")

        # Handle Conflict error (multiple bot instances running)
        if isinstance(error, Conflict):
            # Update last conflict time
            self._last_conflict_time = time.time()

            # If this bot already successfully established connection, don't shutdown
            # It means another instance is trying to start but WE got here first
            if self._ever_had_success:
                logger.warning(
                    "⚠️  Another bot instance tried to start but this instance is "
                    "already active and will continue running."
                )
                logger.info("💡 The other bot instance will shutdown automatically.")
                return  # Don't shutdown, don't count conflicts

            # This bot hasn't successfully started yet, count conflicts
            self._consecutive_conflicts += 1

            if self._consecutive_conflicts >= 3:
                logger.error(
                    "⚠️  Another bot instance is already running. "
                    "Shutting down this instance..."
                )
                logger.error(
                    "💡 Tip: The other bot instance started first and will keep running."
                )
                # Stop the application
                if self.application:
                    self.application.stop_running()
            else:
                # Log but don't stop yet
                logger.warning(
                    f"⚠️  Conflict detected ({self._consecutive_conflicts}/3). "
                    "Checking if another instance is already active..."
                )
            return

        # Reset conflict counter on any other error
        self._consecutive_conflicts = 0

        # Log other errors
        logger.error(f"Error occurred: {error}", exc_info=context.error)

    def register_handlers(self):
        """Register all command handlers with the application.

        Override this in subclass to add additional handlers.
        """
        # Mark start time for conflict detection
        self._start_time = time.time()

        # Base command handlers
        base_handlers = {
            "start": self.start,
            "my_id": self.my_id,
            "list_users": self.list_users,
            "list_admins": self.list_admins,
            "add_admin": self.add_admin,
            "remove_admin": self.remove_admin,
            "decline_admin": self.decline_admin,
        }

        for command, handler in base_handlers.items():
            full_command = f"/{command}"
            if (
                full_command in self.user_commands
                or full_command in self.admin_commands
            ):
                self.application.add_handler(CommandHandler(command, handler))
                logger.info(f"Registered handler for command /{command}")

        # Add callback query handler for inline buttons
        self.application.add_handler(CallbackQueryHandler(self.handle_callback_query))

        # Add base error handler
        self.application.add_error_handler(self.base_error_handler)

    async def set_bot_commands(self):
        """Set bot commands in Telegram UI to make them visible."""
        try:
            # Define user commands with descriptions
            user_commands = [
                BotCommand(command.lstrip("/"), "User command")
                for command in self.user_commands
            ]

            # Set commands visible to all users
            await self.application.bot.set_my_commands(user_commands)
            logger.info("Set user commands in Telegram")

            # Get all admins
            admins = self.admin_manager.get_all_admins()

            # Define admin commands with descriptions
            admin_commands = [
                BotCommand(command.lstrip("/"), "Admin command")
                for command in self.admin_commands
            ]

            # Set admin-specific commands for each admin
            for admin_id in admins:
                try:
                    await self.application.bot.set_my_commands(
                        admin_commands, scope=BotCommandScopeChat(chat_id=admin_id)
                    )
                    logger.info(f"Set admin commands for admin {admin_id}")
                except Exception as e:
                    logger.error(f"Failed to set admin commands for {admin_id}: {e}")

            logger.info("Bot commands updated in Telegram")
        except Exception as e:
            logger.error(f"Error setting bot commands: {e}")

    async def shutdown(self):
        """Gracefully shutdown the bot."""
        if not self._running:
            return

        self._running = False
        logger.info("Shutting down bot...")

        try:
            if self.application:
                logger.info("Stopping application...")
                await self.application.stop()
                await self.application.shutdown()

            logger.info("Shutdown complete")
            self._shutdown_event.set()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
