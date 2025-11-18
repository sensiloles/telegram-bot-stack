"""Test suite to validate all example bots.

This module tests that all example bots can be imported and initialized correctly.
It ensures that:
- All bot modules can be imported without errors
- All bot classes can be instantiated with the new API
- All bots have required attributes (storage, user_manager, admin_manager)
- All bots implement the register_handlers method
"""

import importlib.util
import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from telegram_bot_stack.storage import create_storage


class TestExampleBots:
    """Test suite for example bots."""

    @pytest.fixture
    def examples_dir(self):
        """Get examples directory path."""
        return project_root / "examples"

    @pytest.fixture
    def bot_files(self, examples_dir):
        """Get all bot.py files from examples directory."""
        return sorted(examples_dir.glob("*/bot.py"))

    def test_all_bots_found(self, bot_files):
        """Test that example bots are found."""
        assert len(bot_files) > 0, "No bot files found in examples directory"

        bot_names = [bf.parent.name for bf in bot_files]
        expected_bots = [
            "counter_bot",
            "echo_bot",
            "menu_bot",
            "poll_bot",
            "quit_smoking_bot",
            "reminder_bot",
        ]

        for expected in expected_bots:
            assert expected in bot_names, f"Expected bot '{expected}' not found"

    @pytest.mark.parametrize(
        "bot_file",
        [
            pytest.param(bf, id=bf.parent.name)
            for bf in sorted((project_root / "examples").glob("*/bot.py"))
        ],
    )
    def test_bot_import(self, bot_file):
        """Test that a bot can be imported."""
        bot_name = bot_file.parent.name

        # Add bot directory to path BEFORE loading for relative imports
        bot_dir = bot_file.parent
        if str(bot_dir) not in sys.path:
            sys.path.insert(0, str(bot_dir))

        # Load the module
        spec = importlib.util.spec_from_file_location(f"{bot_name}_module", bot_file)
        assert spec is not None, f"Failed to load spec for {bot_name}"
        assert spec.loader is not None, f"Failed to load loader for {bot_name}"

        module = importlib.util.module_from_spec(spec)
        sys.modules[f"{bot_name}_module"] = module

        # Import should not raise
        spec.loader.exec_module(module)

    @pytest.mark.parametrize(
        "bot_file",
        [
            pytest.param(bf, id=bf.parent.name)
            for bf in sorted((project_root / "examples").glob("*/bot.py"))
        ],
    )
    def test_bot_class_exists(self, bot_file):
        """Test that bot class exists in module."""
        bot_name = bot_file.parent.name

        # Add bot directory to path
        bot_dir = bot_file.parent
        if str(bot_dir) not in sys.path:
            sys.path.insert(0, str(bot_dir))

        # Load module
        spec = importlib.util.spec_from_file_location(f"{bot_name}_test", bot_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"{bot_name}_test"] = module
        spec.loader.exec_module(module)

        # Find bot classes
        bot_classes = []
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and attr_name.endswith("Bot")
                and attr.__module__ == module.__name__
            ):
                bot_classes.append((attr_name, attr))

        assert len(bot_classes) > 0, f"No bot class found in {bot_name}"

    @pytest.mark.parametrize(
        "bot_file",
        [
            pytest.param(bf, id=bf.parent.name)
            for bf in sorted((project_root / "examples").glob("*/bot.py"))
        ],
    )
    def test_bot_initialization(self, bot_file):
        """Test that bot can be initialized with new API."""
        bot_name = bot_file.parent.name

        # Add bot directory to path
        bot_dir = bot_file.parent
        if str(bot_dir) not in sys.path:
            sys.path.insert(0, str(bot_dir))

        # Load module
        spec = importlib.util.spec_from_file_location(f"{bot_name}_init_test", bot_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"{bot_name}_init_test"] = module
        spec.loader.exec_module(module)

        # Find bot class
        bot_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and attr_name.endswith("Bot")
                and attr.__module__ == module.__name__
            ):
                bot_class = attr
                break

        assert bot_class is not None, f"No bot class found in {bot_name}"

        # Create storage
        storage = create_storage("memory")

        # Initialize bot (should not raise)
        bot = bot_class(storage=storage, bot_name=f"Test {bot_name}")

        # Verify bot has required attributes
        assert hasattr(bot, "storage"), (
            f"{bot_class.__name__} missing storage attribute"
        )
        assert hasattr(bot, "user_manager"), (
            f"{bot_class.__name__} missing user_manager"
        )
        assert hasattr(bot, "admin_manager"), (
            f"{bot_class.__name__} missing admin_manager"
        )
        assert hasattr(bot, "register_handlers"), (
            f"{bot_class.__name__} missing register_handlers method"
        )

        # Verify storage is set correctly
        assert bot.storage is storage, f"{bot_class.__name__} storage not set correctly"

    @pytest.mark.parametrize(
        "bot_file",
        [
            pytest.param(bf, id=bf.parent.name)
            for bf in sorted((project_root / "examples").glob("*/bot.py"))
        ],
    )
    def test_bot_has_register_handlers(self, bot_file):
        """Test that bot has register_handlers method."""
        bot_name = bot_file.parent.name

        # Add bot directory to path
        bot_dir = bot_file.parent
        if str(bot_dir) not in sys.path:
            sys.path.insert(0, str(bot_dir))

        # Load module
        spec = importlib.util.spec_from_file_location(
            f"{bot_name}_handlers_test", bot_file
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"{bot_name}_handlers_test"] = module
        spec.loader.exec_module(module)

        # Find bot class
        bot_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and attr_name.endswith("Bot")
                and attr.__module__ == module.__name__
            ):
                bot_class = attr
                break

        assert bot_class is not None

        # Create bot instance
        storage = create_storage("memory")
        bot = bot_class(storage=storage, bot_name=f"Test {bot_name}")

        # Check register_handlers exists and is callable
        assert hasattr(bot, "register_handlers")
        assert callable(bot.register_handlers)


class TestExampleBotsIntegration:
    """Integration tests for example bots."""

    def test_all_bots_use_new_api(self):
        """Test that all bots use the new initialization API."""
        examples_dir = project_root / "examples"
        bot_files = list(examples_dir.glob("*/bot.py"))

        for bot_file in bot_files:
            bot_name = bot_file.parent.name
            content = bot_file.read_text()

            # Check that bot doesn't use old-style initialization
            # Old style: def __init__(self, token: str, storage, admin_ids: List[int])
            # New style: def __init__(self, storage, bot_name="...")

            # Should not have 'token' as first parameter after self
            assert "def __init__(self, token:" not in content, (
                f"{bot_name} still uses old-style initialization with token parameter"
            )

            # Should not have 'admin_ids' parameter
            assert "admin_ids: List[int]" not in content, (
                f"{bot_name} still uses old-style initialization with admin_ids parameter"
            )

    def test_all_bots_have_main_function(self):
        """Test that all bots have a main() function."""
        examples_dir = project_root / "examples"
        bot_files = list(examples_dir.glob("*/bot.py"))

        for bot_file in bot_files:
            bot_name = bot_file.parent.name
            content = bot_file.read_text()

            assert "def main():" in content, f"{bot_name} missing main() function"

            assert 'if __name__ == "__main__":' in content, (
                f"{bot_name} missing __main__ guard"
            )

    def test_all_bots_use_post_init_wrapper(self):
        """Test that all bots use post_init wrapper for set_bot_commands."""
        examples_dir = project_root / "examples"
        bot_files = list(examples_dir.glob("*/bot.py"))

        for bot_file in bot_files:
            bot_name = bot_file.parent.name
            content = bot_file.read_text()

            # Should use async wrapper
            assert "async def post_init_wrapper" in content, (
                f"{bot_name} missing post_init_wrapper"
            )

            assert "await bot.set_bot_commands()" in content, (
                f"{bot_name} not calling set_bot_commands correctly"
            )
