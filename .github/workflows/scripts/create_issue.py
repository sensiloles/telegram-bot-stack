#!/usr/bin/env python3
"""Create GitHub Issue - Simple Script.

This script creates a GitHub issue using PyGithub.
Issue content can be provided as a file or via stdin.

Usage:
    # From file
    python create_issue.py --title "Bug: Fix tests" --file issue.md

    # From stdin
    echo "Issue description" | python create_issue.py --title "Feature request"

    # With labels
    python create_issue.py --title "Bug" --file bug.md --labels bug,priority:high

    # Interactive (reads from stdin until Ctrl+D)
    python create_issue.py --title "New feature"
    > Type your issue description here...
    > Press Ctrl+D when done

Environment Variables:
    GITHUB_TOKEN: GitHub personal access token (required)
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from github_helper import GithubException, get_repo


def read_issue_body(file_path: Optional[str] = None) -> str:
    """Read issue body from file or stdin.

    Args:
        file_path: Path to file with issue body (None = read from stdin)

    Returns:
        Issue body text
    """
    if file_path:
        path = Path(file_path)
        if not path.exists():
            print(f"❌ Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        return path.read_text()
    else:
        # Read from stdin
        if sys.stdin.isatty():
            print("📝 Enter issue description (Ctrl+D when done):")
        return sys.stdin.read()


def create_issue(
    repo,
    title: str,
    body: str,
    labels: Optional[list] = None,
    assignees: Optional[list] = None,
    milestone: Optional[int] = None,
):
    """Create GitHub issue.

    Args:
        repo: Repository object
        title: Issue title
        body: Issue body (markdown)
        labels: List of label names
        assignees: List of usernames to assign
        milestone: Milestone number

    Returns:
        Created Issue object
    """
    try:
        print(f"📝 Creating issue: {title}")

        kwargs = {
            "title": title,
            "body": body,
        }

        if labels:
            kwargs["labels"] = labels

        if assignees:
            kwargs["assignees"] = assignees

        if milestone:
            milestone_obj = repo.get_milestone(milestone)
            kwargs["milestone"] = milestone_obj

        issue = repo.create_issue(**kwargs)

        print("✅ Issue created successfully!")
        print(f"   Number: #{issue.number}")
        print(f"   URL: {issue.html_url}")

        return issue

    except GithubException as e:
        print("❌ Error: Failed to create issue", file=sys.stderr)
        if e.status == 401:
            print("Invalid token or missing 'repo' scope", file=sys.stderr)
        elif e.status == 404:
            print("Repository not found or no access", file=sys.stderr)
        elif e.status == 422:
            print("Validation failed - check title and body", file=sys.stderr)
        else:
            print(f"GitHub API error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create GitHub issue using PyGithub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From markdown file
  python create_issue.py --title "Bug: Tests fail" --file issue.md

  # From stdin with labels
  echo "Description..." | python create_issue.py --title "Feature" --labels feature

  # Interactive
  python create_issue.py --title "Bug report"
  > Type description here
  > Ctrl+D to finish

  # With assignee and milestone
  python create_issue.py --title "Task" --file task.md --assignees sensiloles --milestone 1
        """,
    )

    parser.add_argument(
        "--title",
        type=str,
        required=True,
        help="Issue title (required)",
    )

    parser.add_argument(
        "--file",
        type=str,
        help="File containing issue body (markdown). If not provided, reads from stdin",
    )

    parser.add_argument(
        "--labels",
        type=str,
        help="Comma-separated labels (e.g. 'bug,priority:high')",
    )

    parser.add_argument(
        "--assignees",
        type=str,
        help="Comma-separated usernames to assign",
    )

    parser.add_argument(
        "--milestone",
        type=int,
        help="Milestone number",
    )

    parser.add_argument(
        "--repo",
        type=str,
        help="Repository in format owner/repo (auto-detected if not specified)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without actually creating it",
    )

    args = parser.parse_args()

    try:
        # Read issue body
        body = read_issue_body(args.file)

        if not body.strip():
            print("❌ Error: Issue body cannot be empty", file=sys.stderr)
            sys.exit(1)

        # Parse labels and assignees
        labels = (
            [label.strip() for label in args.labels.split(",")] if args.labels else None
        )
        assignees = (
            [a.strip() for a in args.assignees.split(",")] if args.assignees else None
        )

        if args.dry_run:
            # Show what would be created
            print("🔍 DRY RUN - Would create:")
            print(f"   Title: {args.title}")
            if labels:
                print(f"   Labels: {', '.join(labels)}")
            if assignees:
                print(f"   Assignees: {', '.join(assignees)}")
            if args.milestone:
                print(f"   Milestone: #{args.milestone}")
            print(f"\n{body[:200]}..." if len(body) > 200 else f"\n{body}")
            sys.exit(0)

        # Get repository
        repo = get_repo(args.repo)

        # Create issue
        create_issue(
            repo,
            title=args.title,
            body=body,
            labels=labels,
            assignees=assignees,
            milestone=args.milestone,
        )

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
