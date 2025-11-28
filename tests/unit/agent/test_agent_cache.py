"""Tests for agent cache system."""

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest


@pytest.fixture
def cache_file(tmp_path):
    """Provide temporary cache file."""
    cache_path = tmp_path / ".cursor" / "agent_cache.json"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    return cache_path


@pytest.fixture
def agent_cache(cache_file, monkeypatch):
    """Provide agent_cache module with mocked cache file."""
    import sys

    sys.path.insert(0, str(Path(__file__).parents[2] / ".github/workflows/scripts"))

    import agent_cache

    monkeypatch.setattr(agent_cache, "CACHE_FILE", cache_file)
    yield agent_cache


def test_cache_does_not_exist_initially(agent_cache):
    """Test that cache is invalid when file doesn't exist."""
    assert not agent_cache.is_cache_valid()


def test_cache_is_valid_when_fresh(agent_cache):
    """Test that fresh cache (<5 min) is valid."""
    cache = {
        "updated_at": datetime.utcnow().isoformat(),
        "ttl_seconds": 300,
        "cached_data": {"test_key": "test_value"},
    }
    agent_cache.CACHE_FILE.write_text(json.dumps(cache))

    assert agent_cache.is_cache_valid()


def test_cache_is_invalid_when_stale(agent_cache):
    """Test that stale cache (>5 min) is invalid."""
    old_time = datetime.utcnow() - timedelta(seconds=400)
    cache = {
        "updated_at": old_time.isoformat(),
        "ttl_seconds": 300,
        "cached_data": {"test_key": "test_value"},
    }
    agent_cache.CACHE_FILE.write_text(json.dumps(cache))

    assert not agent_cache.is_cache_valid()


def test_get_cached_returns_none_when_invalid(agent_cache):
    """Test that get_cached returns None when cache is invalid."""
    assert agent_cache.get_cached("test_key") is None


def test_get_cached_returns_value_when_valid(agent_cache):
    """Test that get_cached returns value from valid cache."""
    cache = {
        "updated_at": datetime.utcnow().isoformat(),
        "ttl_seconds": 300,
        "cached_data": {"test_key": "test_value"},
    }
    agent_cache.CACHE_FILE.write_text(json.dumps(cache))

    assert agent_cache.get_cached("test_key") == "test_value"


def test_get_cached_returns_none_for_missing_key(agent_cache):
    """Test that get_cached returns None for non-existent key."""
    cache = {
        "updated_at": datetime.utcnow().isoformat(),
        "ttl_seconds": 300,
        "cached_data": {"test_key": "test_value"},
    }
    agent_cache.CACHE_FILE.write_text(json.dumps(cache))

    assert agent_cache.get_cached("missing_key") is None


def test_update_cache_creates_new_cache(agent_cache):
    """Test that update_cache creates new cache file."""
    agent_cache.update_cache("test_key", "test_value")

    assert agent_cache.CACHE_FILE.exists()
    cache = json.loads(agent_cache.CACHE_FILE.read_text())
    assert cache["cached_data"]["test_key"] == "test_value"


def test_update_cache_preserves_other_entries(agent_cache):
    """Test that update_cache preserves existing entries."""
    agent_cache.update_cache("key1", "value1")
    agent_cache.update_cache("key2", "value2")

    cache = json.loads(agent_cache.CACHE_FILE.read_text())
    assert cache["cached_data"]["key1"] == "value1"
    assert cache["cached_data"]["key2"] == "value2"


def test_refresh_cache_creates_full_cache(agent_cache):
    """Test that refresh_cache creates complete cache structure."""
    cache = agent_cache.refresh_cache()

    assert "updated_at" in cache
    assert "ttl_seconds" in cache
    assert "cached_data" in cache
    assert "current_branch" in cache["cached_data"]
    assert "open_issues" in cache["cached_data"]
    assert "infrastructure_status" in cache["cached_data"]


def test_invalidate_cache_removes_file(agent_cache):
    """Test that invalidate_cache removes cache file."""
    agent_cache.update_cache("test", "value")
    assert agent_cache.CACHE_FILE.exists()

    agent_cache.invalidate_cache()
    assert not agent_cache.CACHE_FILE.exists()


def test_invalidate_cache_returns_false_when_no_cache(agent_cache):
    """Test that invalidate_cache returns False when cache doesn't exist."""
    assert agent_cache.invalidate_cache() is False


def test_cache_with_malformed_json(agent_cache):
    """Test that malformed JSON cache is treated as invalid."""
    agent_cache.CACHE_FILE.write_text("not valid json")

    assert not agent_cache.is_cache_valid()
    assert agent_cache.get_cached("test") is None
