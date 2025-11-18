#!/usr/bin/env python3
"""Reminder Bot - Demonstrates scheduler usage with telegram-bot-stack.

This bot allows users to create reminders with natural language, demonstrating:
- APScheduler integration
- User-specific notifications
- Timezone handling
- Scheduled task management

Features:
- Create reminders with natural language ("remind me in 1 hour")
- List active reminders
- Delete reminders
- Automatic cleanup of completed reminders
"""

import logging
import os
import re
import signal
import sys
from datetime import datetime, timedelta
from typing import Dict, Optional

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

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


class ReminderBot(BotBase):
    """Reminder bot with scheduler support."""

    def __init__(self, storage, bot_name="Reminder Bot"):
        """Initialize reminder bot.

        Args:
            storage: Storage backend
            bot_name: Name of the bot
        """
        super().__init__(storage=storage, bot_name=bot_name)

        # Storage key for reminders
        self.REMINDERS_KEY = "reminders"

        # Counter for unique reminder IDs
        self.reminder_counter = 0

    def register_handlers(self):
        """Register bot command handlers."""
        super().register_handlers()

        # Reminder commands
        self.application.add_handler(CommandHandler("remind", self.create_reminder))
        self.application.add_handler(CommandHandler("reminders", self.list_reminders))
        self.application.add_handler(
            CommandHandler("delete_reminder", self.delete_reminder)
        )

        # Admin commands
        self.application.add_handler(
            CommandHandler("clear_reminders", self.clear_reminders)
        )

    def get_welcome_message(self) -> str:
        """Get welcome message for new users."""
        return (
            "Welcome to Reminder Bot! ⏰\n\n"
            "I'll help you remember important things.\n\n"
            "Available commands:\n"
            "/remind <time> <message> - Create a reminder\n"
            "/reminders - List your active reminders\n"
            "/delete_reminder <id> - Delete a reminder\n"
            "/help - Show this message\n\n"
            "Time formats:\n"
            "• in 5m - in 5 minutes\n"
            "• in 2h - in 2 hours\n"
            "• in 1d - in 1 day\n"
            "• at 14:30 - at specific time today\n\n"
            "Examples:\n"
            "/remind in 30m Check the oven\n"
            "/remind in 2h Call mom\n"
            "/remind at 15:00 Meeting with team"
        )

    # Reminder Management

    def _get_reminders(self) -> Dict:
        """Get all reminders from storage."""
        return self.storage.load(self.REMINDERS_KEY, default={})

    def _save_reminders(self, reminders: Dict) -> bool:
        """Save reminders to storage."""
        return self.storage.save(self.REMINDERS_KEY, reminders)

    def _generate_reminder_id(self) -> str:
        """Generate unique reminder ID."""
        self.reminder_counter += 1
        return f"r{self.reminder_counter}"

    def _parse_time(self, time_str: str) -> Optional[datetime]:
        """Parse time string to datetime.

        Supported formats:
        - "in 5m" - in 5 minutes
        - "in 2h" - in 2 hours
        - "in 1d" - in 1 day
        - "at 14:30" - at specific time today

        Args:
            time_str: Time string to parse

        Returns:
            datetime object or None if parsing failed
        """
        now = datetime.now()

        # Pattern: "in 5m", "in 2h", "in 1d"
        relative_match = re.match(r"in\s+(\d+)([mhd])", time_str.lower())
        if relative_match:
            amount = int(relative_match.group(1))
            unit = relative_match.group(2)

            if unit == "m":
                return now + timedelta(minutes=amount)
            elif unit == "h":
                return now + timedelta(hours=amount)
            elif unit == "d":
                return now + timedelta(days=amount)

        # Pattern: "at 14:30"
        absolute_match = re.match(r"at\s+(\d{1,2}):(\d{2})", time_str.lower())
        if absolute_match:
            hour = int(absolute_match.group(1))
            minute = int(absolute_match.group(2))

            if 0 <= hour <= 23 and 0 <= minute <= 59:
                target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                # If time has passed today, schedule for tomorrow
                if target <= now:
                    target += timedelta(days=1)
                return target

        return None

    async def _send_reminder(self, context: ContextTypes.DEFAULT_TYPE):
        """Send reminder notification to user.

        This is called by the scheduler when a reminder is due.
        """
        job = context.job
        user_id = job.data["user_id"]
        reminder_id = job.data["reminder_id"]
        message = job.data["message"]

        try:
            # Send reminder message
            await context.bot.send_message(
                chat_id=user_id,
                text=f"⏰ Reminder:\n\n{message}",
            )

            # Remove completed reminder from storage
            reminders = self._get_reminders()
            user_reminders = reminders.get(str(user_id), {})
            if reminder_id in user_reminders:
                del user_reminders[reminder_id]
                if user_reminders:
                    reminders[str(user_id)] = user_reminders
                else:
                    del reminders[str(user_id)]
                self._save_reminders(reminders)

            logger.info(f"Sent reminder {reminder_id} to user {user_id}")

        except Exception as e:
            logger.error(f"Error sending reminder {reminder_id}: {e}")

    # Command Handlers

    async def create_reminder(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Create a new reminder.

        Usage: /remind <time> <message>

        Examples:
        /remind in 30m Check the oven
        /remind in 2h Call mom
        /remind at 15:00 Meeting with team
        """
        user_id = update.effective_user.id

        # Check if user is registered
        if not self.user_manager.user_exists(user_id):
            await update.message.reply_text(
                "Please register first with /start command."
            )
            return

        # Parse command arguments
        if not context.args or len(context.args) < 3:
            await update.message.reply_text(
                "Usage: /remind <time> <message>\n\n"
                "Examples:\n"
                "/remind in 30m Check the oven\n"
                "/remind in 2h Call mom\n"
                "/remind at 15:00 Meeting with team\n\n"
                "Time formats:\n"
                "• in 5m - in 5 minutes\n"
                "• in 2h - in 2 hours\n"
                "• in 1d - in 1 day\n"
                "• at 14:30 - at specific time today"
            )
            return

        # Parse time (first 2 args: "in 30m" or "at 14:30")
        time_str = " ".join(context.args[:2])
        message = " ".join(context.args[2:])

        # Parse time
        target_time = self._parse_time(time_str)
        if not target_time:
            await update.message.reply_text(
                "❌ Invalid time format.\n\n"
                "Supported formats:\n"
                "• in 5m - in 5 minutes\n"
                "• in 2h - in 2 hours\n"
                "• in 1d - in 1 day\n"
                "• at 14:30 - at specific time today"
            )
            return

        # Check if time is in the past
        if target_time <= datetime.now():
            await update.message.reply_text("❌ Cannot create reminder in the past.")
            return

        # Generate reminder ID
        reminder_id = self._generate_reminder_id()

        # Schedule reminder
        context.job_queue.run_once(
            self._send_reminder,
            when=target_time,
            data={
                "user_id": user_id,
                "reminder_id": reminder_id,
                "message": message,
            },
            name=f"reminder_{user_id}_{reminder_id}",
        )

        # Save reminder to storage
        reminders = self._get_reminders()
        user_reminders = reminders.get(str(user_id), {})
        user_reminders[reminder_id] = {
            "message": message,
            "time": target_time.isoformat(),
            "created_at": datetime.now().isoformat(),
        }
        reminders[str(user_id)] = user_reminders
        self._save_reminders(reminders)

        # Format response
        time_diff = target_time - datetime.now()
        hours, remainder = divmod(int(time_diff.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)

        time_str = []
        if hours > 0:
            time_str.append(f"{hours}h")
        if minutes > 0:
            time_str.append(f"{minutes}m")

        await update.message.reply_text(
            f"✅ Reminder created! ID: {reminder_id}\n\n"
            f"📝 {message}\n"
            f"⏰ In {' '.join(time_str)} ({target_time.strftime('%H:%M')})"
        )
        logger.info(f"User {user_id} created reminder {reminder_id}")

    async def list_reminders(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all active reminders for the user."""
        user_id = update.effective_user.id

        # Check if user is registered
        if not self.user_manager.user_exists(user_id):
            await update.message.reply_text(
                "Please register first with /start command."
            )
            return

        # Get user's reminders
        reminders = self._get_reminders()
        user_reminders = reminders.get(str(user_id), {})

        if not user_reminders:
            await update.message.reply_text("You have no active reminders.")
            return

        # Format response
        response = "📋 Your Active Reminders:\n\n"
        now = datetime.now()

        for reminder_id, reminder in user_reminders.items():
            message = reminder["message"]
            target_time = datetime.fromisoformat(reminder["time"])

            # Calculate time remaining
            time_diff = target_time - now
            if time_diff.total_seconds() < 0:
                time_str = "overdue"
            else:
                hours, remainder = divmod(int(time_diff.total_seconds()), 3600)
                minutes, _ = divmod(remainder, 60)

                time_parts = []
                if hours > 0:
                    time_parts.append(f"{hours}h")
                if minutes > 0:
                    time_parts.append(f"{minutes}m")
                time_str = " ".join(time_parts) if time_parts else "< 1m"

            response += f"ID: {reminder_id}\n"
            response += f"📝 {message}\n"
            response += f"⏰ In {time_str} ({target_time.strftime('%H:%M')})\n\n"

        response += "Delete with: /delete_reminder <id>"

        await update.message.reply_text(response)

    async def delete_reminder(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Delete a reminder.

        Usage: /delete_reminder <id>

        Example: /delete_reminder r1
        """
        user_id = update.effective_user.id

        # Check if user is registered
        if not self.user_manager.user_exists(user_id):
            await update.message.reply_text(
                "Please register first with /start command."
            )
            return

        # Parse arguments
        if len(context.args) != 1:
            await update.message.reply_text(
                "Usage: /delete_reminder <id>\n\nExample: /delete_reminder r1"
            )
            return

        reminder_id = context.args[0]

        # Get user's reminders
        reminders = self._get_reminders()
        user_reminders = reminders.get(str(user_id), {})

        if reminder_id not in user_reminders:
            await update.message.reply_text(f"Reminder {reminder_id} not found.")
            return

        # Remove scheduled job
        job_name = f"reminder_{user_id}_{reminder_id}"
        jobs = context.job_queue.get_jobs_by_name(job_name)
        for job in jobs:
            job.schedule_removal()

        # Remove from storage
        del user_reminders[reminder_id]
        if user_reminders:
            reminders[str(user_id)] = user_reminders
        else:
            del reminders[str(user_id)]
        self._save_reminders(reminders)

        await update.message.reply_text(f"✅ Reminder {reminder_id} deleted.")
        logger.info(f"User {user_id} deleted reminder {reminder_id}")

    async def clear_reminders(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Clear all reminders (admin only)."""
        user_id = update.effective_user.id

        # Check if user is admin
        if not self.admin_manager.is_admin(user_id):
            await update.message.reply_text("This command is only for admins.")
            return

        # Remove all scheduled jobs
        current_jobs = context.job_queue.jobs()
        for job in current_jobs:
            if job.name and job.name.startswith("reminder_"):
                job.schedule_removal()

        # Clear storage
        self._save_reminders({})

        await update.message.reply_text("✅ All reminders cleared.")
        logger.info(f"Admin {user_id} cleared all reminders")


def main():
    """Run the reminder bot."""
    # Get bot token from environment
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError(
            "BOT_TOKEN environment variable is required.\n"
            "Set it in .env file or export it: export BOT_TOKEN='your_token'"
        )

    admin_id = os.getenv("ADMIN_ID")
    if admin_id:
        admin_id = int(admin_id)

    # Determine storage backend
    storage_backend = os.getenv("STORAGE_BACKEND", "json")
    base_dir = os.getenv("STORAGE_DIR", "data")
    if not os.path.isabs(base_dir):
        base_dir = os.path.join(os.path.dirname(__file__), base_dir)

    logger.info(f"Using storage backend: {storage_backend}")

    # Create storage
    storage = create_storage(storage_backend, base_dir=base_dir)
    logger.info(f"Storage initialized at: {base_dir}")

    # Create bot instance
    bot = ReminderBot(storage=storage, bot_name="Reminder Bot")

    # Add admin if specified
    if admin_id:
        bot.admin_manager.add_admin(admin_id)
        logger.info(f"Added admin: {admin_id}")

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
    logger.info("Starting Reminder Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
