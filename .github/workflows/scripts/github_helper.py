#!/usr/bin/env python3
"""Unified GitHub API Helper using PyGithub.

This module provides a simple, modern interface to GitHub API
using the PyGithub library. All GitHub operations should use this helper.

Features:
- Automatic token loading from .env or environment
- Simple API for common operations
- Proper error handling
- Type hints for better IDE support

Usage:
    from github_helper import get_github_client, load_token

    # Get authenticated client
    gh = get_github_client()
    repo = gh.get_repo("owner/repo")

    # List issues
    issues = repo.get_issues(state='open')
    for issue in issues:
        print(f"#{issue.number}: {issue.title}")

    # Create issue
    issue = repo.create_issue(
        title="Bug: Something broke",
        body="Detailed description...",
        labels=["bug", "priority:high"]
    )
"""

import os
import sys
from pathlib import Path
from typing import Optional

try:
    from github import Auth, Github, GithubException
    from github.Repository import Repository
except ImportError:
    print("📦 Installing PyGithub...", file=sys.stderr)
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "PyGithub"])
    from github import Auth, Github, GithubException
    from github.Repository import Repository


def load_token(token: Optional[str] = None) -> str:
    """Load GitHub token from environment or .env file.

    Priority:
    1. Provided token parameter
    2. GITHUB_TOKEN environment variable
    3. .env file in workspace root

    Args:
        token: Optional token to use directly

    Returns:
        GitHub token string

    Raises:
        SystemExit: If token not found
    """
    if token:
        return token

    # Try environment variable
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
                    if token:
                        return token

    print("❌ Error: GITHUB_TOKEN not found", file=sys.stderr)
    print("", file=sys.stderr)
    print("Please set GITHUB_TOKEN in one of:", file=sys.stderr)
    print("  1. Environment: export GITHUB_TOKEN=your_token", file=sys.stderr)
    print("  2. .env file: GITHUB_TOKEN=your_token", file=sys.stderr)
    sys.exit(1)


def get_github_client(token: Optional[str] = None) -> Github:
    """Get authenticated GitHub client.

    Args:
        token: Optional token (auto-loaded if not provided)

    Returns:
        Authenticated Github instance
    """
    token = load_token(token)
    auth = Auth.Token(token)
    return Github(auth=auth)


def get_repo(
    repo_name: Optional[str] = None, token: Optional[str] = None
) -> Repository:
    """Get repository object.

    Args:
        repo_name: Repository in format "owner/repo" (auto-detected from git if None)
        token: Optional GitHub token

    Returns:
        Repository object
    """
    gh = get_github_client(token)

    if not repo_name:
        repo_name = get_repo_from_git()

    try:
        return gh.get_repo(repo_name)
    except GithubException as e:
        print(f"❌ Error: Could not access repository '{repo_name}'", file=sys.stderr)
        if e.status == 404:
            print("Repository not found or you don't have access", file=sys.stderr)
        elif e.status == 401:
            print(
                "Invalid token or token doesn't have required permissions",
                file=sys.stderr,
            )
        else:
            print(f"GitHub API error: {e}", file=sys.stderr)
        sys.exit(1)


def get_repo_from_git() -> str:
    """Detect repository name from git remote.

    Returns:
        Repository name in format "owner/repo"

    Raises:
        SystemExit: If repository cannot be detected
    """
    import subprocess

    # Try environment variable first
    repo = os.getenv("GITHUB_REPOSITORY")
    if repo:
        return repo

    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )
        remote_url = result.stdout.strip()

        # Parse different URL formats
        if "github.com" not in remote_url:
            raise ValueError(f"Not a GitHub repository: {remote_url}")

        # Remove .git suffix
        remote_url = remote_url.rstrip(".git")

        # Extract owner/repo from different formats
        if remote_url.startswith("git@github.com:"):
            # SSH format: git@github.com:owner/repo
            return remote_url.replace("git@github.com:", "")
        elif "github.com/" in remote_url:
            # HTTPS format: https://github.com/owner/repo
            return remote_url.split("github.com/")[-1]

        raise ValueError(f"Could not parse GitHub URL: {remote_url}")

    except subprocess.CalledProcessError as e:
        print("❌ Error: Could not detect repository from git", file=sys.stderr)
        print(f"Git error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        print("Please specify repository with --repo owner/repo", file=sys.stderr)
        sys.exit(1)


def get_current_branch(default: Optional[str] = None) -> Optional[str]:
    """Get current git branch name.

    Args:
        default: Value to return if branch detection fails

    Returns:
        Branch name or default value

    Examples:
        >>> branch = get_current_branch()  # Returns None if not in git repo
        >>> branch = get_current_branch(default="unknown")  # Returns "unknown" if fails
    """
    import subprocess

    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
        )
        branch = result.stdout.strip()
        return branch if branch else default
    except subprocess.CalledProcessError:
        return default


def validate_conventional_commit(title: str) -> bool:
    """Validate conventional commit format.

    Args:
        title: Commit title to validate

    Returns:
        True if valid conventional commit format

    Examples:
        >>> validate_conventional_commit("feat: add new feature")
        True
        >>> validate_conventional_commit("feat(scope): add feature")
        True
        >>> validate_conventional_commit("feat!: breaking change")
        True
        >>> validate_conventional_commit("invalid commit")
        False
    """
    import re

    pattern = r"^(feat|fix|docs|style|refactor|perf|test|chore|ci)(\(.+\))?!?: .+"
    return bool(re.match(pattern, title))


def parse_commit_type(title: str) -> Optional[str]:
    """Parse commit type from conventional commit title.

    Args:
        title: Commit title

    Returns:
        Commit type (feat, fix, docs, etc.) or None

    Examples:
        >>> parse_commit_type("feat: add feature")
        'feat'
        >>> parse_commit_type("fix(api): fix bug")
        'fix'
    """
    import re

    match = re.match(r"^(feat|fix|docs|style|refactor|perf|test|chore|ci)", title)
    if match:
        return match.group(1)
    return None


def get_label_for_commit_type(commit_type: str) -> Optional[str]:
    """Get GitHub label for commit type.

    Args:
        commit_type: Commit type (feat, fix, docs, etc.)

    Returns:
        GitHub label name or None

    Examples:
        >>> get_label_for_commit_type("feat")
        'enhancement'
        >>> get_label_for_commit_type("fix")
        'bug'
    """
    label_map = {
        "feat": "enhancement",
        "fix": "bug",
        "docs": "documentation",
        "test": "testing",
        "perf": "performance",
    }
    return label_map.get(commit_type)


def is_breaking_change(title: str) -> bool:
    """Check if commit is a breaking change.

    Args:
        title: Commit title

    Returns:
        True if breaking change

    Examples:
        >>> is_breaking_change("feat!: breaking change")
        True
        >>> is_breaking_change("feat: BREAKING CHANGE: something")
        True
        >>> is_breaking_change("feat: normal change")
        False
    """
    return "!" in title.split(":")[0] or "BREAKING CHANGE:" in title


# Aliases for backward compatibility
get_repository_name = get_repo_from_git  # Alias for common.py compatibility
get_github_token = load_token  # Alias for common.py compatibility


def format_issue_list(issues, show_labels: bool = True) -> str:
    """Format list of issues for display.

    Args:
        issues: Iterable of Issue objects
        show_labels: Whether to show labels

    Returns:
        Formatted string
    """
    lines = []
    issue_list = list(issues)

    if not issue_list:
        return "No issues found."

    lines.append(f"Found {len(issue_list)} issue(s):")
    lines.append("")

    for issue in issue_list:
        state = "OPEN" if issue.state == "open" else "CLOSED"
        line = f"#{issue.number} [{state}] {issue.title}"

        if show_labels and issue.labels:
            label_names = [label.name for label in issue.labels]
            line += f" [{', '.join(label_names)}]"

        lines.append(line)

    return "\n".join(lines)


def format_issue_detail(issue) -> str:
    """Format single issue with full details.

    Args:
        issue: Issue object

    Returns:
        Formatted string
    """
    lines = []
    lines.append("=" * 80)
    lines.append(f"Issue #{issue.number}: {issue.title}")
    lines.append("=" * 80)
    lines.append(f"State: {issue.state.upper()}")
    lines.append(f"Author: {issue.user.login}")

    if issue.labels:
        label_names = [label.name for label in issue.labels]
        lines.append(f"Labels: {', '.join(label_names)}")

    if issue.assignees:
        assignee_names = [a.login for a in issue.assignees]
        lines.append(f"Assignees: {', '.join(assignee_names)}")

    if issue.milestone:
        lines.append(f"Milestone: {issue.milestone.title}")

    lines.append(f"URL: {issue.html_url}")
    lines.append("")

    if issue.body:
        lines.append("Description:")
        lines.append("-" * 80)
        lines.append(issue.body)
        lines.append("-" * 80)

    # Comments
    comments = list(issue.get_comments())
    if comments:
        lines.append(f"\nComments ({len(comments)}):")
        for i, comment in enumerate(comments, 1):
            lines.append(f"\n--- Comment {i} ---")
            lines.append(f"Author: {comment.user.login}")
            lines.append(f"Date: {comment.created_at}")
            lines.append(comment.body)

    return "\n".join(lines)


if __name__ == "__main__":
    # Quick self-test
    print("🔍 Testing GitHub Helper...")
    print(
        f"Token found: {'✅' if os.getenv('GITHUB_TOKEN') or (Path.cwd() / '.env').exists() else '❌'}"
    )

    try:
        repo_name = get_repo_from_git()
        print(f"Repository: {repo_name}")

        gh = get_github_client()
        repo = gh.get_repo(repo_name)
        print(f"✅ Connected to: {repo.full_name}")
        print(f"   Description: {repo.description}")
        print(f"   Stars: {repo.stargazers_count}")
    except SystemExit:
        print("❌ Could not connect to GitHub")
