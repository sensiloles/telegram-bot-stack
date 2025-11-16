"""Tests for UserManager class."""

from pathlib import Path

from src.core.storage import Storage
from src.core.user_manager import UserManager


class TestUserManager:
    """Test suite for UserManager class."""

    def test_init_loads_existing_users(self, tmp_path: Path):
        """Test that UserManager loads existing users on initialization."""
        storage = Storage(tmp_path)
        storage.save("test_users.json", [12345, 67890])

        manager = UserManager(storage, "test_users")

        assert 12345 in manager.get_all_users()
        assert 67890 in manager.get_all_users()

    def test_init_empty_storage(self, user_manager: UserManager):
        """Test initialization with empty storage."""
        assert user_manager.get_all_users() == []
        assert user_manager.get_user_count() == 0

    def test_add_new_user(self, user_manager: UserManager):
        """Test adding a new user."""
        result = user_manager.add_user(12345)

        assert result is True
        assert 12345 in user_manager.get_all_users()
        assert user_manager.get_user_count() == 1

    def test_add_duplicate_user(self, user_manager: UserManager):
        """Test that adding same user twice returns False."""
        user_manager.add_user(12345)
        result = user_manager.add_user(12345)

        assert result is False
        assert user_manager.get_user_count() == 1

    def test_add_multiple_users(self, user_manager: UserManager):
        """Test adding multiple different users."""
        user_manager.add_user(12345)
        user_manager.add_user(67890)
        user_manager.add_user(11111)

        users = user_manager.get_all_users()
        assert len(users) == 3
        assert 12345 in users
        assert 67890 in users
        assert 11111 in users

    def test_remove_existing_user(self, user_manager: UserManager):
        """Test removing an existing user."""
        user_manager.add_user(12345)

        result = user_manager.remove_user(12345)

        assert result is True
        assert 12345 not in user_manager.get_all_users()
        assert user_manager.get_user_count() == 0

    def test_remove_nonexistent_user(self, user_manager: UserManager):
        """Test that removing non-existent user returns False."""
        result = user_manager.remove_user(99999)

        assert result is False

    def test_user_exists(self, user_manager: UserManager):
        """Test checking if user exists."""
        user_manager.add_user(12345)

        assert user_manager.user_exists(12345) is True
        assert user_manager.user_exists(99999) is False

    def test_get_all_users_returns_copy(self, user_manager: UserManager):
        """Test that get_all_users returns a copy, not the original list."""
        user_manager.add_user(12345)

        users1 = user_manager.get_all_users()
        users2 = user_manager.get_all_users()

        assert users1 == users2
        assert users1 is not users2  # Different list objects

    def test_get_all_users_immutable(self, user_manager: UserManager):
        """Test that modifying returned list doesn't affect internal state."""
        user_manager.add_user(12345)

        users = user_manager.get_all_users()
        users.append(99999)

        # Internal state should not be affected
        assert 99999 not in user_manager.get_all_users()
        assert user_manager.get_user_count() == 1

    def test_get_user_count_empty(self, user_manager: UserManager):
        """Test getting user count when empty."""
        assert user_manager.get_user_count() == 0

    def test_get_user_count_with_users(self, user_manager: UserManager):
        """Test getting user count with users."""
        user_manager.add_user(12345)
        user_manager.add_user(67890)

        assert user_manager.get_user_count() == 2

    def test_persistence_across_instances(self, tmp_path: Path):
        """Test that users persist across UserManager instances."""
        storage = Storage(tmp_path)

        # First instance - add users
        manager1 = UserManager(storage, "test_users")
        manager1.add_user(12345)
        manager1.add_user(67890)

        # Second instance - verify users exist
        manager2 = UserManager(storage, "test_users")
        users = manager2.get_all_users()

        assert len(users) == 2
        assert 12345 in users
        assert 67890 in users

    def test_save_users_creates_file(self, user_manager: UserManager, tmp_path: Path):
        """Test that save_users creates a file in storage."""
        user_manager.add_user(12345)

        # Verify file was created
        filepath = user_manager.storage.base_dir / f"{user_manager.storage_key}.json"
        assert filepath.exists()

    def test_add_user_saves_automatically(self, user_manager: UserManager):
        """Test that adding a user automatically saves to storage."""
        user_manager.add_user(12345)

        # Load directly from storage to verify
        loaded = user_manager.storage.load(user_manager.storage_key)
        assert 12345 in loaded

    def test_remove_user_saves_automatically(self, user_manager: UserManager):
        """Test that removing a user automatically saves to storage."""
        user_manager.add_user(12345)
        user_manager.add_user(67890)
        user_manager.remove_user(12345)

        # Load directly from storage to verify
        loaded = user_manager.storage.load(user_manager.storage_key)
        assert 12345 not in loaded
        assert 67890 in loaded

    def test_large_user_count(self, user_manager: UserManager):
        """Test handling large number of users."""
        num_users = 1000

        # Add many users
        for i in range(num_users):
            user_manager.add_user(i)

        assert user_manager.get_user_count() == num_users

        # Verify all users exist
        users = user_manager.get_all_users()
        assert len(users) == num_users
        assert 0 in users
        assert 999 in users

    def test_remove_from_empty_list(self, user_manager: UserManager):
        """Test removing from empty user list."""
        result = user_manager.remove_user(12345)

        assert result is False
        assert user_manager.get_user_count() == 0

    def test_add_remove_add_same_user(self, user_manager: UserManager):
        """Test adding, removing, then adding the same user again."""
        user_manager.add_user(12345)
        user_manager.remove_user(12345)
        result = user_manager.add_user(12345)

        assert result is True
        assert user_manager.user_exists(12345) is True
        assert user_manager.get_user_count() == 1

    def test_custom_storage_key(self, temp_storage: Storage):
        """Test using custom storage key."""
        manager1 = UserManager(temp_storage, "custom_users")
        manager2 = UserManager(temp_storage, "other_users")

        manager1.add_user(12345)
        manager2.add_user(67890)

        # Users should be in separate storage
        assert 12345 in manager1.get_all_users()
        assert 12345 not in manager2.get_all_users()
        assert 67890 in manager2.get_all_users()
        assert 67890 not in manager1.get_all_users()

    def test_user_ids_as_integers(self, user_manager: UserManager):
        """Test that user IDs are stored as integers."""
        user_manager.add_user(12345)

        users = user_manager.get_all_users()
        assert isinstance(users[0], int)

    def test_zero_user_id(self, user_manager: UserManager):
        """Test handling user ID of 0."""
        result = user_manager.add_user(0)

        assert result is True
        assert 0 in user_manager.get_all_users()

    def test_negative_user_id(self, user_manager: UserManager):
        """Test handling negative user IDs."""
        result = user_manager.add_user(-12345)

        assert result is True
        assert -12345 in user_manager.get_all_users()

    def test_very_large_user_id(self, user_manager: UserManager):
        """Test handling very large user IDs."""
        large_id = 9999999999999

        result = user_manager.add_user(large_id)

        assert result is True
        assert large_id in user_manager.get_all_users()
