#!/usr/bin/env python3
"""Link GitHub Issues - Create dependencies between issues.

This script creates relationships between GitHub issues by adding
structured comments that indicate dependencies.

Usage:
    # Mark issue as blocked by others
    python link_issues.py 31 --blocked-by 27,28,29

    # Mark issue as blocking others
    python link_issues.py 27 --blocks 31

    # Create bidirectional link
    python link_issues.py 31 --blocked-by 27 --bidirectional

    # Add related issues (no dependency)
    python link_issues.py 31 --related-to 19,20

    # Custom comment
    python link_issues.py 31 --blocked-by 27 --comment "Waiting for deployment feature"

    # Dry run
    python link_issues.py 31 --blocked-by 27,28 --dry-run

Environment Variables:
    GITHUB_TOKEN: GitHub personal access token (required)
"""

import argparse
import sys
from typing import List, Optional

from github_helper import GithubException, get_repo


def format_blocked_by_comment(
    blocker_issues: List[int],
    custom_message: Optional[str] = None,
) -> str:
    """Format comment for issue that is blocked.

    Args:
        blocker_issues: List of issue numbers that block this issue
        custom_message: Optional custom message to include

    Returns:
        Formatted markdown comment
    """
    blockers_list = "\n".join([f"- #{num}" for num in blocker_issues])

    comment = f"""## ⚠️ Blocked by Other Issues

This issue is blocked by the following issues that must be completed first:

{blockers_list}"""

    if custom_message:
        comment += f"\n\n**Note:** {custom_message}"

    comment += "\n\n**Status:** This issue will be unblocked once all blocker issues are resolved."

    return comment


def format_blocks_comment(
    blocked_issues: List[int],
    custom_message: Optional[str] = None,
) -> str:
    """Format comment for issue that blocks others.

    Args:
        blocked_issues: List of issue numbers blocked by this issue
        custom_message: Optional custom message to include

    Returns:
        Formatted markdown comment
    """
    blocked_list = "\n".join([f"- #{num}" for num in blocked_issues])

    comment = f"""## 🔗 Blocks Other Issues

Completing this issue will unblock:

{blocked_list}"""

    if custom_message:
        comment += f"\n\n**Note:** {custom_message}"

    comment += "\n\n**Impact:** These issues depend on this one being completed first."

    return comment


def format_related_comment(
    related_issues: List[int],
    custom_message: Optional[str] = None,
) -> str:
    """Format comment for related issues (no dependency).

    Args:
        related_issues: List of related issue numbers
        custom_message: Optional custom message to include

    Returns:
        Formatted markdown comment
    """
    related_list = "\n".join([f"- #{num}" for num in related_issues])

    comment = f"""## 🔗 Related Issues

This issue is related to:

{related_list}"""

    if custom_message:
        comment += f"\n\n**Note:** {custom_message}"

    return comment


def link_issues(
    issue_number: int,
    repo,
    blocked_by: Optional[List[int]] = None,
    blocks: Optional[List[int]] = None,
    related_to: Optional[List[int]] = None,
    custom_message: Optional[str] = None,
    bidirectional: bool = False,
    dry_run: bool = False,
):
    """Link issues with dependency comments.

    Args:
        issue_number: Issue number to update
        repo: Repository object
        blocked_by: Issue numbers that block this issue
        blocks: Issue numbers that this issue blocks
        related_to: Related issues (no dependency)
        custom_message: Custom message to include in comments
        bidirectional: Also add reverse links to target issues
        dry_run: Show changes without applying
    """
    try:
        # Get main issue
        issue = repo.get_issue(issue_number)

        print(f"🔗 Linking issue #{issue.number}: {issue.title}")
        print(f"   URL: {issue.html_url}")
        print()

        comments_to_add = []

        # Prepare comments
        if blocked_by:
            comment = format_blocked_by_comment(blocked_by, custom_message)
            comments_to_add.append(
                (
                    issue,
                    comment,
                    f"blocked by: {', '.join(f'#{n}' for n in blocked_by)}",
                )
            )

            # Add reverse links if bidirectional
            if bidirectional:
                for blocker_num in blocked_by:
                    blocker = repo.get_issue(blocker_num)
                    reverse_comment = format_blocks_comment(
                        [issue_number], custom_message
                    )
                    comments_to_add.append(
                        (blocker, reverse_comment, f"blocks: #{issue_number}")
                    )

        if blocks:
            comment = format_blocks_comment(blocks, custom_message)
            comments_to_add.append(
                (issue, comment, f"blocks: {', '.join(f'#{n}' for n in blocks)}")
            )

            # Add reverse links if bidirectional
            if bidirectional:
                for blocked_num in blocks:
                    blocked = repo.get_issue(blocked_num)
                    reverse_comment = format_blocked_by_comment(
                        [issue_number], custom_message
                    )
                    comments_to_add.append(
                        (blocked, reverse_comment, f"blocked by: #{issue_number}")
                    )

        if related_to:
            comment = format_related_comment(related_to, custom_message)
            comments_to_add.append(
                (
                    issue,
                    comment,
                    f"related to: {', '.join(f'#{n}' for n in related_to)}",
                )
            )

            # Add reverse links if bidirectional
            if bidirectional:
                for related_num in related_to:
                    related = repo.get_issue(related_num)
                    reverse_comment = format_related_comment(
                        [issue_number], custom_message
                    )
                    comments_to_add.append(
                        (related, reverse_comment, f"related to: #{issue_number}")
                    )

        # Show planned changes
        print("📋 Planned comments:")
        for target_issue, _comment_text, description in comments_to_add:
            print(f"   • Issue #{target_issue.number}: {description}")
        print()

        # Apply changes if not dry run
        if dry_run:
            print("⚠️  DRY RUN - No changes applied")
            print("\nPreview of comments:\n")
            for target_issue, comment_text, _description in comments_to_add:
                print(f"--- Comment for #{target_issue.number} ---")
                print(comment_text)
                print()
            return

        # Add comments
        for target_issue, comment_text, _description in comments_to_add:
            target_issue.create_comment(comment_text)
            print(f"✅ Added comment to issue #{target_issue.number}")

        print("\n🎯 Issues linked successfully!")
        print(f"   Main issue: {issue.html_url}")

    except GithubException as e:
        print(f"❌ GitHub API error: {e.data.get('message', str(e))}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Link GitHub issues with dependency comments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Mark issue as blocked by others
  %(prog)s 31 --blocked-by 27,28,29

  # Mark issue as blocking another
  %(prog)s 27 --blocks 31

  # Create bidirectional link
  %(prog)s 31 --blocked-by 27 --bidirectional

  # Add related issues
  %(prog)s 31 --related-to 19,20

  # With custom message
  %(prog)s 31 --blocked-by 27 --comment "Waiting for core features"

  # Preview without applying
  %(prog)s 31 --blocked-by 27,28 --dry-run
        """,
    )

    parser.add_argument("issue_number", type=int, help="Issue number to update")

    parser.add_argument(
        "--blocked-by",
        help="Comma-separated list of issue numbers that block this issue",
    )

    parser.add_argument(
        "--blocks",
        help="Comma-separated list of issue numbers that this issue blocks",
    )

    parser.add_argument(
        "--related-to",
        help="Comma-separated list of related issues (no dependency)",
    )

    parser.add_argument(
        "--comment",
        dest="custom_message",
        help="Custom message to include in comments",
    )

    parser.add_argument(
        "--bidirectional",
        action="store_true",
        help="Also add reverse links to target issues",
    )

    parser.add_argument(
        "--repo",
        help="Repository (owner/repo). Auto-detected from git if not provided",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show changes without applying them",
    )

    args = parser.parse_args()

    # Parse issue lists
    blocked_by = (
        [int(n.strip()) for n in args.blocked_by.split(",") if n.strip()]
        if args.blocked_by
        else None
    )
    blocks = (
        [int(n.strip()) for n in args.blocks.split(",") if n.strip()]
        if args.blocks
        else None
    )
    related_to = (
        [int(n.strip()) for n in args.related_to.split(",") if n.strip()]
        if args.related_to
        else None
    )

    # Validate: at least one relationship type required
    if not any([blocked_by, blocks, related_to]):
        print(
            "❌ Error: Must specify at least one of --blocked-by, --blocks, or --related-to",
            file=sys.stderr,
        )
        sys.exit(2)

    # Get repository
    repo = get_repo(args.repo)

    # Link issues
    link_issues(
        issue_number=args.issue_number,
        repo=repo,
        blocked_by=blocked_by,
        blocks=blocks,
        related_to=related_to,
        custom_message=args.custom_message,
        bidirectional=args.bidirectional,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
