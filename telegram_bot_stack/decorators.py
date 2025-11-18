"""Rate limiting and utility decorators for telegram bot handlers."""

import logging
import time
from functools import wraps
from typing import Callable, Literal, Optional

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


def rate_limit(
    calls: int,
    period: int,
    scope: Literal["user", "global"] = "user",
    message: Optional[str] = None,
):
    """Rate limit decorator for bot command handlers.

    Limits how often a command can be called within a time period.
    Uses the bot's storage backend to track call timestamps.

    Args:
        calls: Maximum number of calls allowed within the period
        period: Time period in seconds
        scope: Rate limit scope:
            - "user": Per-user rate limiting (default)
            - "global": Bot-wide rate limiting (affects all users)
        message: Custom message to send when rate limited.
            If None, uses default message showing cooldown time.

    Returns:
        Decorated handler function that enforces rate limits

    Example:
        >>> from telegram_bot_stack import BotBase
        >>> from telegram_bot_stack.decorators import rate_limit
        >>>
        >>> class MyBot(BotBase):
        ...     @rate_limit(calls=5, period=60)
        ...     async def expensive_command(self, update, context):
        ...         '''Can be called 5 times per minute per user'''
        ...         await update.message.reply_text("Processing...")
        ...
        ...     @rate_limit(calls=1, period=3600, scope="global")
        ...     async def rare_command(self, update, context):
        ...         '''Can be called once per hour by anyone'''
        ...         await update.message.reply_text("Rare operation executed!")

    Note:
        - Requires bot to have a storage backend
        - Admins bypass rate limits automatically
        - Old timestamps are cleaned up automatically
        - If storage fails, allows the call (fail-open for availability)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            self, update: Update, context: ContextTypes.DEFAULT_TYPE
        ) -> None:
            # Check if bot has required attributes
            if not hasattr(self, "storage"):
                logger.warning(
                    f"Rate limit on {func.__name__} skipped: bot has no storage"
                )
                return await func(self, update, context)

            # Get user info
            user_id = update.effective_user.id if update.effective_user else 0

            # Admins bypass rate limits
            if hasattr(self, "admin_manager") and self.admin_manager.is_admin(user_id):
                logger.debug(f"Admin {user_id} bypassed rate limit on {func.__name__}")
                return await func(self, update, context)

            # Generate storage key
            command_name = func.__name__
            if scope == "global":
                storage_key = f"rate_limit:global:{command_name}"
            else:
                storage_key = f"rate_limit:user:{user_id}:{command_name}"

            # Get current time
            now = time.time()

            try:
                # Load existing timestamps (fail-open if storage fails)
                timestamps = self.storage.load(storage_key, default=[])

                # Clean up old timestamps (older than period)
                cutoff_time = now - period
                timestamps = [ts for ts in timestamps if ts > cutoff_time]

                # Check if rate limit exceeded
                if len(timestamps) >= calls:
                    # Calculate remaining cooldown time
                    oldest_timestamp = min(timestamps) if timestamps else now
                    cooldown_seconds = int(period - (now - oldest_timestamp))

                    # Format cooldown message
                    if cooldown_seconds >= 3600:
                        cooldown_str = f"{cooldown_seconds // 3600}h {(cooldown_seconds % 3600) // 60}m"
                    elif cooldown_seconds >= 60:
                        cooldown_str = (
                            f"{cooldown_seconds // 60}m {cooldown_seconds % 60}s"
                        )
                    else:
                        cooldown_str = f"{cooldown_seconds}s"

                    # Send rate limit message
                    if message:
                        reply_text = message
                    else:
                        if scope == "global":
                            reply_text = (
                                f"⏱ This command is globally rate limited.\n"
                                f"Try again in {cooldown_str}."
                            )
                        else:
                            reply_text = (
                                f"⏱ Rate limit exceeded!\n"
                                f"You can use this command {calls} time(s) per "
                                f"{_format_period(period)}.\n"
                                f"Try again in {cooldown_str}."
                            )

                    if update.message:
                        await update.message.reply_text(reply_text)
                    elif update.callback_query:
                        await update.callback_query.answer(reply_text, show_alert=True)

                    logger.info(
                        f"Rate limit enforced for user {user_id} "
                        f"on {command_name} (scope={scope})"
                    )
                    return

                # Add current timestamp
                timestamps.append(now)

                # Save updated timestamps
                self.storage.save(storage_key, timestamps)

                # Call the original handler
                return await func(self, update, context)

            except Exception as e:
                # Fail-open: allow call if storage fails
                logger.error(
                    f"Rate limit storage error for {command_name}: {e}. "
                    "Allowing call (fail-open)."
                )
                return await func(self, update, context)

        return wrapper

    return decorator


def _format_period(seconds: int) -> str:
    """Format time period in human-readable form.

    Args:
        seconds: Time period in seconds

    Returns:
        Human-readable string like "5m", "1h", "2h 30m"
    """
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m"
    elif seconds < 86400:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        if remaining_minutes > 0:
            return f"{hours}h {remaining_minutes}m"
        return f"{hours}h"
    else:
        days = seconds // 86400
        return f"{days}d"
