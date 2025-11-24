#!/usr/bin/env python3
"""List pull requests."""

import argparse

from common import get_github_client, get_repository_name, print_info, print_success


def list_prs(
    state: str = "open",
    author: str | None = None,
    label: str | None = None,
) -> None:
    """List pull requests."""
    g = get_github_client()
    repo_name = get_repository_name()
    repo = g.get_repo(repo_name)

    # Build filter kwargs
    kwargs = {"state": state}

    prs = repo.get_pulls(**kwargs)

    count = 0
    for pr in prs:
        # Apply filters
        if author and pr.user.login != author:
            continue

        if label:
            pr_labels = [lbl.name for lbl in pr.labels]
            if label not in pr_labels:
                continue

        count += 1
        status = "🟢" if pr.state == "open" else "🔴"
        draft = " [DRAFT]" if pr.draft else ""

        print(f"{status} #{pr.number}: {pr.title}{draft}")
        print(f"   Author: {pr.user.login}")
        print(f"   Base: {pr.base.ref} ← Head: {pr.head.ref}")

        labels_str = ", ".join([label.name for label in pr.labels])
        if labels_str:
            print(f"   Labels: {labels_str}")

        print(f"   URL: {pr.html_url}")
        print()

    if count == 0:
        print_info(f"No {state} PRs found")
    else:
        print_success(f"Found {count} {state} PR(s)")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="List pull requests")
    parser.add_argument(
        "--state",
        choices=["open", "closed", "all"],
        default="open",
        help="PR state filter (default: open)",
    )
    parser.add_argument(
        "--author",
        help="Filter by author username",
    )
    parser.add_argument(
        "--label",
        help="Filter by label",
    )

    args = parser.parse_args()

    list_prs(state=args.state, author=args.author, label=args.label)


if __name__ == "__main__":
    main()
