"""Tests for Quit Smoking Bot example."""

import importlib.util
import sys
from pathlib import Path

import pytest

from telegram_bot_stack.storage import create_storage

# Get project root
project_root = Path(__file__).parent.parent.parent
bot_path = project_root / "examples" / "quit_smoking_bot" / "bot.py"


class TestQuitSmokingBot:
    """Test suite for Quit Smoking Bot."""

    @pytest.fixture
    def bot_module(self):
        """Load quit smoking bot module."""
        bot_dir = bot_path.parent
        if str(bot_dir) not in sys.path:
            sys.path.insert(0, str(bot_dir))

        spec = importlib.util.spec_from_file_location(
            "quit_smoking_bot_module", bot_path
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules["quit_smoking_bot_module"] = module
        spec.loader.exec_module(module)
        return module

    @pytest.fixture
    def bot_class(self, bot_module):
        """Get QuitSmokingBot class."""
        return bot_module.QuitSmokingBot

    @pytest.fixture
    def bot_instance(self, bot_class):
        """Create QuitSmokingBot instance with memory storage."""
        storage = create_storage("memory")
        return bot_class(storage=storage, bot_name="Test Quit Smoking Bot")

    def test_module_import(self, bot_module):
        """Test that quit smoking bot module can be imported."""
        assert bot_module is not None

    def test_class_exists(self, bot_class):
        """Test that QuitSmokingBot class exists."""
        assert bot_class is not None
        assert bot_class.__name__ == "QuitSmokingBot"

    def test_initialization(self, bot_instance):
        """Test that QuitSmokingBot can be initialized."""
        assert bot_instance is not None
        assert bot_instance.bot_name == "Test Quit Smoking Bot"

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

    def test_has_custom_managers(self, bot_instance):
        """Test that bot has custom managers."""
        assert hasattr(bot_instance, "quotes_manager")
        assert hasattr(bot_instance, "status_manager")

    def test_has_status_method(self, bot_instance):
        """Test that bot has status method."""
        assert hasattr(bot_instance, "status")
        assert callable(bot_instance.status)

    def test_welcome_message_override(self, bot_instance):
        """Test that bot overrides welcome message."""
        welcome = bot_instance.get_welcome_message()
        assert welcome is not None
        assert len(welcome) > 0

    def test_get_user_status(self, bot_instance):
        """Test that get_user_status method exists."""
        assert callable(getattr(bot_instance, "get_user_status", None))

    def test_quotes_manager_initialized(self, bot_instance):
        """Test that quotes manager is properly initialized."""
        assert bot_instance.quotes_manager is not None
        assert hasattr(bot_instance.quotes_manager, "get_random_quote")

    def test_status_manager_initialized(self, bot_instance):
        """Test that status manager is properly initialized."""
        assert bot_instance.status_manager is not None
        assert hasattr(bot_instance.status_manager, "get_status_info")
