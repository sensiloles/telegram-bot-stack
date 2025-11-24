"""Common utilities for GitHub automation scripts."""

import os
import sys
from pathlib import Path
from typing import Optional

from github import Github, GithubException


def get_github_token() -> str:
    """Get GitHub token from environment or .env file."""
    # Try environment variable first
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return token

    # Try .env file
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("GITHUB_TOKEN="):
                    token = line.split("=", 1)[1].strip().strip('"').strip("'")
                    return token

    print("❌ Error: GITHUB_TOKEN not found", file=sys.stderr)
    print("\nSet token via environment variable:", file=sys.stderr)
    print("  export GITHUB_TOKEN=ghp_...", file=sys.stderr)
    print("\nOr create .env file with:", file=sys.stderr)
    print("  GITHUB_TOKEN=ghp_...", file=sys.stderr)
    print("\nGenerate token at: https://github.com/settings/tokens", file=sys.stderr)
    sys.exit(1)


def get_github_client() -> Github:
    """Get authenticated GitHub client."""
    token = get_github_token()
    try:
        return Github(token)
    except GithubException as e:
        print(f"❌ Error: Failed to authenticate with GitHub: {e}", file=sys.stderr)
        sys.exit(1)


def get_repository_name() -> str:
    """Get repository name from git remote or environment."""
    # Try environment variable
    repo = os.getenv("GITHUB_REPOSITORY")
    if repo:
        return repo

    # Try to get from git remote
    import subprocess

    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )
        remote_url = result.stdout.strip()

        # Parse URL (https or ssh)
        if "github.com" in remote_url:
            # Extract owner/repo from URL
            if remote_url.startswith("https://"):
                # https://github.com/owner/repo.git
                parts = remote_url.replace("https://github.com/", "").replace(
                    ".git", ""
                )
            elif remote_url.startswith("git@"):
                # git@github.com:owner/repo.git
                parts = remote_url.replace("git@github.com:", "").replace(".git", "")
            else:
                raise ValueError("Unknown remote URL format")

            return parts
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"❌ Error: Could not determine repository name: {e}", file=sys.stderr)
        print("\nSet GITHUB_REPOSITORY environment variable:", file=sys.stderr)
        print("  export GITHUB_REPOSITORY=owner/repo", file=sys.stderr)
        sys.exit(1)


def get_current_branch() -> Optional[str]:
    """Get current git branch name."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def validate_conventional_commit(title: str) -> bool:
    """Validate conventional commit format."""
    import re

    pattern = r"^(feat|fix|docs|style|refactor|perf|test|chore|ci)(\(.+\))?!?: .+"
    return bool(re.match(pattern, title))


def parse_commit_type(title: str) -> Optional[str]:
    """Parse commit type from conventional commit title."""
    import re

    match = re.match(r"^(feat|fix|docs|style|refactor|perf|test|chore|ci)", title)
    if match:
        return match.group(1)
    return None


def get_label_for_commit_type(commit_type: str) -> Optional[str]:
    """Get GitHub label for commit type."""
    label_map = {
        "feat": "enhancement",
        "fix": "bug",
        "docs": "documentation",
        "test": "testing",
        "perf": "performance",
    }
    return label_map.get(commit_type)


def is_breaking_change(title: str) -> bool:
    """Check if commit is a breaking change."""
    return "!" in title.split(":")[0] or "BREAKING CHANGE:" in title


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
