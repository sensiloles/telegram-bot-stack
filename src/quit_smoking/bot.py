"""Quit smoking bot implementation - inherits from BotBase."""

import argparse
import asyncio
import datetime
import logging
import logging.config
import os
import signal

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from src.config import (
    ADMIN_COMMANDS,
    BOT_NAME,
    BOT_TIMEZONE,
    DATA_DIR,
    LOGGING_CONFIG,
    NOTIFICATION_DAY,
    NOTIFICATION_HOUR,
    NOTIFICATION_MINUTE,
    USER_COMMANDS,
    WELCOME_MESSAGE,
)
from src.core import BotBase, Storage

from .quotes_manager import QuotesManager
from .status_manager import StatusManager

# Configure logging only if not already configured
if not logging.getLogger().handlers:
    logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


class QuitSmokingBot(BotBase):
    """Quit smoking tracking bot - inherits common functionality from BotBase."""

    def __init__(self):
        """Initialize quit smoking bot with storage and managers."""
        # Initialize storage
        storage = Storage(DATA_DIR)

        # Initialize base class with configuration
        super().__init__(
            storage=storage,
            bot_name=BOT_NAME,
            user_commands=USER_COMMANDS,
            admin_commands=ADMIN_COMMANDS,
        )

        # Initialize quit smoking specific managers
        self.quotes_manager = QuotesManager(storage)
        self.status_manager = StatusManager(self.quotes_manager)
        self.scheduler = None

    # Override hooks from BotBase

    def get_welcome_message(self) -> str:
        """Return custom welcome message for quit smoking bot."""
        return WELCOME_MESSAGE.format(bot_name=self.bot_name)

    async def get_user_status(self, user_id: int) -> str:
        """Return quit smoking status for user."""
        return self.status_manager.get_status_info(str(user_id))

    # Quit smoking specific commands

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send current non-smoking status when the command /status is issued."""
        user_id = update.effective_user.id

        # Get status info with a quote
        status_info = self.status_manager.get_status_info("status")

        # Send status message
        await update.message.reply_text(status_info)
        logger.info(f"Status sent to user {user_id}")

    async def _send_notifications_to_users(self, bot, status_info):
        """Send notifications to all users with the provided status info."""
        logger.info("Starting to send notifications to users")

        users = self.user_manager.get_all_users()
        if not users:
            logger.warning("No users to send notifications to")
            return

        for user_id in users:
            try:
                await bot.send_message(chat_id=user_id, text=status_info)
                logger.info(f"Status sent to user {user_id}")
            except Exception as e:
                logger.error(f"Failed to send notification to user {user_id}: {e}")

        logger.info("Notification sending completed")

    async def send_monthly_notification(self, context=None) -> None:
        """Send monthly notifications to all users."""
        logger.info("Starting monthly notification process")

        # Use global random quote for notifications
        status_info = self.status_manager.get_status_info("monthly_notification")

        # Determine which bot instance to use
        bot_instance = context.bot if context else self.application.bot

        # Send notifications to all users
        await self._send_notifications_to_users(bot_instance, status_info)

    async def scheduled_notification_job(self):
        """Job for scheduler to send monthly notifications."""
        logger.info("Scheduled notification job triggered")

        # Use global random quote for notifications
        status_info = self.status_manager.get_status_info("monthly_notification")

        # Send notifications to all users
        await self._send_notifications_to_users(self.application.bot, status_info)

    async def manual_notification(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE = None,
    ) -> None:
        """Manually send notifications to all users (admin command)."""
        user_id = update.effective_user.id

        if self.admin_manager.is_admin(user_id):
            try:
                await self.send_monthly_notification(context)
                await update.message.reply_text("Notifications sent to all users.")
                logger.info(f"Manual notification triggered by admin {user_id}")
            except Exception as e:
                await update.message.reply_text(f"Error sending notifications: {e!s}")
                logger.error(f"Error in manual notification: {e}")
        else:
            await update.message.reply_text(
                "You don't have permission to use this command."
            )
            logger.warning(
                f"Unauthorized manual notification attempt by user {user_id}"
            )

    # Override register_handlers to add quit smoking specific commands

    def register_handlers(self):
        """Register all command handlers including quit smoking specific ones."""
        # Register base handlers first
        super().register_handlers()

        # Add quit smoking specific handlers
        self.application.add_handler(CommandHandler("status", self.status))
        self.application.add_handler(
            CommandHandler("notify_all", self.manual_notification)
        )

        logger.info("Registered quit smoking specific command handlers")

    # Bot lifecycle methods

    async def setup(self):
        """Setup the bot and scheduler."""
        # Get token from command line arguments or environment variable
        parser = argparse.ArgumentParser(description="Quit Smoking Telegram Bot")
        parser.add_argument("--token", type=str, help="Telegram bot token")
        args = parser.parse_args()

        # Get token from args or environment
        bot_token = args.token or os.environ.get("BOT_TOKEN")
        if not bot_token:
            logger.error(
                "No token provided. Please provide a token via --token argument or BOT_TOKEN environment variable."
            )
            return False

        # Log token information (but not the actual token for security)
        token_source = "command line argument" if args.token else "environment variable"
        logger.info(f"Using token from {token_source}")

        try:
            # Create the Application
            self.application = Application.builder().token(bot_token).build()

            # Register all handlers
            self.register_handlers()

            # Setup scheduler for monthly notifications
            self.scheduler = AsyncIOScheduler(timezone=BOT_TIMEZONE)

            # Add monthly notification job
            self.scheduler.add_job(
                self.scheduled_notification_job,
                "cron",
                day=NOTIFICATION_DAY,
                hour=NOTIFICATION_HOUR,
                minute=NOTIFICATION_MINUTE,
            )

            return True
        except Exception as e:
            logger.error(f"Error during setup: {e}")
            return False

    async def shutdown(self):
        """Cleanup and shutdown the bot gracefully."""
        if not self._running:
            return

        self._running = False
        logger.info("Shutting down quit smoking bot...")

        try:
            if self.scheduler and self.scheduler.running:
                logger.info("Stopping scheduler...")
                self.scheduler.shutdown(wait=True)

            # Call parent shutdown
            await super().shutdown()

            logger.info("Quit smoking bot shutdown complete")
        except Exception as e:
            logger.error(f"Error during quit smoking bot shutdown: {e}")

    async def run(self):
        """Run the bot."""
        if not await self.setup():
            return

        self._running = True

        try:
            # Start the scheduler
            self.scheduler.start()

            # Log clear session start marker
            logger.info("=" * 50)
            logger.info("NEW BOT SESSION STARTED")
            logger.info("=" * 50)

            logger.info(f"Bot started at {datetime.datetime.now(BOT_TIMEZONE)}")

            # Calculate and log next notification time
            next_run = self.scheduler.get_jobs()[0].next_run_time
            logger.info(f"Next scheduled notification will be sent at: {next_run}")
            logger.info(
                f"Scheduled monthly notification for day={NOTIFICATION_DAY}, {NOTIFICATION_HOUR:02d}:{NOTIFICATION_MINUTE:02d} {BOT_TIMEZONE.key} time"
            )

            # Start the bot with polling
            await self.application.initialize()
            await self.application.start()

            # Update commands in Telegram UI
            await self.set_bot_commands()

            await self.application.updater.start_polling()

            # Keep the bot running until shutdown is requested
            while self._running:
                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Error running bot: {e}")
        finally:
            if self._running:
                await self.shutdown()


def main():
    """Main function to run the quit smoking bot."""
    bot = QuitSmokingBot()

    async def async_shutdown(signum):
        logger.info(f"Received signal {signum}")
        bot._running = False
        await bot.shutdown()

    def signal_handler(signum, frame):
        # Create a new event loop for the signal handler
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(async_shutdown(signum))
        finally:
            loop.close()

    # Setup signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Run the bot
    try:
        # Create a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bot.run())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        # Create a new event loop for keyboard interrupt handling
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(async_shutdown("SIGINT"))
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        # Clean up the event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.stop()
        loop.close()


if __name__ == "__main__":
    main()
