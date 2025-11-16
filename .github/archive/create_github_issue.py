#!/usr/bin/env python3
"""
Create GitHub Issue from FIRST_ISSUE_DRAFT.md

This script reads the draft issue and creates it on GitHub using the GitHub API.
"""

import os
import sys
from pathlib import Path

try:
    from github import Github
    from github.GithubException import GithubException
except ImportError:
    print("❌ PyGithub is not installed. Installing...")
    os.system("pip install PyGithub")
    from github import Github
    from github.GithubException import GithubException


def get_github_token():
    """Get GitHub token from environment or .env file."""
    # Try environment variable first
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return token

    # Try reading from .env file
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith("GITHUB_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"')

    return None


def read_issue_draft():
    """Read the issue draft from file."""
    draft_file = (
        Path(__file__).parent.parent / ".github" / "archive" / "FIRST_ISSUE_DRAFT.md"
    )

    if not draft_file.exists():
        print(f"❌ Draft file not found: {draft_file}")
        sys.exit(1)

    with open(draft_file) as f:
        content = f.read()

    # Extract title (first line starting with #)
    lines = content.split("\n")
    title = None
    body_lines = []

    for line in lines:
        if line.startswith("# ") and not title:
            title = line[2:].strip()
        elif title:
            body_lines.append(line)

    body = "\n".join(body_lines).strip()

    return title, body


def get_repo_info():
    """Get repository owner and name from git remote."""
    import subprocess

    try:
        # Get remote URL
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )

        remote_url = result.stdout.strip()

        # Parse owner and repo from URL
        # Format: git@github.com:owner/repo.git or https://github.com/owner/repo.git
        if "github.com" in remote_url:
            parts = remote_url.replace(".git", "").split("/")
            repo_name = parts[-1]
            owner = parts[-2].split(":")[-1]
            return owner, repo_name
        else:
            print("❌ Remote URL is not a GitHub repository")
            sys.exit(1)

    except subprocess.CalledProcessError:
        print("❌ Failed to get git remote URL")
        print("Make sure you're in a git repository with a GitHub remote")
        sys.exit(1)


def create_issue(token, owner, repo_name, title, body, labels):
    """Create GitHub issue using PyGithub."""
    try:
        # Initialize GitHub API
        g = Github(token)

        # Get repository
        repo = g.get_repo(f"{owner}/{repo_name}")

        print(f"📝 Creating issue in {owner}/{repo_name}...")
        print(f"Title: {title}")
        print(f"Labels: {', '.join(labels)}")

        # Create issue
        issue = repo.create_issue(title=title, body=body, labels=labels)

        print("\n✅ Issue created successfully!")
        print(f"🔗 URL: {issue.html_url}")
        print(f"📋 Issue #{issue.number}")

        return issue

    except GithubException as e:
        print(f"\n❌ Failed to create issue: {e}")
        if e.status == 401:
            print("Token is invalid or doesn't have required permissions")
            print("Make sure your token has 'repo' or 'public_repo' scope")
        sys.exit(1)


def main():
    """Main execution."""
    print("🤖 GitHub Issue Creator")
    print("=" * 50)

    # Get GitHub token
    token = get_github_token()
    if not token:
        print("\n❌ GITHUB_TOKEN not found!")
        print("\nPlease set it in one of these ways:")
        print("1. Export: export GITHUB_TOKEN='your_token_here'")
        print("2. Add to .env: GITHUB_TOKEN=your_token_here")
        print("\nTo create a token:")
        print("1. Go to https://github.com/settings/tokens")
        print("2. Click 'Generate new token (classic)'")
        print("3. Select 'repo' scope")
        print("4. Generate and copy the token")
        sys.exit(1)

    print("✅ GitHub token found")

    # Get repository info
    owner, repo_name = get_repo_info()
    print(f"✅ Repository: {owner}/{repo_name}")

    # Read issue draft
    print("✅ Reading issue draft...")
    title, body = read_issue_draft()

    # Define labels
    labels = ["refactor", "component:bot", "priority:high"]

    # Create issue
    issue = create_issue(token, owner, repo_name, title, body, labels)

    print("\n🎉 Done! Your issue is ready.")
    print("\nNext steps:")
    print("1. Visit the issue URL above")
    print("2. Try Cloud Agent commands:")
    print("   - /breakdown - Break into subtasks")
    print("   - /accept - Generate acceptance criteria")
    print("   - /estimate - Get time estimate")


if __name__ == "__main__":
    main()
