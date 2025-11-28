"""Tests for BotBase class."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from telegram_bot_stack.bot_base import BotBase
from telegram_bot_stack.storage import MemoryStorage


@pytest.fixture
def bot_config(tmp_path: Path):
    """Create test bot configuration."""
    storage = MemoryStorage()
    return {
        "storage": storage,
        "bot_name": "Test Bot",
        "user_commands": ["/start", "/my_id"],
        "admin_commands": [
            "/list_users",
            "/list_admins",
            "/add_admin",
            "/remove_admin",
            "/decline_admin",
        ]
        + ["/start", "/my_id"],
    }


@pytest.fixture
def test_bot(bot_config):
    """Create test bot instance."""
    return BotBase(**bot_config)


class TestBotBase:
    """Test suite for BotBase class."""

    def test_initialization(self, test_bot: BotBase):
        """Test bot initializes with correct attributes."""
        assert test_bot.bot_name == "Test Bot"
        assert test_bot.user_manager is not None
        assert test_bot.admin_manager is not None
        assert test_bot.storage is not None
        assert test_bot.application is None
        assert test_bot._running is False

    def test_default_commands(self, bot_config):
        """Test bot uses default commands if none provided."""
        bot_config.pop("user_commands")
        bot_config.pop("admin_commands")

        bot = BotBase(**bot_config)

        assert "/start" in bot.user_commands
        assert "/my_id" in bot.user_commands

    @pytest.mark.asyncio
    async def test_on_user_registered_hook(self, test_bot: BotBase):
        """Test on_user_registered hook can be called."""
        # Should not raise error
        await test_bot.on_user_registered(12345)

    @pytest.mark.asyncio
    async def test_get_user_status_hook(self, test_bot: BotBase):
        """Test get_user_status hook returns string."""
        status = await test_bot.get_user_status(12345)

        assert isinstance(status, str)
        assert len(status) > 0

    def test_get_welcome_message_hook(self, test_bot: BotBase):
        """Test get_welcome_message hook returns message."""
        message = test_bot.get_welcome_message()

        assert isinstance(message, str)
        assert "Test Bot" in message

    @pytest.mark.asyncio
    async def test_start_command_first_user(self, test_bot: BotBase):
        """Test /start command makes first user admin."""
        update = MagicMock()
        update.effective_user.id = 12345
        update.message.reply_text = AsyncMock()

        context = MagicMock()

        await test_bot.start(update, context)

        # First user should be admin
        assert test_bot.admin_manager.is_admin(12345) is True
        assert test_bot.user_manager.user_exists(12345) is True

        # Should call reply_text
        update.message.reply_text.assert_called_once()
        call_text = update.message.reply_text.call_args[0][0]
        assert "administrator" in call_text.lower()

    @pytest.mark.asyncio
    async def test_start_command_subsequent_user(self, test_bot: BotBase):
        """Test /start command for non-first users."""
        # Add first user as admin
        test_bot.admin_manager.add_admin(11111)
        test_bot.user_manager.add_user(11111)

        update = MagicMock()
        update.effective_user.id = 22222
        update.message.reply_text = AsyncMock()

        context = MagicMock()

        await test_bot.start(update, context)

        # Second user should NOT be admin
        assert test_bot.admin_manager.is_admin(22222) is False
        assert test_bot.user_manager.user_exists(22222) is True

        # Should call reply_text with welcome message only
        update.message.reply_text.assert_called_once()
        call_text = update.message.reply_text.call_args[0][0]
        assert "administrator" not in call_text.lower()

    @pytest.mark.asyncio
    async def test_start_command_existing_user(self, test_bot: BotBase):
        """Test /start command for already registered user."""
        test_bot.admin_manager.add_admin(12345)
        test_bot.user_manager.add_user(12345)

        update = MagicMock()
        update.effective_user.id = 12345
        update.message.reply_text = AsyncMock()

        context = MagicMock()

        await test_bot.start(update, context)

        # User should still be registered and admin
        assert test_bot.user_manager.user_exists(12345) is True
        assert test_bot.admin_manager.is_admin(12345) is True

    @pytest.mark.asyncio
    async def test_my_id_command(self, test_bot: BotBase):
        """Test /my_id command returns user ID."""
        update = MagicMock()
        update.effective_user.id = 12345
        update.effective_user.first_name = "John"
        update.message.reply_text = AsyncMock()

        context = MagicMock()

        await test_bot.my_id(update, context)

        # Should reply with user ID
        update.message.reply_text.assert_called_once()
        call_text = update.message.reply_text.call_args[0][0]
        assert "12345" in call_text
        assert "John" in call_text

    @pytest.mark.asyncio
    async def test_list_users_as_admin(self, test_bot: BotBase):
        """Test /list_users command as admin."""
        # Setup admin and users
        test_bot.admin_manager.add_admin(12345)
        test_bot.user_manager.add_user(12345)
        test_bot.user_manager.add_user(67890)

        update = MagicMock()
        update.effective_user.id = 12345
        update.message.reply_text = AsyncMock()

        context = MagicMock()

        await test_bot.list_users(update, context)

        # Should show user list
        update.message.reply_text.assert_called_once()
        call_text = update.message.reply_text.call_args[0][0]
        assert "12345" in call_text
        assert "67890" in call_text

    @pytest.mark.asyncio
    async def test_list_users_as_non_admin(self, test_bot: BotBase):
        """Test /list_users command as non-admin."""
        update = MagicMock()
        update.effective_user.id = 99999
        update.message.reply_text = AsyncMock()

        context = MagicMock()

        await test_bot.list_users(update, context)

        # Should show permission error
        update.message.reply_text.assert_called_once()
        call_text = update.message.reply_text.call_args[0][0]
        assert "permission" in call_text.lower()

    @pytest.mark.asyncio
    async def test_list_admins_as_admin(self, test_bot: BotBase):
        """Test /list_admins command as admin."""
        # Setup admins
        test_bot.admin_manager.add_admin(12345)
        test_bot.admin_manager.add_admin(67890)

        update = MagicMock()
        update.effective_user.id = 12345
        update.message.reply_text = AsyncMock()

        context = MagicMock()

        await test_bot.list_admins(update, context)

        # Should show admin list
        update.message.reply_text.assert_called_once()
        call_text = update.message.reply_text.call_args[0][0]
        assert "12345" in call_text
        assert "67890" in call_text

    @pytest.mark.asyncio
    async def test_add_admin_success(self, test_bot: BotBase):
        """Test /add_admin command successfully adds admin."""
        # Setup: admin user and target user
        test_bot.admin_manager.add_admin(12345)
        test_bot.user_manager.add_user(12345)
        test_bot.user_manager.add_user(67890)

        update = MagicMock()
        update.effective_user.id = 12345
        update.effective_user.first_name = "Admin"
        update.message.reply_text = AsyncMock()

        context = MagicMock()
        context.args = ["67890"]
        context.bot.send_message = AsyncMock()

        await test_bot.add_admin(update, context)

        # New user should be admin
        assert test_bot.admin_manager.is_admin(67890) is True

        # Should confirm to requesting admin
        assert update.message.reply_text.called

    @pytest.mark.asyncio
    async def test_add_admin_missing_user_id(self, test_bot: BotBase):
        """Test /add_admin without user ID shows usage."""
        test_bot.admin_manager.add_admin(12345)

        update = MagicMock()
        update.effective_user.id = 12345
        update.message.reply_text = AsyncMock()

        context = MagicMock()
        context.args = []

        await test_bot.add_admin(update, context)

        # Should show usage message
        update.message.reply_text.assert_called_once()
        call_text = update.message.reply_text.call_args[0][0]
        assert "Usage" in call_text or "usage" in call_text.lower()

    @pytest.mark.asyncio
    async def test_add_admin_unregistered_user(self, test_bot: BotBase):
        """Test /add_admin for unregistered user shows error."""
        test_bot.admin_manager.add_admin(12345)

        update = MagicMock()
        update.effective_user.id = 12345
        update.message.reply_text = AsyncMock()

        context = MagicMock()
        context.args = ["99999"]

        await test_bot.add_admin(update, context)

        # Should show error about unregistered user
        update.message.reply_text.assert_called_once()
        call_text = update.message.reply_text.call_args[0][0]
        assert "not registered" in call_text.lower()

    @pytest.mark.asyncio
    async def test_remove_admin_success(self, test_bot: BotBase):
        """Test /remove_admin successfully removes admin."""
        # Setup: two admins
        test_bot.admin_manager.add_admin(12345)
        test_bot.admin_manager.add_admin(67890)

        update = MagicMock()
        update.effective_user.id = 12345
        update.effective_user.first_name = "Admin"
        update.message.reply_text = AsyncMock()

        context = MagicMock()
        context.args = ["67890"]
        context.bot.send_message = AsyncMock()

        await test_bot.remove_admin(update, context)

        # Target should no longer be admin
        assert test_bot.admin_manager.is_admin(67890) is False

        # Should confirm to requesting admin
        assert update.message.reply_text.called

    @pytest.mark.asyncio
    async def test_remove_admin_cannot_remove_self(self, test_bot: BotBase):
        """Test admin cannot remove themselves via /remove_admin."""
        test_bot.admin_manager.add_admin(12345)

        update = MagicMock()
        update.effective_user.id = 12345
        update.message.reply_text = AsyncMock()

        context = MagicMock()
        context.args = ["12345"]

        await test_bot.remove_admin(update, context)

        # Should show error
        update.message.reply_text.assert_called_once()
        call_text = update.message.reply_text.call_args[0][0]
        assert "decline_admin" in call_text.lower()

    @pytest.mark.asyncio
    async def test_decline_admin_success(self, test_bot: BotBase):
        """Test /decline_admin when multiple admins exist."""
        # Setup: two admins
        test_bot.admin_manager.add_admin(12345)
        test_bot.admin_manager.add_admin(67890)

        update = MagicMock()
        update.effective_user.id = 12345
        update.message.reply_text = AsyncMock()

        context = MagicMock()

        # Mock update_commands_for_user
        test_bot.application = MagicMock()
        test_bot.application.bot = MagicMock()
        with patch.object(test_bot, "update_commands_for_user", new=AsyncMock()):
            await test_bot.decline_admin(update, context)

        # User should no longer be admin
        assert test_bot.admin_manager.is_admin(12345) is False

        # Should confirm
        assert update.message.reply_text.called

    @pytest.mark.asyncio
    async def test_decline_admin_last_admin(self, test_bot: BotBase):
        """Test /decline_admin fails when user is last admin."""
        test_bot.admin_manager.add_admin(12345)

        update = MagicMock()
        update.effective_user.id = 12345
        update.message.reply_text = AsyncMock()

        context = MagicMock()

        await test_bot.decline_admin(update, context)

        # User should still be admin
        assert test_bot.admin_manager.is_admin(12345) is True

        # Should show error
        update.message.reply_text.assert_called_once()
        call_text = update.message.reply_text.call_args[0][0]
        assert "last" in call_text.lower()

    @pytest.mark.asyncio
    async def test_shutdown_when_not_running(self, test_bot: BotBase):
        """Test shutdown when bot is not running."""
        await test_bot.shutdown()

        # Should complete without error
        assert test_bot._running is False

    @pytest.mark.asyncio
    async def test_shutdown_when_running(self, test_bot: BotBase):
        """Test shutdown when bot is running."""
        test_bot._running = True
        test_bot.application = MagicMock()
        test_bot.application.stop = AsyncMock()
        test_bot.application.shutdown = AsyncMock()

        await test_bot.shutdown()

        # Should stop application
        test_bot.application.stop.assert_called_once()
        test_bot.application.shutdown.assert_called_once()
        assert test_bot._running is False

    def test_register_handlers(self, test_bot: BotBase):
        """Test register_handlers method."""
        test_bot.application = MagicMock()

        test_bot.register_handlers()

        # Should have registered handlers
        assert test_bot.application.add_handler.called

    def test_user_commands_list(self, test_bot: BotBase):
        """Test user_commands is a list."""
        assert isinstance(test_bot.user_commands, list)
        assert len(test_bot.user_commands) > 0

    def test_admin_commands_list(self, test_bot: BotBase):
        """Test admin_commands is a list."""
        assert isinstance(test_bot.admin_commands, list)
        assert len(test_bot.admin_commands) > 0

    def test_admin_commands_include_user_commands(self, test_bot: BotBase):
        """Test admin commands include all user commands."""
        for cmd in test_bot.user_commands:
            assert cmd in test_bot.admin_commands
