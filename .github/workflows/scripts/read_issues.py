#!/usr/bin/env python3
"""GitHub Issues Reader Script - Modern PyGithub version.

This script reads GitHub issues using PyGithub library and provides
formatted output for automation and manual review.

Usage:
    python read_issues.py <issue_number>           # Get specific issue
    python read_issues.py --list                    # List open issues
    python read_issues.py --list --state open       # List open issues
    python read_issues.py --list --state closed     # List closed issues
    python read_issues.py --list --labels "bug"     # Filter by labels
    python read_issues.py 4 --json                  # JSON output

Environment Variables:
    GITHUB_TOKEN: GitHub personal access token (required)
                  Can be in environment or .env file
"""

import argparse
import json
import sys
from typing import Optional

from github_helper import (
    GithubException,
    format_issue_detail,
    format_issue_list,
    get_repo,
)


def get_issue(repo, issue_number: int):
    """Get specific issue by number.

    Args:
        repo: Repository object
        issue_number: Issue number

    Returns:
        Issue object
    """
    try:
        return repo.get_issue(issue_number)
    except GithubException as e:
        if e.status == 404:
            print(f"❌ Error: Issue #{issue_number} not found", file=sys.stderr)
        else:
            print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def list_issues(
    repo,
    state: str = "open",
    labels: Optional[list] = None,
    limit: int = 30,
):
    """List issues with filters.

    Args:
        repo: Repository object
        state: Issue state (open, closed, all)
        labels: List of label names to filter by
        limit: Maximum number of issues to return

    Returns:
        List of Issue objects
    """
    try:
        issues = repo.get_issues(state=state, labels=labels or [])
        # Convert to list with limit using iterator (handles empty lists correctly)
        result = []
        for i, issue in enumerate(issues):
            if i >= limit:
                break
            result.append(issue)
        return result
    except GithubException as e:
        print(f"❌ Error: Failed to list issues: {e}", file=sys.stderr)
        sys.exit(1)


def issue_to_dict(issue) -> dict:
    """Convert Issue object to dict for JSON export.

    Args:
        issue: Issue object

    Returns:
        Dict representation
    """
    return {
        "number": issue.number,
        "title": issue.title,
        "state": issue.state,
        "body": issue.body,
        "url": issue.html_url,
        "author": issue.user.login,
        "labels": [label.name for label in issue.labels],
        "assignees": [a.login for a in issue.assignees],
        "milestone": issue.milestone.title if issue.milestone else None,
        "created_at": issue.created_at.isoformat(),
        "updated_at": issue.updated_at.isoformat(),
        "comments": [
            {
                "author": c.user.login,
                "body": c.body,
                "created_at": c.created_at.isoformat(),
            }
            for c in issue.get_comments()
        ],
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Read GitHub issues using PyGithub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get specific issue
  python read_issues.py 4

  # List all open issues
  python read_issues.py --list

  # List closed issues
  python read_issues.py --list --state closed

  # List issues with specific labels
  python read_issues.py --list --labels bug,priority:high

  # Export issue to JSON
  python read_issues.py 4 --json > issue_4.json

  # Brief output (no full body)
  python read_issues.py 4 --brief
        """,
    )

    parser.add_argument(
        "issue_number",
        type=int,
        nargs="?",
        help="Issue number to read",
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List issues instead of reading a specific one",
    )

    parser.add_argument(
        "--state",
        choices=["open", "closed", "all"],
        default="open",
        help="Filter issues by state (default: open)",
    )

    parser.add_argument(
        "--labels",
        type=str,
        help="Filter issues by labels (comma-separated)",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=30,
        help="Maximum number of issues to list (default: 30)",
    )

    parser.add_argument(
        "--repo",
        type=str,
        help="Repository in format owner/repo (auto-detected if not specified)",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON instead of formatted text",
    )

    parser.add_argument(
        "--brief",
        action="store_true",
        help="Show brief output without full body (only for single issue)",
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.list and args.issue_number is None:
        parser.error("Either provide an issue number or use --list")

    try:
        # Get repository
        repo = get_repo(args.repo)

        if args.list:
            # List issues
            labels_list = (
                [label.strip() for label in args.labels.split(",")]
                if args.labels
                else None
            )
            issues = list_issues(
                repo,
                state=args.state,
                labels=labels_list,
                limit=args.limit,
            )

            if args.json:
                # Export to JSON
                data = [issue_to_dict(issue) for issue in issues]
                print(json.dumps(data, indent=2))
            else:
                # Formatted output
                print(format_issue_list(issues))

        else:
            # Get specific issue
            issue = get_issue(repo, args.issue_number)

            if args.json:
                # Export to JSON
                print(json.dumps(issue_to_dict(issue), indent=2))
            else:
                # Formatted output
                if args.brief:
                    # Brief: just show summary
                    state = "OPEN" if issue.state == "open" else "CLOSED"
                    print(f"#{issue.number} [{state}] {issue.title}")
                    print(f"URL: {issue.html_url}")
                    if issue.labels:
                        labels = [label.name for label in issue.labels]
                        print(f"Labels: {', '.join(labels)}")
                else:
                    # Full details
                    print(format_issue_detail(issue))

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
