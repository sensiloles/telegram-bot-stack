#!/usr/bin/env python3
"""Poll Bot - Demonstrates SQL storage usage with telegram-bot-stack.

This bot allows users to create and vote on polls, demonstrating:
- SQL storage backend (SQLite/PostgreSQL)
- Complex data structures
- Multiple storage keys
- Data persistence

Features:
- Create polls with multiple options
- Vote on active polls
- View poll results
- List all polls
- Admin-only poll management
"""

import logging
import os
import sys
from typing import Dict

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


class PollBot(BotBase):
    """Poll bot with SQL storage backend."""

    def __init__(self, storage, bot_name="Poll Bot"):
        """Initialize poll bot.

        Args:
            storage: Storage backend (SQL recommended)
            bot_name: Name of the bot
        """
        super().__init__(storage=storage, bot_name=bot_name)

        # Storage keys
        self.POLLS_KEY = "polls"
        self.VOTES_KEY = "votes"

    def register_handlers(self):
        """Register bot command handlers."""
        super().register_handlers()

        # Poll commands (available to all users)
        self.application.add_handler(CommandHandler("create_poll", self.create_poll))
        self.application.add_handler(CommandHandler("vote", self.vote))
        self.application.add_handler(CommandHandler("results", self.results))
        self.application.add_handler(CommandHandler("list_polls", self.list_polls))

        # Admin commands
        self.application.add_handler(CommandHandler("delete_poll", self.delete_poll))
        self.application.add_handler(CommandHandler("clear_polls", self.clear_polls))

    def get_welcome_message(self) -> str:
        """Get welcome message for new users."""
        return (
            "Welcome to Poll Bot! 🗳️\n\n"
            "Create and vote on polls with your friends.\n\n"
            "Available commands:\n"
            "/create_poll <question> | <option1> | <option2> | ... - Create a poll\n"
            "/vote <poll_id> <option_number> - Vote on a poll\n"
            "/results <poll_id> - View poll results\n"
            "/list_polls - List all active polls\n"
            "/help - Show this message"
        )

    # Poll Management

    def _get_polls(self) -> Dict:
        """Get all polls from storage."""
        return self.storage.load(self.POLLS_KEY, default={})

    def _save_polls(self, polls: Dict) -> bool:
        """Save polls to storage."""
        return self.storage.save(self.POLLS_KEY, polls)

    def _get_votes(self) -> Dict:
        """Get all votes from storage."""
        return self.storage.load(self.VOTES_KEY, default={})

    def _save_votes(self, votes: Dict) -> bool:
        """Save votes to storage."""
        return self.storage.save(self.VOTES_KEY, votes)

    def _generate_poll_id(self, polls: Dict) -> str:
        """Generate unique poll ID."""
        if not polls:
            return "1"
        max_id = max(int(pid) for pid in polls.keys())
        return str(max_id + 1)

    # Command Handlers

    async def create_poll(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Create a new poll.

        Usage: /create_poll <question> | <option1> | <option2> | ...

        Example: /create_poll What's your favorite color? | Red | Blue | Green
        """
        user_id = update.effective_user.id

        # Check if user is registered
        if not self.user_manager.user_exists(user_id):
            await update.message.reply_text(
                "Please register first with /start command."
            )
            return

        # Parse command arguments
        if not context.args:
            await update.message.reply_text(
                "Usage: /create_poll <question> | <option1> | <option2> | ...\n\n"
                "Example: /create_poll What's your favorite color? | Red | Blue | Green"
            )
            return

        # Parse poll data
        poll_text = " ".join(context.args)
        parts = [p.strip() for p in poll_text.split("|")]

        if len(parts) < 3:
            await update.message.reply_text(
                "Please provide a question and at least 2 options.\n\n"
                "Example: /create_poll What's your favorite color? | Red | Blue | Green"
            )
            return

        question = parts[0]
        options = parts[1:]

        # Create poll
        polls = self._get_polls()
        poll_id = self._generate_poll_id(polls)

        polls[poll_id] = {
            "question": question,
            "options": options,
            "created_by": user_id,
            "created_by_username": update.effective_user.username or "Unknown",
        }

        self._save_polls(polls)

        # Format response
        response = f"✅ Poll created! ID: {poll_id}\n\n"
        response += f"❓ {question}\n\n"
        for i, option in enumerate(options, 1):
            response += f"{i}. {option}\n"
        response += f"\nVote with: /vote {poll_id} <option_number>"

        await update.message.reply_text(response)
        logger.info(f"User {user_id} created poll {poll_id}")

    async def vote(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Vote on a poll.

        Usage: /vote <poll_id> <option_number>

        Example: /vote 1 2
        """
        user_id = update.effective_user.id

        # Check if user is registered
        if not self.user_manager.user_exists(user_id):
            await update.message.reply_text(
                "Please register first with /start command."
            )
            return

        # Parse arguments
        if len(context.args) != 2:
            await update.message.reply_text(
                "Usage: /vote <poll_id> <option_number>\n\nExample: /vote 1 2"
            )
            return

        poll_id = context.args[0]
        try:
            option_num = int(context.args[1])
        except ValueError:
            await update.message.reply_text("Option number must be a number.")
            return

        # Check if poll exists
        polls = self._get_polls()
        if poll_id not in polls:
            await update.message.reply_text(f"Poll {poll_id} not found.")
            return

        poll = polls[poll_id]

        # Validate option number
        if option_num < 1 or option_num > len(poll["options"]):
            await update.message.reply_text(
                f"Invalid option. Please choose 1-{len(poll['options'])}."
            )
            return

        # Record vote
        votes = self._get_votes()
        if poll_id not in votes:
            votes[poll_id] = {}

        votes[poll_id][str(user_id)] = option_num
        self._save_votes(votes)

        option_text = poll["options"][option_num - 1]
        await update.message.reply_text(
            f"✅ Your vote has been recorded!\n\n"
            f"You voted for: {option_text}\n\n"
            f"View results with: /results {poll_id}"
        )
        logger.info(f"User {user_id} voted on poll {poll_id}: option {option_num}")

    async def results(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """View poll results.

        Usage: /results <poll_id>

        Example: /results 1
        """
        # Parse arguments
        if len(context.args) != 1:
            await update.message.reply_text(
                "Usage: /results <poll_id>\n\nExample: /results 1"
            )
            return

        poll_id = context.args[0]

        # Check if poll exists
        polls = self._get_polls()
        if poll_id not in polls:
            await update.message.reply_text(f"Poll {poll_id} not found.")
            return

        poll = polls[poll_id]
        votes = self._get_votes()
        poll_votes = votes.get(poll_id, {})

        # Count votes
        vote_counts = [0] * len(poll["options"])
        for vote in poll_votes.values():
            vote_counts[vote - 1] += 1

        total_votes = sum(vote_counts)

        # Format response
        response = f"📊 Poll Results (ID: {poll_id})\n\n"
        response += f"❓ {poll['question']}\n\n"

        for i, option in enumerate(poll["options"]):
            count = vote_counts[i]
            percentage = (count / total_votes * 100) if total_votes > 0 else 0
            bar_length = int(percentage / 5)  # 20 chars max
            bar = "█" * bar_length + "░" * (20 - bar_length)
            response += f"{i + 1}. {option}\n"
            response += f"   {bar} {count} votes ({percentage:.1f}%)\n\n"

        response += f"Total votes: {total_votes}\n"
        response += f"Created by: @{poll['created_by_username']}"

        await update.message.reply_text(response)

    async def list_polls(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all active polls."""
        polls = self._get_polls()

        if not polls:
            await update.message.reply_text("No active polls.")
            return

        response = "📋 Active Polls:\n\n"
        for poll_id, poll in polls.items():
            votes = self._get_votes()
            vote_count = len(votes.get(poll_id, {}))
            response += f"ID: {poll_id}\n"
            response += f"❓ {poll['question']}\n"
            response += f"📊 {vote_count} votes\n"
            response += f"Vote with: /vote {poll_id} <option>\n\n"

        await update.message.reply_text(response)

    async def delete_poll(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Delete a poll (admin only).

        Usage: /delete_poll <poll_id>

        Example: /delete_poll 1
        """
        user_id = update.effective_user.id

        # Check if user is admin
        if not self.admin_manager.is_admin(user_id):
            await update.message.reply_text("This command is only for admins.")
            return

        # Parse arguments
        if len(context.args) != 1:
            await update.message.reply_text(
                "Usage: /delete_poll <poll_id>\n\nExample: /delete_poll 1"
            )
            return

        poll_id = context.args[0]

        # Delete poll
        polls = self._get_polls()
        if poll_id not in polls:
            await update.message.reply_text(f"Poll {poll_id} not found.")
            return

        del polls[poll_id]
        self._save_polls(polls)

        # Delete votes
        votes = self._get_votes()
        if poll_id in votes:
            del votes[poll_id]
            self._save_votes(votes)

        await update.message.reply_text(f"✅ Poll {poll_id} deleted.")
        logger.info(f"Admin {user_id} deleted poll {poll_id}")

    async def clear_polls(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Clear all polls (admin only)."""
        user_id = update.effective_user.id

        # Check if user is admin
        if not self.admin_manager.is_admin(user_id):
            await update.message.reply_text("This command is only for admins.")
            return

        # Clear all polls and votes
        self._save_polls({})
        self._save_votes({})

        await update.message.reply_text("✅ All polls cleared.")
        logger.info(f"Admin {user_id} cleared all polls")


def main():
    """Run the poll bot."""
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
    storage_backend = os.getenv("STORAGE_BACKEND", "sqlite")
    database_url = os.getenv("DATABASE_URL", "sqlite:///poll_bot.db")

    # Handle SQLite database paths - ensure they're created in data/ directory
    if database_url.startswith("sqlite:///"):
        db_path = database_url.replace("sqlite:///", "")
        # If path is relative, make it relative to bot's data directory
        if not os.path.isabs(db_path):
            data_dir = os.path.join(os.path.dirname(__file__), "data")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, db_path)
        database_url = f"sqlite:///{db_path}"

    logger.info(f"Using storage backend: {storage_backend}")
    logger.info(f"Database URL: {database_url}")

    # Create storage
    try:
        if storage_backend in ("sqlite", "postgres", "postgresql", "sql"):
            storage = create_storage(storage_backend, database_url=database_url)
        else:
            base_dir = os.getenv("STORAGE_DIR", "data")
            if not os.path.isabs(base_dir):
                base_dir = os.path.join(os.path.dirname(__file__), base_dir)
            storage = create_storage(storage_backend, base_dir=base_dir)
    except ImportError:
        logger.error(
            "SQL storage not available. Install with: pip install telegram-bot-stack[database]"
        )
        logger.info("Falling back to JSON storage")
        base_dir = os.path.join(os.path.dirname(__file__), "data")
        storage = create_storage("json", base_dir=base_dir)

    logger.info("Storage initialized")

    # Create bot instance
    bot = PollBot(storage=storage, bot_name="Poll Bot")

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

    # Run the bot
    try:
        logger.info("Starting Poll Bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        # Close SQL storage if applicable
        if hasattr(storage, "close"):
            storage.close()
            logger.info("Storage closed")


if __name__ == "__main__":
    main()
