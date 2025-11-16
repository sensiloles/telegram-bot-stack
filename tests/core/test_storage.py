"""Tests for Storage abstraction layer."""

from pathlib import Path

from src.core.storage import Storage


class TestStorage:
    """Test suite for Storage class."""

    def test_init_creates_directory(self, tmp_path: Path):
        """Test that Storage creates base directory if it doesn't exist."""
        storage_dir = tmp_path / "new_storage"
        assert not storage_dir.exists()

        storage = Storage(storage_dir)

        assert storage_dir.exists()
        assert storage_dir.is_dir()
        assert storage.base_dir == storage_dir

    def test_save_creates_file(self, temp_storage: Storage):
        """Test that save() creates a new file."""
        key = "test_data"
        data = {"name": "test", "value": 42}

        result = temp_storage.save(key, data)

        assert result is True
        filepath = temp_storage._get_filepath(key)
        assert filepath.exists()

    def test_save_and_load(self, temp_storage: Storage):
        """Test saving and loading data."""
        key = "test_data"
        data = {"name": "test", "value": 42, "nested": {"key": "value"}}

        # Save data
        assert temp_storage.save(key, data) is True

        # Load data
        loaded = temp_storage.load(key)
        assert loaded == data

    def test_save_overwrites_existing(self, temp_storage: Storage):
        """Test that save() overwrites existing data."""
        key = "test_data"
        original_data = {"version": 1}
        new_data = {"version": 2}

        temp_storage.save(key, original_data)
        temp_storage.save(key, new_data)

        loaded = temp_storage.load(key)
        assert loaded == new_data

    def test_load_nonexistent_returns_default(self, temp_storage: Storage):
        """Test that loading non-existent key returns default value."""
        result = temp_storage.load("nonexistent")
        assert result == []

    def test_load_with_custom_default(self, temp_storage: Storage):
        """Test loading with custom default value."""
        default = {"custom": "default"}
        result = temp_storage.load("nonexistent", default=default)
        assert result == default

    def test_exists_returns_true_for_existing(self, temp_storage: Storage):
        """Test that exists() returns True for existing keys."""
        key = "test_data"
        temp_storage.save(key, {"data": "value"})

        assert temp_storage.exists(key) is True

    def test_exists_returns_false_for_missing(self, temp_storage: Storage):
        """Test that exists() returns False for missing keys."""
        assert temp_storage.exists("nonexistent") is False

    def test_delete_existing_file(self, temp_storage: Storage):
        """Test deleting an existing file."""
        key = "test_data"
        temp_storage.save(key, {"data": "value"})

        # Verify file exists
        assert temp_storage.exists(key) is True

        # Delete file
        result = temp_storage.delete(key)

        assert result is True
        assert temp_storage.exists(key) is False

    def test_delete_nonexistent_file(self, temp_storage: Storage):
        """Test deleting a non-existent file returns False."""
        result = temp_storage.delete("nonexistent")
        assert result is False

    def test_get_filepath_adds_json_extension(self, temp_storage: Storage):
        """Test that _get_filepath adds .json extension if missing."""
        filepath = temp_storage._get_filepath("test_key")
        assert filepath.name == "test_key.json"

    def test_get_filepath_preserves_json_extension(self, temp_storage: Storage):
        """Test that _get_filepath doesn't double-add .json extension."""
        filepath = temp_storage._get_filepath("test_key.json")
        assert filepath.name == "test_key.json"
        assert not filepath.name.endswith(".json.json")

    def test_save_complex_data_types(self, temp_storage: Storage):
        """Test saving various data types."""
        data = {
            "string": "text",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
            "nested_dict": {"a": 1, "b": 2},
            "nested_list": [[1, 2], [3, 4]],
        }

        temp_storage.save("complex", data)
        loaded = temp_storage.load("complex")

        assert loaded == data

    def test_save_unicode_data(self, temp_storage: Storage):
        """Test saving Unicode/Russian text."""
        data = {
            "russian": "Привет мир",
            "emoji": "🚀🎉",
            "mixed": "Hello мир 🌍",
        }

        temp_storage.save("unicode", data)
        loaded = temp_storage.load("unicode")

        assert loaded == data

    def test_save_empty_dict(self, temp_storage: Storage):
        """Test saving empty dictionary."""
        data = {}

        temp_storage.save("empty", data)
        loaded = temp_storage.load("empty")

        assert loaded == data

    def test_save_empty_list(self, temp_storage: Storage):
        """Test saving empty list."""
        data = []

        temp_storage.save("empty_list", data)
        loaded = temp_storage.load("empty_list")

        assert loaded == data

    def test_multiple_keys_in_same_storage(self, temp_storage: Storage):
        """Test storing multiple different keys."""
        data1 = {"key": "value1"}
        data2 = {"key": "value2"}
        data3 = {"key": "value3"}

        temp_storage.save("key1", data1)
        temp_storage.save("key2", data2)
        temp_storage.save("key3", data3)

        assert temp_storage.load("key1") == data1
        assert temp_storage.load("key2") == data2
        assert temp_storage.load("key3") == data3

    def test_filepath_in_base_dir(self, temp_storage: Storage):
        """Test that generated filepath is within base directory."""
        filepath = temp_storage._get_filepath("test")
        assert filepath.parent == temp_storage.base_dir

    def test_json_formatting(self, temp_storage: Storage):
        """Test that saved JSON is properly formatted."""
        data = {"a": 1, "b": 2}
        temp_storage.save("formatted", data)

        filepath = temp_storage._get_filepath("formatted")
        with open(filepath) as f:
            content = f.read()

        # Check that JSON is indented (not single line)
        assert "\n" in content
        assert "  " in content  # Check for indentation

    def test_persistence_across_instances(self, tmp_path: Path):
        """Test that data persists across Storage instances."""
        key = "persistent"
        data = {"persist": True}

        # First instance - save data
        storage1 = Storage(tmp_path)
        storage1.save(key, data)

        # Second instance - load data
        storage2 = Storage(tmp_path)
        loaded = storage2.load(key)

        assert loaded == data

    def test_concurrent_keys_dont_interfere(self, temp_storage: Storage):
        """Test that operations on different keys don't interfere."""
        temp_storage.save("key1", {"value": 1})
        temp_storage.save("key2", {"value": 2})

        temp_storage.delete("key1")

        assert temp_storage.exists("key1") is False
        assert temp_storage.exists("key2") is True
        assert temp_storage.load("key2") == {"value": 2}

    def test_save_with_permission_error(self, temp_storage: Storage, monkeypatch):
        """Test save handles permission errors gracefully."""
        import builtins

        original_open = builtins.open

        def mock_open(*args, **kwargs):
            if "w" in str(kwargs.get("mode", args[1] if len(args) > 1 else "")):
                raise PermissionError("Permission denied")
            return original_open(*args, **kwargs)

        monkeypatch.setattr("builtins.open", mock_open)

        result = temp_storage.save("test", {"data": "value"})
        assert result is False

    def test_load_with_json_decode_error(self, temp_storage: Storage):
        """Test load handles corrupted JSON files."""
        key = "corrupted"
        filepath = temp_storage._get_filepath(key)

        # Create corrupted JSON file
        with open(filepath, "w") as f:
            f.write("{ invalid json }")

        result = temp_storage.load(key, default={"default": True})
        assert result == {"default": True}

    def test_delete_with_permission_error(self, temp_storage: Storage, monkeypatch):
        """Test delete handles permission errors."""
        key = "test_delete"
        temp_storage.save(key, {"data": "value"})

        import pathlib

        original_unlink = pathlib.Path.unlink

        def mock_unlink(self, *args, **kwargs):
            raise PermissionError("Permission denied")

        monkeypatch.setattr(pathlib.Path, "unlink", mock_unlink)

        result = temp_storage.delete(key)
        assert result is False
