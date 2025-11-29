"""Tests for dependency management utilities."""

from telegram_bot_stack.cli.utils.dependencies import (
    _normalize_package_name,
    get_telegram_bot_stack_version,
)


class TestNormalizePackageName:
    """Tests for package name normalization."""

    def test_normalize_simple_name(self):
        """Test normalization of simple package name."""
        assert _normalize_package_name("my-bot") == "my-bot"
        assert _normalize_package_name("mybot") == "mybot"

    def test_normalize_name_with_leading_dot(self):
        """Test normalization of name with leading dot."""
        assert _normalize_package_name(".test-bot") == "test-bot"
        assert _normalize_package_name("...bot") == "bot"

    def test_normalize_name_with_underscores(self):
        """Test normalization replaces underscores with hyphens."""
        assert _normalize_package_name("my_bot") == "my-bot"
        assert _normalize_package_name("test_bot_2") == "test-bot-2"

    def test_normalize_name_with_multiple_special_chars(self):
        """Test normalization of name with multiple special characters."""
        assert _normalize_package_name("...weird___name---") == "weird-name"
        assert _normalize_package_name("__test__bot__") == "test-bot"

    def test_normalize_name_with_consecutive_hyphens(self):
        """Test normalization removes consecutive hyphens."""
        assert _normalize_package_name("test---bot") == "test-bot"
        assert _normalize_package_name("my--bot--name") == "my-bot-name"

    def test_normalize_name_with_trailing_special_chars(self):
        """Test normalization removes trailing dots and hyphens."""
        assert _normalize_package_name("test-bot...") == "test-bot"
        assert _normalize_package_name("my-bot---") == "my-bot"
        assert _normalize_package_name("bot-.-.-") == "bot"

    def test_normalize_name_with_invalid_chars(self):
        """Test normalization replaces invalid characters."""
        assert _normalize_package_name("my@bot") == "my-bot"
        assert _normalize_package_name("test#bot") == "test-bot"
        assert _normalize_package_name("bot$name") == "bot-name"

    def test_normalize_empty_or_only_special_chars(self):
        """Test normalization of empty or only special characters."""
        assert _normalize_package_name("") == "bot-project"
        assert _normalize_package_name("...") == "bot-project"
        assert _normalize_package_name("___") == "bot-project"
        assert _normalize_package_name("---") == "bot-project"

    def test_normalize_name_preserves_alphanumeric(self):
        """Test normalization preserves alphanumeric characters."""
        assert _normalize_package_name("bot123") == "bot123"
        assert _normalize_package_name("my2bot") == "my2bot"

    def test_normalize_name_with_dots_in_middle(self):
        """Test normalization preserves dots in middle (valid in PEP 508)."""
        assert _normalize_package_name("my.bot") == "my.bot"
        assert _normalize_package_name("telegram.bot.stack") == "telegram.bot.stack"

    def test_normalize_real_world_examples(self):
        """Test normalization with real-world examples."""
        # User's original case
        assert _normalize_package_name(".test-bot") == "test-bot"

        # Common patterns
        assert _normalize_package_name("my_awesome_bot") == "my-awesome-bot"
        assert _normalize_package_name(".hidden_bot") == "hidden-bot"
        assert _normalize_package_name("_private_bot_") == "private-bot"


class TestGetTelegramBotStackVersion:
    """Tests for get_telegram_bot_stack_version function."""

    def test_get_version_returns_string(self):
        """Test that get_version returns a string."""
        version = get_telegram_bot_stack_version()
        assert isinstance(version, str)
        assert len(version) > 0

    def test_get_version_format(self):
        """Test that version follows semantic versioning format."""
        version = get_telegram_bot_stack_version()
        # Should be in format X.Y.Z
        parts = version.split(".")
        assert len(parts) >= 2  # At least major.minor
        assert all(part.isdigit() for part in parts[:2])  # Major and minor are digits

    def test_get_version_is_current(self):
        """Test that version matches expected current version."""
        version = get_telegram_bot_stack_version()
        # Should be 1.34.0 or higher
        major, minor = version.split(".")[:2]
        assert int(major) >= 1
        if int(major) == 1:
            assert int(minor) >= 34  # Current version at time of writing
