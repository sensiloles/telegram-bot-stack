"""Common utilities for GitHub automation scripts.

DEPRECATED: This module is deprecated and will be removed in v2.0.0.
Please use github_helper.py instead:

    # OLD (common.py - DEPRECATED)
    from common import get_github_client, get_github_token

    # NEW (github_helper.py - RECOMMENDED)
    from github_helper import get_github_client, load_token

Migration guide:
- get_github_token() → load_token()
- get_github_client() → get_github_client() (same)
- get_repository_name() → get_repo_from_git()
- get_current_branch() → get_current_branch() (same)
- All other functions are now in github_helper.py

For backward compatibility, this module now imports from github_helper.py.
"""

import warnings

# Show deprecation warning
warnings.warn(
    "common.py is deprecated and will be removed in v2.0.0. "
    "Please use github_helper.py instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Import from github_helper for backward compatibility
from github_helper import (
    GithubException,
    get_current_branch,
    get_github_client,
    get_label_for_commit_type,
    is_breaking_change,
    parse_commit_type,
    validate_conventional_commit,
)
from github_helper import (
    get_repo_from_git as get_repository_name,
)
from github_helper import (
    load_token as get_github_token,
)

__all__ = [
    "get_github_token",
    "get_github_client",
    "get_repository_name",
    "get_current_branch",
    "validate_conventional_commit",
    "parse_commit_type",
    "get_label_for_commit_type",
    "is_breaking_change",
    "GithubException",
]

# Keep utility functions that are specific to common.py
import sys


def print_success(message: str) -> None:
    """Print success message."""
    print(f"✅ {message}")


def print_error(message: str) -> None:
    """Print error message."""
    print(f"❌ {message}", file=sys.stderr)


def print_warning(message: str) -> None:
    """Print warning message."""
    print(f"⚠️  {message}")


def print_info(message: str) -> None:
    """Print info message."""
    print(f"ℹ️  {message}")
