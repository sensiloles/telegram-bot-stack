"""Integration tests for complete user flows."""

from pathlib import Path

import pytest

from src.core.bot_base import BotBase
from src.core.storage import Storage


class TestFullUserFlow:
    """Test complete user registration and management flows."""

    @pytest.mark.asyncio
    async def test_user_registration_and_admin_flow(self, tmp_path: Path):
        """Test complete flow: registration, admin assignment, and management."""
        storage = Storage(tmp_path)
        bot = BotBase(
            storage=storage,
            bot_name="Integration Test Bot",
            user_commands=["/start", "/my_id"],
            admin_commands=[
                "/list_users",
                "/list_admins",
                "/add_admin",
                "/remove_admin",
            ]
            + ["/start", "/my_id"],
        )

        # Step 1: First user registers and becomes admin automatically
        assert bot.user_manager.add_user(12345) is True
        assert bot.admin_manager.add_admin(12345) is True
        assert bot.admin_manager.is_admin(12345) is True
        assert bot.admin_manager.has_admins() is True

        # Step 2: Second user registers as regular user
        assert bot.user_manager.add_user(67890) is True
        assert bot.admin_manager.is_admin(67890) is False

        # Step 3: First admin promotes second user to admin
        assert bot.admin_manager.add_admin(67890) is True
        assert bot.admin_manager.is_admin(67890) is True

        # Step 4: Verify both users are in system
        users = bot.user_manager.get_all_users()
        assert len(users) == 2
        assert 12345 in users
        assert 67890 in users

        # Step 5: Verify both are admins
        admins = bot.admin_manager.get_all_admins()
        assert len(admins) == 2
        assert 12345 in admins
        assert 67890 in admins

    @pytest.mark.asyncio
    async def test_admin_removal_and_last_admin_protection(self, tmp_path: Path):
        """Test admin removal flow with last admin protection."""
        storage = Storage(tmp_path)
        bot = BotBase(
            storage=storage,
            bot_name="Test Bot",
            user_commands=["/start"],
            admin_commands=["/remove_admin", "/start"],
        )

        # Setup: Three admins
        bot.admin_manager.add_admin(12345)
        bot.admin_manager.add_admin(67890)
        bot.admin_manager.add_admin(11111)

        # Remove first admin
        assert bot.admin_manager.remove_admin(12345) is True
        assert bot.admin_manager.is_admin(12345) is False
        assert bot.admin_manager.get_admin_count() == 2

        # Remove second admin
        assert bot.admin_manager.remove_admin(67890) is True
        assert bot.admin_manager.is_admin(67890) is False
        assert bot.admin_manager.get_admin_count() == 1

        # Cannot remove last admin
        assert bot.admin_manager.remove_admin(11111) is False
        assert bot.admin_manager.is_admin(11111) is True
        assert bot.admin_manager.get_admin_count() == 1
        assert bot.admin_manager.has_admins() is True

    @pytest.mark.asyncio
    async def test_data_persistence_across_bot_instances(self, tmp_path: Path):
        """Test that user and admin data persists across bot restarts."""
        storage = Storage(tmp_path)

        # First bot instance - register users and admins
        bot1 = BotBase(storage=storage, bot_name="Bot1")
        bot1.user_manager.add_user(12345)
        bot1.user_manager.add_user(67890)
        bot1.admin_manager.add_admin(12345)

        # Second bot instance - verify data persists
        bot2 = BotBase(storage=storage, bot_name="Bot2")

        # Users should be loaded from storage
        assert 12345 in bot2.user_manager.get_all_users()
        assert 67890 in bot2.user_manager.get_all_users()
        assert bot2.user_manager.get_user_count() == 2

        # Admins should be loaded from storage
        assert bot2.admin_manager.is_admin(12345) is True
        assert bot2.admin_manager.is_admin(67890) is False
        assert bot2.admin_manager.get_admin_count() == 1

    @pytest.mark.asyncio
    async def test_multiple_operations_sequence(self, tmp_path: Path):
        """Test sequence of multiple operations."""
        storage = Storage(tmp_path)
        bot = BotBase(storage=storage, bot_name="Test Bot")

        # Register multiple users
        for user_id in [100, 200, 300, 400, 500]:
            bot.user_manager.add_user(user_id)

        assert bot.user_manager.get_user_count() == 5

        # Make some users admins
        bot.admin_manager.add_admin(100)
        bot.admin_manager.add_admin(200)
        bot.admin_manager.add_admin(300)

        assert bot.admin_manager.get_admin_count() == 3

        # Remove some users
        bot.user_manager.remove_user(400)
        bot.user_manager.remove_user(500)

        assert bot.user_manager.get_user_count() == 3

        # Remove some admins
        bot.admin_manager.remove_admin(200)

        assert bot.admin_manager.get_admin_count() == 2
        assert bot.admin_manager.is_admin(100) is True
        assert bot.admin_manager.is_admin(300) is True

    @pytest.mark.asyncio
    async def test_storage_isolation_between_bots(self, tmp_path: Path):
        """Test that different bots with different storage don't interfere."""
        storage1 = Storage(tmp_path / "bot1")
        storage2 = Storage(tmp_path / "bot2")

        bot1 = BotBase(storage=storage1, bot_name="Bot1")
        bot2 = BotBase(storage=storage2, bot_name="Bot2")

        # Add users to different bots
        bot1.user_manager.add_user(12345)
        bot2.user_manager.add_user(67890)

        # Users should be isolated
        assert 12345 in bot1.user_manager.get_all_users()
        assert 12345 not in bot2.user_manager.get_all_users()
        assert 67890 in bot2.user_manager.get_all_users()
        assert 67890 not in bot1.user_manager.get_all_users()

    @pytest.mark.asyncio
    async def test_edge_case_empty_bot(self, tmp_path: Path):
        """Test bot behavior with no users or admins."""
        storage = Storage(tmp_path)
        bot = BotBase(storage=storage, bot_name="Empty Bot")

        # Initial state
        assert bot.user_manager.get_user_count() == 0
        assert bot.admin_manager.get_admin_count() == 0
        assert bot.admin_manager.has_admins() is False

        # Operations on empty state
        assert bot.user_manager.user_exists(99999) is False
        assert bot.admin_manager.is_admin(99999) is False
        assert bot.user_manager.remove_user(99999) is False
        assert bot.admin_manager.remove_admin(99999) is False

    @pytest.mark.asyncio
    async def test_concurrent_user_and_admin_operations(self, tmp_path: Path):
        """Test mixed user and admin operations."""
        storage = Storage(tmp_path)
        bot = BotBase(storage=storage, bot_name="Test Bot")

        # Add users
        bot.user_manager.add_user(12345)
        bot.user_manager.add_user(67890)

        # Make first user admin
        bot.admin_manager.add_admin(12345)

        # Regular user should not be admin
        assert bot.user_manager.user_exists(67890) is True
        assert bot.admin_manager.is_admin(67890) is False

        # Admin should be both user and admin
        assert bot.user_manager.user_exists(12345) is True
        assert bot.admin_manager.is_admin(12345) is True

        # Remove user who is also admin
        bot.user_manager.remove_user(12345)

        # User removed but admin status independent
        assert bot.user_manager.user_exists(12345) is False
        assert bot.admin_manager.is_admin(12345) is True

    @pytest.mark.asyncio
    async def test_bot_initialization_with_existing_data(self, tmp_path: Path):
        """Test bot initializes correctly with pre-existing data."""
        storage = Storage(tmp_path)

        # Pre-populate storage
        storage.save("bot_users.json", [12345, 67890, 11111])
        storage.save("bot_admins.json", [12345])

        # Create bot with existing data
        bot = BotBase(storage=storage, bot_name="Test Bot")

        # Should load existing data
        assert bot.user_manager.get_user_count() == 3
        assert bot.admin_manager.get_admin_count() == 1
        assert bot.admin_manager.is_admin(12345) is True
        assert bot.user_manager.user_exists(67890) is True

    @pytest.mark.asyncio
    async def test_full_lifecycle_first_user_scenario(self, tmp_path: Path):
        """Test complete lifecycle of first user becoming admin."""
        storage = Storage(tmp_path)
        bot = BotBase(storage=storage, bot_name="Test Bot")

        # Verify initial empty state
        assert bot.admin_manager.has_admins() is False
        assert bot.user_manager.get_user_count() == 0

        # First user joins
        user_id = 12345
        bot.user_manager.add_user(user_id)

        # Since no admins exist, make first user admin
        if not bot.admin_manager.has_admins():
            bot.admin_manager.add_admin(user_id)

        # Verify first user is admin
        assert bot.admin_manager.is_admin(user_id) is True
        assert bot.admin_manager.has_admins() is True

        # Second user joins
        second_user = 67890
        bot.user_manager.add_user(second_user)

        # Second user should NOT automatically become admin
        assert bot.admin_manager.is_admin(second_user) is False

        # Both users should be registered
        assert bot.user_manager.get_user_count() == 2
        assert bot.admin_manager.get_admin_count() == 1
