"""Tests for rate limiting decorators."""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from telegram import CallbackQuery, Message, Update, User
from telegram.ext import ContextTypes

from telegram_bot_stack import BotBase, rate_limit
from telegram_bot_stack.storage import MemoryStorage


class RateLimitedBot(BotBase):
    """Bot with rate-limited handlers for testing."""

    @rate_limit(calls=3, period=60)
    async def limited_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler limited to 3 calls per minute per user."""
        if update.message:
            await update.message.reply_text("Success!")
        return "success"

    @rate_limit(calls=1, period=10, scope="global")
    async def global_limited_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handler limited to 1 call per 10 seconds globally."""
        await update.message.reply_text("Global success!")
        return "global_success"

    @rate_limit(calls=2, period=30, message="Custom rate limit message!")
    async def custom_message_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handler with custom rate limit message."""
        await update.message.reply_text("Custom success!")
        return "custom_success"

    async def no_limit_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handler without rate limiting."""
        await update.message.reply_text("No limit!")
        return "no_limit"


@pytest.fixture
def storage():
    """Create memory storage for tests."""
    return MemoryStorage()


@pytest.fixture
def bot(storage):
    """Create test bot instance."""
    return RateLimitedBot(storage, bot_name="Test Bot")


@pytest.fixture
def user():
    """Create mock user."""
    return User(id=12345, first_name="Test", is_bot=False)


@pytest.fixture
def admin_user(bot):
    """Create mock admin user."""
    user = User(id=99999, first_name="Admin", is_bot=False)
    bot.admin_manager.add_admin(user.id)
    return user


@pytest.fixture
def update(user):
    """Create mock update with message."""
    message = MagicMock(spec=Message)
    message.reply_text = AsyncMock()
    update = MagicMock(spec=Update)
    update.effective_user = user
    update.message = message
    update.callback_query = None
    return update


@pytest.fixture
def context():
    """Create mock context."""
    return MagicMock(spec=ContextTypes.DEFAULT_TYPE)


@pytest.mark.asyncio
class TestRateLimit:
    """Tests for @rate_limit decorator."""

    async def test_basic_rate_limiting(self, bot, update, context):
        """Test basic rate limiting per user."""
        # First 3 calls should succeed
        for i in range(3):
            result = await bot.limited_command(update, context)
            assert result == "success"
            assert update.message.reply_text.call_count == i + 1

        # 4th call should be rate limited
        update.message.reply_text.reset_mock()
        result = await bot.limited_command(update, context)
        assert result is None  # Rate limited, returns None
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args[0][0]
        assert "Rate limit exceeded" in call_args
        assert "Try again in" in call_args

    async def test_different_users_separate_limits(self, bot, update, context, storage):
        """Test that different users have separate rate limits."""
        # User 1 makes 3 calls
        for _ in range(3):
            result = await bot.limited_command(update, context)
            assert result == "success"

        # User 1 is rate limited
        update.message.reply_text.reset_mock()
        result = await bot.limited_command(update, context)
        assert result is None

        # User 2 can still make calls
        user2 = User(id=67890, first_name="Test2", is_bot=False)
        update.effective_user = user2
        update.message.reply_text.reset_mock()
        result = await bot.limited_command(update, context)
        assert result == "success"

    async def test_global_rate_limiting(self, bot, update, context):
        """Test global rate limiting affects all users."""
        # User 1 makes 1 call
        result = await bot.global_limited_command(update, context)
        assert result == "global_success"

        # User 2 is also rate limited (global scope)
        user2 = User(id=67890, first_name="Test2", is_bot=False)
        update.effective_user = user2
        update.message.reply_text.reset_mock()
        result = await bot.global_limited_command(update, context)
        assert result is None
        call_args = update.message.reply_text.call_args[0][0]
        assert "globally rate limited" in call_args

    async def test_admin_bypasses_rate_limit(self, bot, admin_user, context):
        """Test that admins bypass rate limits."""
        # Create update with admin user
        message = MagicMock(spec=Message)
        message.reply_text = AsyncMock()
        update = MagicMock(spec=Update)
        update.effective_user = admin_user
        update.message = message
        update.callback_query = None

        # Admin can make unlimited calls
        for _ in range(10):
            result = await bot.limited_command(update, context)
            assert result == "success"

    async def test_custom_error_message(self, bot, update, context):
        """Test custom rate limit error message."""
        # Use up the limit
        for _ in range(2):
            await bot.custom_message_command(update, context)

        # Next call should show custom message
        update.message.reply_text.reset_mock()
        await bot.custom_message_command(update, context)
        update.message.reply_text.assert_called_once_with("Custom rate limit message!")

    async def test_rate_limit_cleanup(self, bot, update, context, storage):
        """Test that old timestamps are cleaned up."""
        # Make 2 calls
        for _ in range(2):
            await bot.limited_command(update, context)

        # Check storage has 2 timestamps
        key = "rate_limit:user:12345:limited_command"
        timestamps = storage.load(key)
        assert len(timestamps) == 2

        # Manually set old timestamp (beyond period)
        old_time = time.time() - 120  # 2 minutes ago (period is 60s)
        timestamps[0] = old_time
        storage.save(key, timestamps)

        # Make another call - should clean up old timestamp
        await bot.limited_command(update, context)
        timestamps = storage.load(key)
        assert len(timestamps) == 2  # Old one cleaned, new one added
        assert all(ts > time.time() - 60 for ts in timestamps)

    async def test_rate_limit_expiry(self, bot, update, context, storage):
        """Test that rate limit expires after period."""
        # Use up the limit (3 calls)
        for _ in range(3):
            await bot.limited_command(update, context)

        # 4th call is rate limited
        update.message.reply_text.reset_mock()
        result = await bot.limited_command(update, context)
        assert result is None

        # Manually expire the oldest timestamp
        key = "rate_limit:user:12345:limited_command"
        timestamps = storage.load(key)
        timestamps[0] = time.time() - 61  # Beyond 60s period
        storage.save(key, timestamps)

        # Now should be able to call again
        update.message.reply_text.reset_mock()
        result = await bot.limited_command(update, context)
        assert result == "success"

    async def test_callback_query_rate_limit(self, bot, user, context):
        """Test rate limiting works with callback queries."""
        # Create update with callback query instead of message
        callback = MagicMock(spec=CallbackQuery)
        callback.answer = AsyncMock()
        update = MagicMock(spec=Update)
        update.effective_user = user
        update.message = None
        update.callback_query = callback

        # Use up limit
        for _ in range(3):
            await bot.limited_command(update, context)

        # Next call should be rate limited via callback answer
        await bot.limited_command(update, context)
        callback.answer.assert_called_once()
        call_args = callback.answer.call_args
        assert "Rate limit exceeded" in call_args[0][0]
        assert call_args[1]["show_alert"] is True

    async def test_concurrent_calls(self, bot, update, context):
        """Test rate limiting with concurrent calls."""
        # Make 5 concurrent calls
        tasks = [bot.limited_command(update, context) for _ in range(5)]
        results = await asyncio.gather(*tasks)

        # Only first 3 should succeed
        successes = [r for r in results if r == "success"]
        assert len(successes) == 3

    async def test_storage_failure_fail_open(self, bot, update, context, storage):
        """Test that storage failures allow the call (fail-open)."""
        # Make storage raise exception
        original_save = storage.save

        def failing_save(key, data):
            if "rate_limit" in key:
                raise Exception("Storage error!")
            return original_save(key, data)

        storage.save = failing_save

        # Call should still succeed despite storage error
        result = await bot.limited_command(update, context)
        assert result == "success"

    async def test_bot_without_storage(self, update, context):
        """Test decorator handles bot without storage gracefully."""

        class MinimalBot:
            """Bot without storage."""

            @rate_limit(calls=1, period=10)
            async def limited(self, update, context):
                await update.message.reply_text("Success!")
                return "success"

        bot = MinimalBot()
        # Should work without rate limiting
        result = await bot.limited(update, context)
        assert result == "success"

    async def test_bot_without_admin_manager(self, storage, update, context):
        """Test decorator still rate limits without admin_manager."""

        class MinimalBot:
            """Bot with storage but no admin_manager."""

            def __init__(self, storage):
                self.storage = storage

            @rate_limit(calls=1, period=10)
            async def limited(self, update, context):
                await update.message.reply_text("Success!")
                return "success"

        bot = MinimalBot(storage)
        # Should work with rate limiting even without admin_manager
        result = await bot.limited(update, context)
        assert result == "success"

        # Second call should be rate limited (no admin bypass available)
        update.message.reply_text.reset_mock()
        result = await bot.limited(update, context)
        assert result is None  # Rate limited

    async def test_multiple_commands_separate_limits(self, bot, update, context):
        """Test that different commands have separate rate limits."""
        # Use up limit for limited_command
        for _ in range(3):
            await bot.limited_command(update, context)

        # limited_command is now rate limited
        update.message.reply_text.reset_mock()
        result = await bot.limited_command(update, context)
        assert result is None

        # custom_message_command still has its own limit
        result = await bot.custom_message_command(update, context)
        assert result == "custom_success"

    async def test_no_rate_limit_command(self, bot, update, context):
        """Test that commands without decorator are not rate limited."""
        # Can call unlimited times
        for _ in range(100):
            result = await bot.no_limit_command(update, context)
            assert result == "no_limit"


@pytest.mark.asyncio
class TestRateLimitEdgeCases:
    """Tests for edge cases and error conditions."""

    async def test_zero_calls_period(self, storage, update, context):
        """Test with edge case parameters (0 calls = always rate limited)."""

        class EdgeBot(BotBase):
            @rate_limit(calls=0, period=10)
            async def always_limited(self, update, context):
                if update.message:
                    await update.message.reply_text("Should never see this!")
                return "success"

        bot = EdgeBot(storage)
        # Every call should be rate limited (0 calls allowed)
        result = await bot.always_limited(update, context)
        assert result is None  # Immediately rate limited

    async def test_very_short_period(self, storage, update, context):
        """Test with very short period (1 second)."""

        class ShortBot(BotBase):
            @rate_limit(calls=1, period=1)
            async def short_limit(self, update, context):
                await update.message.reply_text("Success!")
                return "success"

        bot = ShortBot(storage)

        # First call succeeds
        result = await bot.short_limit(update, context)
        assert result == "success"

        # Second call is rate limited
        update.message.reply_text.reset_mock()
        result = await bot.short_limit(update, context)
        assert result is None

        # Wait 1 second and try again
        await asyncio.sleep(1.1)
        result = await bot.short_limit(update, context)
        assert result == "success"

    async def test_very_long_period(self, storage, update, context):
        """Test with very long period (1 day)."""

        class LongBot(BotBase):
            @rate_limit(calls=1, period=86400)  # 1 day
            async def daily_limit(self, update, context):
                await update.message.reply_text("Success!")
                return "success"

        bot = LongBot(storage)

        # First call succeeds
        result = await bot.daily_limit(update, context)
        assert result == "success"

        # Second call shows appropriate cooldown message
        update.message.reply_text.reset_mock()
        await bot.daily_limit(update, context)
        call_args = update.message.reply_text.call_args[0][0]
        assert "1d" in call_args or "23h" in call_args  # Should show days or hours

    async def test_update_without_user(self, storage, context):
        """Test handling update without effective_user."""
        # Create update without user
        message = MagicMock(spec=Message)
        message.reply_text = AsyncMock()
        update = MagicMock(spec=Update)
        update.effective_user = None
        update.message = message
        update.callback_query = None

        bot = RateLimitedBot(storage)

        # Should handle gracefully (treats as user_id=0)
        result = await bot.limited_command(update, context)
        assert result == "success"

    async def test_storage_key_format(self, bot, storage, update, context):
        """Test that storage keys are formatted correctly."""
        # Make a call
        await bot.limited_command(update, context)

        # Check user-scoped key
        user_key = "rate_limit:user:12345:limited_command"
        assert storage.exists(user_key)

        # Make global call
        await bot.global_limited_command(update, context)

        # Check global-scoped key
        global_key = "rate_limit:global:global_limited_command"
        assert storage.exists(global_key)
