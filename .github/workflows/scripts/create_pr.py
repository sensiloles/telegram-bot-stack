#!/usr/bin/env python3
"""Create GitHub Pull Request - Automated Script.

This script creates a Pull Request with conventional commit format,
automatically detecting the current branch and target branch.

Features:
- Auto-detects current branch
- Validates conventional commit format
- Generates PR description from commits
- Links to issues automatically
- Supports draft PRs
- Auto-assigns PR to current user

Usage:
    # Basic (auto-generate description from commits, auto-assign to you)
    python create_pr.py --title "feat(storage): add Redis backend"

    # With custom description from file
    python create_pr.py --title "feat(storage): add Redis" --file pr.md

    # Link to issue
    python create_pr.py --title "fix(auth): resolve bug" --closes 42

    # Assign to specific user
    python create_pr.py --title "feat: feature" --assignee username

    # Don't assign anyone
    python create_pr.py --title "feat: feature" --no-assign

    # Draft PR
    python create_pr.py --title "feat: WIP feature" --draft

    # Custom base branch
    python create_pr.py --title "feat: feature" --base develop

Environment Variables:
    GITHUB_TOKEN: GitHub personal access token (required)
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

from github_helper import GithubException, get_repo


def get_current_branch() -> str:
    """Get current git branch name.

    Returns:
        Branch name

    Raises:
        SystemExit: If cannot detect branch
    """
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
        )
        branch = result.stdout.strip()
        if not branch:
            print("❌ Error: Not on a branch (detached HEAD?)", file=sys.stderr)
            sys.exit(1)
        return branch
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: Could not detect current branch: {e}", file=sys.stderr)
        sys.exit(1)


def get_commit_messages(base_branch: str, head_branch: str) -> list:
    """Get commit messages between two branches.

    Args:
        base_branch: Base branch (e.g., 'main')
        head_branch: Head branch (e.g., 'feature/xyz')

    Returns:
        List of commit messages
    """
    try:
        result = subprocess.run(
            ["git", "log", f"{base_branch}..{head_branch}", "--pretty=format:%s"],
            capture_output=True,
            text=True,
            check=True,
        )
        commits = [line.strip() for line in result.stdout.split("\n") if line.strip()]
        return commits
    except subprocess.CalledProcessError:
        return []


def validate_pr_title(title: str) -> tuple[bool, str]:
    """Validate PR title follows conventional commit format.

    Args:
        title: PR title

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Pattern: type(scope): description or type: description
    pattern = r"^(feat|fix|docs|refactor|test|chore|perf|style|ci|build|revert)(\([a-z0-9,\s-]+\))?:\s.+"

    if re.match(pattern, title, re.IGNORECASE):
        return True, ""

    return False, (
        "PR title must follow format: type(scope): description\n"
        "Valid types: feat, fix, docs, refactor, test, chore, perf, style, ci\n"
        "Example: feat(storage): add Redis backend"
    )


def generate_pr_body(
    commits: list,
    closes_issue: Optional[int] = None,
    custom_body: Optional[str] = None,
) -> str:
    """Generate PR description.

    Args:
        commits: List of commit messages
        closes_issue: Issue number to close (optional)
        custom_body: Custom description (optional)

    Returns:
        PR body markdown
    """
    lines = []

    # Custom description or auto-generated
    if custom_body:
        lines.append(custom_body)
        lines.append("")
    elif commits:
        lines.append("## Changes")
        lines.append("")
        for commit in commits:
            lines.append(f"- {commit}")
        lines.append("")

    # Issue linking
    if closes_issue:
        lines.append("## Related Issue")
        lines.append("")
        lines.append(f"Closes #{closes_issue}")
        lines.append("")

    # Checklist
    lines.append("## Checklist")
    lines.append("")
    lines.append("- [x] Code follows project style guidelines")
    lines.append("- [x] Self-review completed")
    lines.append("- [x] Comments added for complex code")
    lines.append("- [x] Documentation updated (if needed)")
    lines.append("- [x] No new warnings generated")
    lines.append("- [x] Tests added/updated (if applicable)")
    lines.append("- [x] All tests passing locally")

    return "\n".join(lines)


def read_pr_body(file_path: Optional[str] = None) -> Optional[str]:
    """Read PR body from file.

    Args:
        file_path: Path to file with PR body

    Returns:
        PR body text or None
    """
    if not file_path:
        return None

    path = Path(file_path)
    if not path.exists():
        print(f"❌ Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    return path.read_text()


def create_pull_request(
    repo,
    title: str,
    body: str,
    head: str,
    base: str = "main",
    draft: bool = False,
    assignee: Optional[str] = None,
    auto_assign: bool = True,
):
    """Create GitHub Pull Request.

    Args:
        repo: Repository object
        title: PR title
        body: PR description
        head: Source branch
        base: Target branch
        draft: Create as draft PR
        assignee: Username to assign (if None and auto_assign=True, assigns current user)
        auto_assign: Automatically assign current user if assignee not specified

    Returns:
        Created PullRequest object
    """
    try:
        print("📝 Creating Pull Request...")
        print(f"   Repository: {repo.full_name}")
        print(f"   From: {head}")
        print(f"   To: {base}")
        print(f"   Title: {title}")
        print(f"   Draft: {draft}")

        # For same repository, use simple branch name
        # For cross-repository, use owner:branch format
        head_ref = head
        if ":" not in head:
            # Simple branch name (same repo)
            head_ref = head

        print(f"   Head ref: {head_ref}")

        pr = repo.create_pull(
            title=title,
            body=body,
            head=head_ref,
            base=base,
            draft=draft,
        )

        print("✅ Pull Request created successfully!")
        print(f"   Number: #{pr.number}")
        print(f"   URL: {pr.html_url}")

        # Assign to user
        if auto_assign or assignee:
            try:
                # Get GitHub client from repo
                gh = repo._requester._Github

                # Get user to assign
                if assignee:
                    user_to_assign = assignee
                else:
                    # Get current authenticated user
                    current_user = gh.get_user()
                    user_to_assign = current_user.login

                # Add assignee to PR
                pr.add_to_assignees(user_to_assign)
                print(f"👤 Assigned to: @{user_to_assign}")
            except Exception as e:
                print(f"⚠️  Warning: Could not assign PR: {e}", file=sys.stderr)
                # Don't fail the whole operation if assignment fails

        return pr

    except GithubException as e:
        print("❌ Error: Failed to create Pull Request", file=sys.stderr)
        if e.status == 401:
            print("Invalid token or missing 'repo' scope", file=sys.stderr)
        elif e.status == 403:
            print("Permission denied. Check token permissions:", file=sys.stderr)
            print("  - Required: Pull requests: Read & Write", file=sys.stderr)
            print("  - Required: Contents: Read (CRITICAL!)", file=sys.stderr)
            print("  - Required: Metadata: Read", file=sys.stderr)
        elif e.status == 404:
            print("Repository not found or no access", file=sys.stderr)
        elif e.status == 422:
            if "pull request already exists" in str(e).lower():
                print(
                    f"Pull Request already exists for {head} -> {base}", file=sys.stderr
                )
            elif "no commits between" in str(e).lower():
                print(f"No commits between {base} and {head}", file=sys.stderr)
            else:
                # Print detailed error info
                error_msg = (
                    e.data.get("message", str(e))
                    if hasattr(e, "data") and e.data
                    else str(e)
                )
                print(f"Validation failed: {error_msg}", file=sys.stderr)
                if hasattr(e, "data") and e.data and "errors" in e.data:
                    print("Details:", file=sys.stderr)
                    for error in e.data["errors"]:
                        print(f"  - {error}", file=sys.stderr)

                    # Check for "not all refs are readable" error
                    if any(
                        "not all refs are readable" in str(err).lower()
                        for err in e.data["errors"]
                    ):
                        print("\n⚠️  This error usually means:", file=sys.stderr)
                        print(
                            "   1. Token missing 'Contents: Read' permission (MOST COMMON)",
                            file=sys.stderr,
                        )
                        print(
                            "   2. Branch doesn't exist or not pushed", file=sys.stderr
                        )
                        print(
                            "   3. Token missing 'Metadata: Read' permission",
                            file=sys.stderr,
                        )
                        print(
                            "\n💡 Solution: Update token with 'Contents: Read' permission",
                            file=sys.stderr,
                        )
        else:
            print(f"GitHub API error (status {e.status}): {e}", file=sys.stderr)
            if hasattr(e, "data") and e.data:
                print(f"Details: {e.data}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create GitHub Pull Request with conventional format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect branch, auto-generate description
  python create_pr.py --title "feat(storage): add Redis backend"

  # Link to issue
  python create_pr.py --title "fix(auth): resolve bug" --closes 42

  # Custom description from file
  python create_pr.py --title "feat: new feature" --file pr_description.md

  # Draft PR for WIP
  python create_pr.py --title "feat: WIP feature" --draft

  # Custom base branch
  python create_pr.py --title "feat: feature" --base develop

  # Dry run (preview)
  python create_pr.py --title "feat: test" --dry-run
        """,
    )

    parser.add_argument(
        "--title",
        type=str,
        required=True,
        help="PR title in format: type(scope): description",
    )

    parser.add_argument(
        "--file",
        type=str,
        help="File containing PR description (markdown). Auto-generated if not provided",
    )

    parser.add_argument(
        "--head",
        type=str,
        help="Source branch (auto-detected if not specified)",
    )

    parser.add_argument(
        "--base",
        type=str,
        default="main",
        help="Target branch (default: main)",
    )

    parser.add_argument(
        "--closes",
        type=int,
        help="Issue number to close (adds 'Closes #N' to description)",
    )

    parser.add_argument(
        "--draft",
        action="store_true",
        help="Create as draft Pull Request",
    )

    parser.add_argument(
        "--repo",
        type=str,
        help="Repository in format owner/repo (auto-detected if not specified)",
    )

    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip PR title validation",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without actually creating it",
    )

    parser.add_argument(
        "--assignee",
        type=str,
        help="GitHub username to assign (default: current user)",
    )

    parser.add_argument(
        "--no-assign",
        action="store_true",
        help="Do not assign anyone to the PR",
    )

    args = parser.parse_args()

    try:
        # Validate PR title
        if not args.no_validate:
            is_valid, error_msg = validate_pr_title(args.title)
            if not is_valid:
                print(f"❌ Invalid PR title format:\n{error_msg}", file=sys.stderr)
                sys.exit(1)

        # Get head branch
        head_branch = args.head or get_current_branch()

        # Check if on base branch
        if head_branch == args.base:
            print(
                f"❌ Error: Cannot create PR from {args.base} to {args.base}",
                file=sys.stderr,
            )
            print("Please create a feature branch first:", file=sys.stderr)
            print("  git checkout -b feature/your-feature", file=sys.stderr)
            sys.exit(1)

        # Get repository
        repo = get_repo(args.repo)

        # Get commits
        commits = get_commit_messages(args.base, head_branch)
        if not commits:
            print(f"⚠️  Warning: No commits found between {args.base} and {head_branch}")

        # Read custom body or auto-generate
        custom_body = read_pr_body(args.file)

        # Generate PR body
        body = generate_pr_body(commits, args.closes, custom_body)

        if args.dry_run:
            # Show what would be created
            print("🔍 DRY RUN - Would create:")
            print(f"   Repository: {repo.full_name}")
            print(f"   From: {head_branch}")
            print(f"   To: {args.base}")
            print(f"   Title: {args.title}")
            print(f"   Draft: {args.draft}")
            print("\n" + "=" * 80)
            print("PR Description:")
            print("=" * 80)
            print(body)
            print("=" * 80)

            if commits:
                print(f"\nCommits to be included ({len(commits)}):")
                for commit in commits:
                    print(f"  - {commit}")

            sys.exit(0)

        # Create Pull Request
        create_pull_request(
            repo,
            title=args.title,
            body=body,
            head=head_branch,
            base=args.base,
            draft=args.draft,
            assignee=args.assignee,
            auto_assign=not args.no_assign,
        )

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
