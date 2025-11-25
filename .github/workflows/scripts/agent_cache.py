#!/usr/bin/env python3
"""
Agent context cache management.

Caches frequently accessed data (open issues, branch status, test results) to reduce
API calls and improve agent startup speed.

Usage:
    # Check if cache is valid
    python3 .github/workflows/scripts/agent_cache.py --check

    # Update specific key
    python3 .github/workflows/scripts/agent_cache.py --update open_issues --value "[40,27,28]"

    # Invalidate cache
    python3 .github/workflows/scripts/agent_cache.py --invalidate

    # Get cached value
    python3 .github/workflows/scripts/agent_cache.py --get open_issues
"""

import argparse
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

# Cache configuration
CACHE_FILE = Path(".cursor/agent_cache.json")
TTL_SECONDS = 300  # 5 minutes


def _ensure_cursor_dir():
    """Ensure .cursor directory exists."""
    cursor_dir = CACHE_FILE.parent
    cursor_dir.mkdir(exist_ok=True)


def _get_current_branch() -> str:
    """Get current git branch."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def _get_open_issue_numbers() -> list[int]:
    """Get list of open issue numbers (uses GitHub CLI if available)."""
    try:
        result = subprocess.run(
            ["gh", "issue", "list", "--json", "number", "--jq", ".[].number"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [int(n) for n in result.stdout.strip().split("\n") if n]
    except Exception:
        # Fallback: return empty if gh not available
        return []


def _get_test_coverage() -> Optional[str]:
    """Get test coverage percentage from last run."""
    coverage_file = Path("coverage.xml")
    if not coverage_file.exists():
        return None

    try:
        import xml.etree.ElementTree as ET

        tree = ET.parse(coverage_file)
        root = tree.getroot()
        line_rate = float(root.attrib.get("line-rate", 0))
        return f"{line_rate * 100:.1f}%"
    except Exception:
        return None


def is_cache_valid() -> bool:
    """Check if cache exists and is fresh (<5 minutes old).

    Returns:
        bool: True if cache is valid and fresh, False otherwise
    """
    if not CACHE_FILE.exists():
        return False

    try:
        data = json.loads(CACHE_FILE.read_text())
        updated = datetime.fromisoformat(data["updated_at"])
        ttl = timedelta(seconds=data.get("ttl_seconds", TTL_SECONDS))
        return datetime.utcnow() - updated < ttl
    except (json.JSONDecodeError, KeyError, ValueError):
        return False


def get_cached(key: str) -> Optional[Any]:
    """Get value from cache if valid.

    Args:
        key: Cache key to retrieve

    Returns:
        Cached value if valid, None otherwise
    """
    if not is_cache_valid():
        return None

    try:
        data = json.loads(CACHE_FILE.read_text())
        return data["cached_data"].get(key)
    except (json.JSONDecodeError, KeyError):
        return None


def update_cache(key: str, value: Any):
    """Update single cache entry, preserving other entries.

    Args:
        key: Cache key to update
        value: Value to store
    """
    _ensure_cursor_dir()

    # Load existing cache or create new
    if CACHE_FILE.exists():
        try:
            data = json.loads(CACHE_FILE.read_text())
        except json.JSONDecodeError:
            data = _create_empty_cache()
    else:
        data = _create_empty_cache()

    # Update specific key
    data["cached_data"][key] = value
    data["updated_at"] = datetime.utcnow().isoformat()

    CACHE_FILE.write_text(json.dumps(data, indent=2))


def _create_empty_cache() -> dict:
    """Create empty cache structure."""
    return {
        "updated_at": datetime.utcnow().isoformat(),
        "ttl_seconds": TTL_SECONDS,
        "cached_data": {},
    }


def refresh_cache():
    """Refresh all cache entries with current data."""
    _ensure_cursor_dir()

    cache = {
        "updated_at": datetime.utcnow().isoformat(),
        "ttl_seconds": TTL_SECONDS,
        "cached_data": {
            "current_branch": _get_current_branch(),
            "open_issues": _get_open_issue_numbers(),
            "test_coverage": _get_test_coverage(),
            "infrastructure_status": {
                "mcp_github_workflow": "available",  # Assume available
                "mcp_project_graph": "available",
                "automation_scripts": "available",
            },
        },
    }

    CACHE_FILE.write_text(json.dumps(cache, indent=2))
    return cache


def invalidate_cache():
    """Invalidate cache by deleting the cache file."""
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
        return True
    return False


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Manage agent context cache")
    parser.add_argument("--check", action="store_true", help="Check if cache is valid")
    parser.add_argument("--refresh", action="store_true", help="Refresh all cache data")
    parser.add_argument(
        "--invalidate", action="store_true", help="Invalidate (delete) cache"
    )
    parser.add_argument("--get", metavar="KEY", help="Get cached value for KEY")
    parser.add_argument(
        "--update",
        nargs=2,
        metavar=("KEY", "VALUE"),
        help="Update cache KEY with VALUE (JSON)",
    )

    args = parser.parse_args()

    if args.check:
        valid = is_cache_valid()
        print(f"Cache is {'valid' if valid else 'invalid/expired'}")
        exit(0 if valid else 1)

    elif args.refresh:
        cache = refresh_cache()
        print("✅ Cache refreshed")
        print(json.dumps(cache, indent=2))

    elif args.invalidate:
        if invalidate_cache():
            print("✅ Cache invalidated")
        else:
            print("ℹ️  Cache was already empty")

    elif args.get:
        value = get_cached(args.get)
        if value is not None:
            print(json.dumps(value, indent=2))
        else:
            print(
                f"❌ Key '{args.get}' not found or cache invalid",
                file=__import__("sys").stderr,
            )
            exit(1)

    elif args.update:
        key, value_str = args.update
        try:
            value = json.loads(value_str)
        except json.JSONDecodeError:
            # Store as string if not valid JSON
            value = value_str
        update_cache(key, value)
        print(f"✅ Updated cache key '{key}'")

    else:
        # No action: show cache status
        if is_cache_valid():
            print("Cache is valid")
            data = json.loads(CACHE_FILE.read_text())
            print(json.dumps(data, indent=2))
        else:
            print("Cache is invalid or does not exist")


if __name__ == "__main__":
    main()
