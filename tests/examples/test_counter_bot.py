"""Tests for Counter Bot example."""

import importlib.util
import sys
from pathlib import Path

import pytest

from telegram_bot_stack.storage import create_storage

# Get project root
project_root = Path(__file__).parent.parent.parent
bot_path = project_root / "examples" / "counter_bot" / "bot.py"


class TestCounterBot:
    """Test suite for Counter Bot."""

    @pytest.fixture
    def bot_module(self):
        """Load counter bot module."""
        bot_dir = bot_path.parent
        if str(bot_dir) not in sys.path:
            sys.path.insert(0, str(bot_dir))

        spec = importlib.util.spec_from_file_location("counter_bot_module", bot_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["counter_bot_module"] = module
        spec.loader.exec_module(module)
        return module

    @pytest.fixture
    def bot_class(self, bot_module):
        """Get CounterBot class."""
        return bot_module.CounterBot

    @pytest.fixture
    def bot_instance(self, bot_class):
        """Create CounterBot instance with memory storage."""
        storage = create_storage("memory")
        return bot_class(storage=storage, bot_name="Test Counter Bot")

    def test_module_import(self, bot_module):
        """Test that counter bot module can be imported."""
        assert bot_module is not None

    def test_class_exists(self, bot_class):
        """Test that CounterBot class exists."""
        assert bot_class is not None
        assert bot_class.__name__ == "CounterBot"

    def test_initialization(self, bot_instance):
        """Test that CounterBot can be initialized."""
        assert bot_instance is not None
        assert bot_instance.bot_name == "Test Counter Bot"

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

    def test_storage_works(self, bot_instance):
        """Test that bot can use storage."""
        assert bot_instance.storage is not None
