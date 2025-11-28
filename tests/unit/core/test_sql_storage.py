"""Tests for SQL storage backend."""

import pytest

from telegram_bot_stack.storage.sql import SQLStorage


class TestSQLiteStorage:
    """Test SQLStorage with SQLite backend (in-memory)."""

    @pytest.fixture
    def storage(self):
        """Create in-memory SQLite storage for testing."""
        storage = SQLStorage(database_url="sqlite:///:memory:")
        yield storage
        storage.close()

    def test_initialization(self, storage):
        """Test storage initialization and table creation."""
        assert storage is not None
        assert storage.database_url == "sqlite:///:memory:"

    def test_save_and_load(self, storage):
        """Test basic save and load operations."""
        test_data = {"user1": {"name": "John", "age": 30}}

        # Save data
        result = storage.save("users", test_data)
        assert result is True

        # Load data
        loaded_data = storage.load("users")
        assert loaded_data == test_data

    def test_save_overwrites_existing(self, storage):
        """Test that save overwrites existing data."""
        # Save initial data
        storage.save("counter", {"count": 1})

        # Overwrite with new data
        storage.save("counter", {"count": 2})

        # Load and verify
        loaded_data = storage.load("counter")
        assert loaded_data == {"count": 2}

    def test_load_nonexistent_key(self, storage):
        """Test loading non-existent key returns default."""
        # Load with default
        result = storage.load("nonexistent", default={"empty": True})
        assert result == {"empty": True}

        # Load without explicit default (should return [])
        result = storage.load("nonexistent")
        assert result == []

    def test_exists(self, storage):
        """Test exists method."""
        # Non-existent key
        assert storage.exists("test_key") is False

        # Save and check again
        storage.save("test_key", {"data": "value"})
        assert storage.exists("test_key") is True

    def test_delete(self, storage):
        """Test delete operation."""
        # Save data
        storage.save("to_delete", {"data": "value"})
        assert storage.exists("to_delete") is True

        # Delete
        result = storage.delete("to_delete")
        assert result is True
        assert storage.exists("to_delete") is False

        # Delete non-existent key
        result = storage.delete("nonexistent")
        assert result is False

    def test_save_complex_data(self, storage):
        """Test saving complex nested data structures."""
        complex_data = {
            "users": {
                "user1": {
                    "name": "John",
                    "age": 30,
                    "tags": ["admin", "developer"],
                    "metadata": {"created": "2024-01-01", "active": True},
                }
            },
            "settings": {"theme": "dark", "notifications": True},
        }

        storage.save("complex", complex_data)
        loaded_data = storage.load("complex")
        assert loaded_data == complex_data

    def test_save_list_data(self, storage):
        """Test saving list data."""
        list_data = [1, 2, 3, 4, 5]

        storage.save("numbers", list_data)
        loaded_data = storage.load("numbers")
        assert loaded_data == list_data

    def test_save_unicode_data(self, storage):
        """Test saving unicode data."""
        unicode_data = {
            "russian": "Привет мир",
            "chinese": "你好世界",
            "emoji": "🚀🎉",
        }

        storage.save("unicode", unicode_data)
        loaded_data = storage.load("unicode")
        assert loaded_data == unicode_data

    def test_multiple_keys(self, storage):
        """Test working with multiple keys simultaneously."""
        # Save multiple keys
        storage.save("key1", {"data": "value1"})
        storage.save("key2", {"data": "value2"})
        storage.save("key3", {"data": "value3"})

        # Verify all exist
        assert storage.exists("key1") is True
        assert storage.exists("key2") is True
        assert storage.exists("key3") is True

        # Load and verify
        assert storage.load("key1") == {"data": "value1"}
        assert storage.load("key2") == {"data": "value2"}
        assert storage.load("key3") == {"data": "value3"}

        # Delete one
        storage.delete("key2")
        assert storage.exists("key1") is True
        assert storage.exists("key2") is False
        assert storage.exists("key3") is True

    def test_empty_data(self, storage):
        """Test saving empty data structures."""
        # Empty dict
        storage.save("empty_dict", {})
        assert storage.load("empty_dict") == {}

        # Empty list
        storage.save("empty_list", [])
        assert storage.load("empty_list") == []

    def test_boolean_and_none_values(self, storage):
        """Test saving boolean and None values."""
        test_data = {
            "bool_true": True,
            "bool_false": False,
            "null_value": None,
            "mixed": [True, False, None, "string", 123],
        }

        storage.save("special_values", test_data)
        loaded_data = storage.load("special_values")
        assert loaded_data == test_data

    def test_numeric_values(self, storage):
        """Test saving various numeric types."""
        numeric_data = {
            "integer": 42,
            "float": 3.14159,
            "negative": -100,
            "zero": 0,
            "large": 999999999999,
        }

        storage.save("numbers", numeric_data)
        loaded_data = storage.load("numbers")
        assert loaded_data == numeric_data

    def test_save_invalid_json(self, storage):
        """Test that save fails gracefully with non-serializable data."""

        # Create non-serializable object
        class CustomObject:
            pass

        invalid_data = {"object": CustomObject()}

        # Should return False
        result = storage.save("invalid", invalid_data)
        assert result is False

        # Key should not exist
        assert storage.exists("invalid") is False


class TestSQLiteStorageFile:
    """Test SQLStorage with file-based SQLite."""

    @pytest.fixture
    def storage(self, tmp_path):
        """Create file-based SQLite storage for testing."""
        db_path = tmp_path / "test.db"
        storage = SQLStorage(database_url=f"sqlite:///{db_path}")
        yield storage
        storage.close()

    def test_persistence(self, storage, tmp_path):
        """Test that data persists across storage instances."""
        # Save data
        storage.save("persistent", {"value": "test"})
        storage.close()

        # Create new storage instance with same database
        db_path = tmp_path / "test.db"
        storage2 = SQLStorage(database_url=f"sqlite:///{db_path}")

        # Data should still exist
        assert storage2.exists("persistent") is True
        assert storage2.load("persistent") == {"value": "test"}

        storage2.close()


class TestSQLStorageFactory:
    """Test SQL storage creation via factory function."""

    def test_create_sqlite_storage(self):
        """Test creating SQLite storage via factory."""
        from telegram_bot_stack.storage import create_storage

        storage = create_storage("sqlite", database_url="sqlite:///:memory:")
        assert isinstance(storage, SQLStorage)
        assert storage.database_url == "sqlite:///:memory:"
        storage.close()

    def test_create_sqlite_default_url(self):
        """Test creating SQLite storage with default URL."""
        from telegram_bot_stack.storage import create_storage

        storage = create_storage("sqlite")
        assert isinstance(storage, SQLStorage)
        assert storage.database_url == "sqlite:///bot.db"
        storage.close()

    def test_create_postgres_without_url_raises(self):
        """Test that PostgreSQL requires database_url."""
        from telegram_bot_stack.storage import create_storage

        with pytest.raises(ValueError, match="requires 'database_url' parameter"):
            create_storage("postgres")

    def test_sql_alias(self):
        """Test that 'sql' backend type works."""
        from telegram_bot_stack.storage import create_storage

        storage = create_storage("sql", database_url="sqlite:///:memory:")
        assert isinstance(storage, SQLStorage)
        storage.close()


class TestSQLStorageCompatibility:
    """Test SQLStorage compatibility with other backends."""

    @pytest.fixture
    def sql_storage(self):
        """Create SQL storage."""
        storage = SQLStorage(database_url="sqlite:///:memory:")
        yield storage
        storage.close()

    @pytest.fixture
    def json_storage(self, tmp_path):
        """Create JSON storage."""
        from telegram_bot_stack.storage import JSONStorage

        return JSONStorage(base_dir=tmp_path)

    @pytest.fixture
    def memory_storage(self):
        """Create memory storage."""
        from telegram_bot_stack.storage import MemoryStorage

        return MemoryStorage()

    def test_same_interface_as_json(self, sql_storage, json_storage):
        """Test that SQL storage has same interface as JSON storage."""
        test_data = {"key": "value"}

        # Both should support same operations
        assert sql_storage.save("test", test_data) is True
        assert json_storage.save("test", test_data) is True

        assert sql_storage.load("test") == test_data
        assert json_storage.load("test") == test_data

        assert sql_storage.exists("test") is True
        assert json_storage.exists("test") is True

        assert sql_storage.delete("test") is True
        assert json_storage.delete("test") is True

    def test_same_interface_as_memory(self, sql_storage, memory_storage):
        """Test that SQL storage has same interface as memory storage."""
        test_data = {"key": "value"}

        # Both should support same operations
        assert sql_storage.save("test", test_data) is True
        assert memory_storage.save("test", test_data) is True

        assert sql_storage.load("test") == test_data
        assert memory_storage.load("test") == test_data

        assert sql_storage.exists("test") is True
        assert memory_storage.exists("test") is True

        assert sql_storage.delete("test") is True
        assert memory_storage.delete("test") is True

    def test_default_behavior_matches(self, sql_storage, json_storage, memory_storage):
        """Test that default behavior matches across all backends."""
        # All should return [] for non-existent keys
        assert sql_storage.load("nonexistent") == []
        assert json_storage.load("nonexistent") == []
        assert memory_storage.load("nonexistent") == []

        # All should return custom default
        default = {"custom": True}
        assert sql_storage.load("nonexistent", default=default) == default
        assert json_storage.load("nonexistent", default=default) == default
        assert memory_storage.load("nonexistent", default=default) == default

        # All should return False for non-existent exists
        assert sql_storage.exists("nonexistent") is False
        assert json_storage.exists("nonexistent") is False
        assert memory_storage.exists("nonexistent") is False

        # All should return False for non-existent delete
        assert sql_storage.delete("nonexistent") is False
        assert json_storage.delete("nonexistent") is False
        assert memory_storage.delete("nonexistent") is False


class TestSQLStorageEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def storage(self):
        """Create in-memory SQLite storage for testing."""
        storage = SQLStorage(database_url="sqlite:///:memory:")
        yield storage
        storage.close()

    def test_very_long_key(self, storage):
        """Test handling of long keys (within limit)."""
        long_key = "k" * 200  # Within 255 char limit
        storage.save(long_key, {"data": "value"})
        assert storage.exists(long_key) is True
        assert storage.load(long_key) == {"data": "value"}

    def test_special_characters_in_key(self, storage):
        """Test keys with special characters."""
        special_keys = [
            "key-with-dashes",
            "key_with_underscores",
            "key.with.dots",
            "key:with:colons",
            "key/with/slashes",
        ]

        for key in special_keys:
            storage.save(key, {"key": key})
            assert storage.exists(key) is True
            assert storage.load(key) == {"key": key}

    def test_large_data(self, storage):
        """Test handling of large data structures."""
        # Create large data structure
        large_data = {"items": [{"id": i, "data": f"item_{i}"} for i in range(1000)]}

        storage.save("large", large_data)
        loaded_data = storage.load("large")
        assert loaded_data == large_data
        assert len(loaded_data["items"]) == 1000

    def test_concurrent_operations(self, storage):
        """Test multiple operations in sequence."""
        # Simulate concurrent-like operations
        for i in range(10):
            storage.save(f"key_{i}", {"value": i})

        # Verify all saved
        for i in range(10):
            assert storage.exists(f"key_{i}") is True
            assert storage.load(f"key_{i}") == {"value": i}

        # Delete half
        for i in range(0, 10, 2):
            storage.delete(f"key_{i}")

        # Verify deletion
        for i in range(10):
            if i % 2 == 0:
                assert storage.exists(f"key_{i}") is False
            else:
                assert storage.exists(f"key_{i}") is True

    def test_close_and_reopen(self, tmp_path):
        """Test closing and reopening storage."""
        # Use file-based storage for persistence test
        db_path = tmp_path / "test.db"
        storage = SQLStorage(database_url=f"sqlite:///{db_path}")

        # Save data
        storage.save("test", {"data": "value"})

        # Close storage
        storage.close()

        # Reopen storage with same database
        storage2 = SQLStorage(database_url=f"sqlite:///{db_path}")

        # Data should persist
        assert storage2.exists("test") is True
        assert storage2.load("test") == {"data": "value"}

        storage2.close()


class TestSQLStorageConfiguration:
    """Test various configuration options."""

    def test_echo_mode(self):
        """Test SQL echo mode."""
        storage = SQLStorage(database_url="sqlite:///:memory:", echo=False)
        assert storage.echo is False
        storage.close()

    def test_pool_configuration(self):
        """Test connection pool configuration (PostgreSQL)."""
        # Note: This just tests that parameters are accepted
        # Actual pooling behavior would need a real PostgreSQL instance
        storage = SQLStorage(
            database_url="sqlite:///:memory:", pool_size=10, max_overflow=20
        )
        storage.close()

    def test_invalid_database_url(self):
        """Test handling of invalid database URL."""
        # SQLAlchemy will raise an error for invalid URLs
        with pytest.raises((ValueError, Exception)):
            SQLStorage(database_url="invalid://url")
