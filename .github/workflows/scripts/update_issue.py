#!/usr/bin/env python3
"""Update GitHub Issue - Modify labels, priority, state.

This script updates existing GitHub issues using PyGithub.
Can modify labels, assignees, milestone, and state.

Usage:
    # Change priority
    python update_issue.py 31 --set-priority low

    # Add labels
    python update_issue.py 31 --add-labels blocked,needs-review

    # Remove labels
    python update_issue.py 31 --remove-labels priority:high

    # Replace all labels
    python update_issue.py 31 --set-labels bug,priority:critical

    # Close issue
    python update_issue.py 31 --close --comment "Fixed in #42"

    # Reopen issue
    python update_issue.py 31 --reopen

    # Add comment
    python update_issue.py 31 --comment "Status update: in progress"

    # Multiple operations
    python update_issue.py 31 \
        --remove-labels priority:high \
        --add-labels priority:low,blocked \
        --comment "Blocked by #27, #28, #29"

    # Dry run (show changes without applying)
    python update_issue.py 31 --set-priority low --dry-run

Environment Variables:
    GITHUB_TOKEN: GitHub personal access token (required)
"""

import argparse
import sys
from typing import List, Optional

from github_helper import GithubException, get_repo


def get_current_labels(issue) -> List[str]:
    """Get current issue labels."""
    return [label.name for label in issue.labels]


def update_priority(
    current_labels: List[str], new_priority: str
) -> tuple[List[str], str]:
    """Update priority label in label list.

    Args:
        current_labels: Current label list
        new_priority: New priority (low/medium/high/critical)

    Returns:
        Tuple of (updated labels, change description)
    """
    # Remove existing priority labels
    updated = [label for label in current_labels if not label.startswith("priority:")]

    # Add new priority
    priority_label = f"priority:{new_priority}"
    updated.append(priority_label)

    old_priority = [label for label in current_labels if label.startswith("priority:")]
    old_priority_str = old_priority[0] if old_priority else "none"

    return updated, f"Priority: {old_priority_str} → {priority_label}"


def add_labels(
    current_labels: List[str], labels_to_add: List[str]
) -> tuple[List[str], str]:
    """Add labels to current list.

    Args:
        current_labels: Current label list
        labels_to_add: Labels to add

    Returns:
        Tuple of (updated labels, change description)
    """
    updated = current_labels.copy()
    added = []

    for label in labels_to_add:
        if label not in updated:
            updated.append(label)
            added.append(label)

    if not added:
        return current_labels, "No new labels to add"

    return updated, f"Added labels: {', '.join(added)}"


def remove_labels(
    current_labels: List[str], labels_to_remove: List[str]
) -> tuple[List[str], str]:
    """Remove labels from current list.

    Args:
        current_labels: Current label list
        labels_to_remove: Labels to remove

    Returns:
        Tuple of (updated labels, change description)
    """
    removed = []
    updated = []

    for label in current_labels:
        if label in labels_to_remove:
            removed.append(label)
        else:
            updated.append(label)

    if not removed:
        return current_labels, "No labels to remove"

    return updated, f"Removed labels: {', '.join(removed)}"


def update_issue(
    issue_number: int,
    repo,
    set_priority: Optional[str] = None,
    add_labels_list: Optional[List[str]] = None,
    remove_labels_list: Optional[List[str]] = None,
    set_labels_list: Optional[List[str]] = None,
    comment: Optional[str] = None,
    close: bool = False,
    reopen: bool = False,
    dry_run: bool = False,
):
    """Update GitHub issue.

    Args:
        issue_number: Issue number to update
        repo: Repository object
        set_priority: Set priority to low/medium/high/critical
        add_labels_list: Labels to add
        remove_labels_list: Labels to remove
        set_labels_list: Replace all labels with these
        comment: Add comment to issue
        close: Close the issue
        reopen: Reopen the issue
        dry_run: Show changes without applying
    """
    try:
        # Get issue
        issue = repo.get_issue(issue_number)

        print(f"📝 Updating issue #{issue.number}: {issue.title}")
        print(f"   URL: {issue.html_url}")
        print(f"   Current state: {issue.state}")

        # Get current labels
        current_labels = get_current_labels(issue)
        print(f"   Current labels: {', '.join(current_labels) or 'none'}")
        print()

        changes = []
        new_labels = current_labels.copy()

        # Apply label changes
        if set_labels_list is not None:
            new_labels = set_labels_list
            changes.append(f"Set labels: {', '.join(set_labels_list)}")

        if remove_labels_list:
            new_labels, change = remove_labels(new_labels, remove_labels_list)
            changes.append(change)

        if add_labels_list:
            new_labels, change = add_labels(new_labels, add_labels_list)
            changes.append(change)

        if set_priority:
            new_labels, change = update_priority(new_labels, set_priority)
            changes.append(change)

        # Show planned changes
        if changes:
            print("📋 Planned label changes:")
            for change in changes:
                print(f"   • {change}")
            print(f"   → New labels: {', '.join(new_labels)}")
            print()

        # Show state change
        if close:
            print("🔒 Will close issue")
        elif reopen:
            print("🔓 Will reopen issue")

        # Show comment
        if comment:
            print("💬 Will add comment:")
            print(f"   {comment[:100]}{'...' if len(comment) > 100 else ''}")
            print()

        # Apply changes if not dry run
        if dry_run:
            print("⚠️  DRY RUN - No changes applied")
            return

        # Update labels
        if changes and new_labels != current_labels:
            issue.set_labels(*new_labels)
            print("✅ Labels updated")

        # Update state
        if close and issue.state == "open":
            issue.edit(state="closed")
            print("✅ Issue closed")
        elif reopen and issue.state == "closed":
            issue.edit(state="open")
            print("✅ Issue reopened")

        # Add comment
        if comment:
            issue.create_comment(comment)
            print("✅ Comment added")

        print("\n🎯 Issue updated successfully!")
        print(f"   URL: {issue.html_url}")

    except GithubException as e:
        print(f"❌ GitHub API error: {e.data.get('message', str(e))}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Update GitHub issue labels, priority, state",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Change priority to low
  %(prog)s 31 --set-priority low

  # Add blocked label
  %(prog)s 31 --add-labels blocked

  # Remove high priority, add low priority and blocked
  %(prog)s 31 --remove-labels priority:high --add-labels priority:low,blocked

  # Close issue with comment
  %(prog)s 31 --close --comment "Fixed in #42"

  # Preview changes without applying
  %(prog)s 31 --set-priority critical --dry-run
        """,
    )

    parser.add_argument("issue_number", type=int, help="Issue number to update")

    parser.add_argument(
        "--set-priority",
        choices=["low", "medium", "high", "critical"],
        help="Set priority (replaces existing priority label)",
    )

    parser.add_argument(
        "--add-labels", help="Comma-separated labels to add (e.g. bug,blocked)"
    )

    parser.add_argument("--remove-labels", help="Comma-separated labels to remove")

    parser.add_argument(
        "--set-labels",
        help="Replace all labels with these (comma-separated)",
    )

    parser.add_argument(
        "--comment",
        help="Add comment to issue",
    )

    parser.add_argument(
        "--close",
        action="store_true",
        help="Close the issue",
    )

    parser.add_argument(
        "--reopen",
        action="store_true",
        help="Reopen the issue",
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

    # Validate conflicting options
    if args.close and args.reopen:
        print("❌ Error: Cannot use --close and --reopen together", file=sys.stderr)
        sys.exit(2)

    # Parse label lists
    add_labels_list = (
        [label.strip() for label in args.add_labels.split(",") if label.strip()]
        if args.add_labels
        else None
    )
    remove_labels_list = (
        [label.strip() for label in args.remove_labels.split(",") if label.strip()]
        if args.remove_labels
        else None
    )
    set_labels_list = (
        [label.strip() for label in args.set_labels.split(",") if label.strip()]
        if args.set_labels
        else None
    )

    # Get repository
    repo = get_repo(args.repo)

    # Update issue
    update_issue(
        issue_number=args.issue_number,
        repo=repo,
        set_priority=args.set_priority,
        add_labels_list=add_labels_list,
        remove_labels_list=remove_labels_list,
        set_labels_list=set_labels_list,
        comment=args.comment,
        close=args.close,
        reopen=args.reopen,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
