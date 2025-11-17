#!/usr/bin/env python3
"""Merge a PR with appropriate strategy."""

import argparse
import sys

from github_helper import GithubException, get_repo


def merge_pr(
    pr_number: int,
    pr_type: str = "release",
    will_release: bool = True,
    merge_method: str = None,
) -> bool:
    """
    Merge a PR with appropriate strategy.

    Args:
        pr_number: PR number to merge
        pr_type: 'release' or 'non-release'
        will_release: Will this PR trigger a release
        merge_method: Force specific merge method ('merge', 'squash', 'rebase')

    Returns:
        True if merged successfully
    """
    repo = get_repo()
    pr = repo.get_pull(pr_number)

    print(f"\n{'=' * 60}")
    print(f"🔀 Merging PR #{pr_number}")
    print(f"{'=' * 60}\n")

    print(f"Title: {pr.title}")
    print(f"Base: {pr.base.ref}")
    print(f"Head: {pr.head.ref}")
    print(f"PR Type: {pr_type}")
    print(f"Will Release: {'✅ YES' if will_release else '❌ NO'}")

    # Determine merge method
    if merge_method is None:
        # Always use squash for clean history
        merge_method = "squash"

    print(f"Merge Method: {merge_method}")

    # Check if mergeable
    if not pr.mergeable:
        print("❌ PR has conflicts and cannot be merged")
        return False

    # Create merge commit message
    if will_release:
        commit_title = f"{pr.title}"
        commit_message = (
            f"{pr.title}\n\n{pr.body or ''}\n\n🚀 This PR will trigger a release"
        )
    else:
        commit_title = f"{pr.title}"
        commit_message = f"{pr.title}\n\n{pr.body or ''}"

    try:
        # Attempt merge
        print("\n⏳ Attempting to merge...")

        result = pr.merge(
            commit_title=commit_title,
            commit_message=commit_message,
            merge_method=merge_method,
        )

        if result.merged:
            print(f"\n✅ PR #{pr_number} merged successfully!")
            print(f"Merge commit: {result.sha[:7]}")

            if will_release:
                print("\n🚀 Release workflow will start automatically")
                print(f"Monitor at: {repo.html_url}/actions")

            return True
        else:
            print(f"❌ Merge failed: {result.message}")
            return False

    except GithubException as e:
        print(
            f"❌ GitHub API error: {e.status} {e.data.get('message', 'Unknown error')}"
        )
        if e.status == 405:
            print("   PR might have required reviews or checks not passing")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Merge a PR")
    parser.add_argument("--pr", type=int, required=True, help="PR number")
    parser.add_argument(
        "--type",
        choices=["release", "non-release"],
        default="release",
        help="PR type",
    )
    parser.add_argument(
        "--release",
        type=lambda x: x.lower() == "true",
        default=True,
        help="Will trigger release (true/false)",
    )
    parser.add_argument(
        "--method",
        choices=["merge", "squash", "rebase"],
        help="Force specific merge method",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run (don't actually merge)",
    )
    args = parser.parse_args()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No actual merge will occur\n")
        # Still analyze but don't merge
        repo = get_repo()
        pr = repo.get_pull(args.pr)
        print(f"Would merge PR #{args.pr}: {pr.title}")
        print(f"Method: {args.method or ('squash' if args.release else 'merge')}")
        sys.exit(0)

    try:
        success = merge_pr(
            args.pr,
            pr_type=args.type,
            will_release=args.release,
            merge_method=args.method,
        )
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
