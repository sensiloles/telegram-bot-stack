"""Tests for AdminManager class."""

from pathlib import Path

from src.core.admin_manager import AdminManager
from src.core.storage import Storage


class TestAdminManager:
    """Test suite for AdminManager class."""

    def test_init_loads_existing_admins(self, tmp_path: Path):
        """Test that AdminManager loads existing admins on initialization."""
        storage = Storage(tmp_path)
        storage.save("test_admins.json", [12345, 67890])

        manager = AdminManager(storage, "test_admins")

        assert manager.is_admin(12345) is True
        assert manager.is_admin(67890) is True

    def test_init_empty_storage(self, admin_manager: AdminManager):
        """Test initialization with empty storage."""
        assert admin_manager.get_all_admins() == []
        assert admin_manager.get_admin_count() == 0
        assert admin_manager.has_admins() is False

    def test_add_new_admin(self, admin_manager: AdminManager):
        """Test adding a new admin."""
        result = admin_manager.add_admin(12345)

        assert result is True
        assert admin_manager.is_admin(12345) is True
        assert admin_manager.get_admin_count() == 1
        assert admin_manager.has_admins() is True

    def test_add_duplicate_admin(self, admin_manager: AdminManager):
        """Test that adding same admin twice returns False."""
        admin_manager.add_admin(12345)
        result = admin_manager.add_admin(12345)

        assert result is False
        assert admin_manager.get_admin_count() == 1

    def test_add_multiple_admins(self, admin_manager: AdminManager):
        """Test adding multiple different admins."""
        admin_manager.add_admin(12345)
        admin_manager.add_admin(67890)
        admin_manager.add_admin(11111)

        admins = admin_manager.get_all_admins()
        assert len(admins) == 3
        assert 12345 in admins
        assert 67890 in admins
        assert 11111 in admins

    def test_remove_admin_with_multiple_admins(self, admin_manager: AdminManager):
        """Test removing an admin when there are multiple admins."""
        admin_manager.add_admin(12345)
        admin_manager.add_admin(67890)

        result = admin_manager.remove_admin(12345)

        assert result is True
        assert admin_manager.is_admin(12345) is False
        assert admin_manager.is_admin(67890) is True
        assert admin_manager.get_admin_count() == 1

    def test_cannot_remove_last_admin(self, admin_manager: AdminManager):
        """Test that the last admin cannot be removed."""
        admin_manager.add_admin(12345)

        result = admin_manager.remove_admin(12345)

        assert result is False
        assert admin_manager.is_admin(12345) is True
        assert admin_manager.get_admin_count() == 1

    def test_remove_nonexistent_admin(self, admin_manager: AdminManager):
        """Test that removing non-existent admin returns False."""
        admin_manager.add_admin(12345)

        result = admin_manager.remove_admin(99999)

        assert result is False
        assert admin_manager.get_admin_count() == 1

    def test_is_admin(self, admin_manager: AdminManager):
        """Test checking if user is admin."""
        admin_manager.add_admin(12345)

        assert admin_manager.is_admin(12345) is True
        assert admin_manager.is_admin(99999) is False

    def test_get_all_admins_returns_copy(self, admin_manager: AdminManager):
        """Test that get_all_admins returns a copy."""
        admin_manager.add_admin(12345)

        admins1 = admin_manager.get_all_admins()
        admins2 = admin_manager.get_all_admins()

        assert admins1 == admins2
        assert admins1 is not admins2  # Different list objects

    def test_get_all_admins_immutable(self, admin_manager: AdminManager):
        """Test that modifying returned list doesn't affect internal state."""
        admin_manager.add_admin(12345)

        admins = admin_manager.get_all_admins()
        admins.append(99999)

        # Internal state should not be affected
        assert admin_manager.is_admin(99999) is False
        assert admin_manager.get_admin_count() == 1

    def test_get_admin_count_empty(self, admin_manager: AdminManager):
        """Test getting admin count when empty."""
        assert admin_manager.get_admin_count() == 0

    def test_get_admin_count_with_admins(self, admin_manager: AdminManager):
        """Test getting admin count with admins."""
        admin_manager.add_admin(12345)
        admin_manager.add_admin(67890)

        assert admin_manager.get_admin_count() == 2

    def test_has_admins_false_when_empty(self, admin_manager: AdminManager):
        """Test has_admins returns False when no admins."""
        assert admin_manager.has_admins() is False

    def test_has_admins_true_when_present(self, admin_manager: AdminManager):
        """Test has_admins returns True when admins exist."""
        admin_manager.add_admin(12345)

        assert admin_manager.has_admins() is True

    def test_persistence_across_instances(self, tmp_path: Path):
        """Test that admins persist across AdminManager instances."""
        storage = Storage(tmp_path)

        # First instance - add admins
        manager1 = AdminManager(storage, "test_admins")
        manager1.add_admin(12345)
        manager1.add_admin(67890)

        # Second instance - verify admins exist
        manager2 = AdminManager(storage, "test_admins")

        assert manager2.is_admin(12345) is True
        assert manager2.is_admin(67890) is True
        assert manager2.get_admin_count() == 2

    def test_save_admins_creates_file(self, admin_manager: AdminManager):
        """Test that save_admins creates a file in storage."""
        admin_manager.add_admin(12345)

        # Verify file was created
        filepath = admin_manager.storage.base_dir / f"{admin_manager.storage_key}.json"
        assert filepath.exists()

    def test_add_admin_saves_automatically(self, admin_manager: AdminManager):
        """Test that adding an admin automatically saves to storage."""
        admin_manager.add_admin(12345)

        # Load directly from storage to verify
        loaded = admin_manager.storage.load(admin_manager.storage_key)
        assert 12345 in loaded

    def test_remove_admin_saves_automatically(self, admin_manager: AdminManager):
        """Test that removing an admin automatically saves to storage."""
        admin_manager.add_admin(12345)
        admin_manager.add_admin(67890)
        admin_manager.add_admin(11111)

        admin_manager.remove_admin(67890)

        # Load directly from storage to verify
        loaded = admin_manager.storage.load(admin_manager.storage_key)
        assert 67890 not in loaded
        assert 12345 in loaded
        assert 11111 in loaded

    def test_remove_second_to_last_admin(self, admin_manager: AdminManager):
        """Test removing admin when two remain (should succeed)."""
        admin_manager.add_admin(12345)
        admin_manager.add_admin(67890)

        result = admin_manager.remove_admin(67890)

        assert result is True
        assert admin_manager.is_admin(67890) is False
        assert admin_manager.get_admin_count() == 1

    def test_add_remove_add_same_admin(self, admin_manager: AdminManager):
        """Test adding, removing (with multiple admins), then adding same admin again."""
        admin_manager.add_admin(12345)
        admin_manager.add_admin(67890)  # Need 2 to remove one

        admin_manager.remove_admin(12345)
        result = admin_manager.add_admin(12345)

        assert result is True
        assert admin_manager.is_admin(12345) is True

    def test_custom_storage_key(self, temp_storage: Storage):
        """Test using custom storage key."""
        manager1 = AdminManager(temp_storage, "custom_admins")
        manager2 = AdminManager(temp_storage, "other_admins")

        manager1.add_admin(12345)
        manager2.add_admin(67890)

        # Admins should be in separate storage
        assert manager1.is_admin(12345) is True
        assert manager1.is_admin(67890) is False
        assert manager2.is_admin(67890) is True
        assert manager2.is_admin(12345) is False

    def test_admin_ids_as_integers(self, admin_manager: AdminManager):
        """Test that admin IDs are stored as integers."""
        admin_manager.add_admin(12345)

        admins = admin_manager.get_all_admins()
        assert isinstance(admins[0], int)

    def test_zero_admin_id(self, admin_manager: AdminManager):
        """Test handling admin ID of 0."""
        result = admin_manager.add_admin(0)

        assert result is True
        assert admin_manager.is_admin(0) is True

    def test_negative_admin_id(self, admin_manager: AdminManager):
        """Test handling negative admin IDs."""
        result = admin_manager.add_admin(-12345)

        assert result is True
        assert admin_manager.is_admin(-12345) is True

    def test_very_large_admin_id(self, admin_manager: AdminManager):
        """Test handling very large admin IDs."""
        large_id = 9999999999999

        result = admin_manager.add_admin(large_id)

        assert result is True
        assert admin_manager.is_admin(large_id) is True

    def test_multiple_attempts_to_remove_last_admin(self, admin_manager: AdminManager):
        """Test multiple attempts to remove the last admin all fail."""
        admin_manager.add_admin(12345)

        result1 = admin_manager.remove_admin(12345)
        result2 = admin_manager.remove_admin(12345)

        assert result1 is False
        assert result2 is False
        assert admin_manager.is_admin(12345) is True

    def test_remove_from_empty_list(self, admin_manager: AdminManager):
        """Test removing from empty admin list."""
        result = admin_manager.remove_admin(12345)

        assert result is False
        assert admin_manager.get_admin_count() == 0

    def test_large_admin_count(self, admin_manager: AdminManager):
        """Test handling large number of admins."""
        num_admins = 100

        # Add many admins
        for i in range(num_admins):
            admin_manager.add_admin(i)

        assert admin_manager.get_admin_count() == num_admins
        assert admin_manager.has_admins() is True

        # Can remove all but one
        for i in range(1, num_admins):
            result = admin_manager.remove_admin(i)
            assert result is True

        # Cannot remove the last one
        assert admin_manager.remove_admin(0) is False
        assert admin_manager.get_admin_count() == 1
