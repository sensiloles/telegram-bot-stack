"""Tests for Poll Bot example."""

import importlib.util
import sys
from pathlib import Path

import pytest

from telegram_bot_stack.storage import create_storage

# Get project root
project_root = Path(__file__).parent.parent.parent.parent
bot_path = project_root / "examples" / "poll_bot" / "bot.py"


class TestPollBot:
    """Test suite for Poll Bot."""

    @pytest.fixture
    def bot_module(self):
        """Load poll bot module."""
        bot_dir = bot_path.parent
        if str(bot_dir) not in sys.path:
            sys.path.insert(0, str(bot_dir))

        spec = importlib.util.spec_from_file_location("poll_bot_module", bot_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["poll_bot_module"] = module
        spec.loader.exec_module(module)
        return module

    @pytest.fixture
    def bot_class(self, bot_module):
        """Get PollBot class."""
        return bot_module.PollBot

    @pytest.fixture
    def bot_instance(self, bot_class):
        """Create PollBot instance with memory storage."""
        storage = create_storage("memory")
        return bot_class(storage=storage, bot_name="Test Poll Bot")

    def test_module_import(self, bot_module):
        """Test that poll bot module can be imported."""
        assert bot_module is not None

    def test_class_exists(self, bot_class):
        """Test that PollBot class exists."""
        assert bot_class is not None
        assert bot_class.__name__ == "PollBot"

    def test_initialization(self, bot_instance):
        """Test that PollBot can be initialized."""
        assert bot_instance is not None
        assert bot_instance.bot_name == "Test Poll Bot"

    def test_has_required_attributes(self, bot_instance):
        """Test that bot has required attributes."""
        assert hasattr(bot_instance, "storage")
        assert hasattr(bot_instance, "user_manager")
        assert hasattr(bot_instance, "admin_manager")
        assert hasattr(bot_instance, "application")

    def test_has_register_handlers(self, bot_instance):
        """Test that bot has register_handlers method."""
        assert hasattr(bot_instance, "register_handlers")
        assert callable(bot_instance.register_handlers)

    def test_has_storage_keys(self, bot_instance):
        """Test that bot has storage keys defined."""
        assert hasattr(bot_instance, "POLLS_KEY")
        assert hasattr(bot_instance, "VOTES_KEY")
        assert bot_instance.POLLS_KEY == "polls"
        assert bot_instance.VOTES_KEY == "votes"

    def test_has_poll_methods(self, bot_instance):
        """Test that bot has poll-specific command handlers."""
        assert hasattr(bot_instance, "create_poll")
        assert hasattr(bot_instance, "vote")
        assert hasattr(bot_instance, "results")
        assert hasattr(bot_instance, "list_polls")
