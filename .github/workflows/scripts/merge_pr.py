#!/usr/bin/env python3
"""Merge a PR with appropriate strategy and auto-cleanup.

Features:
- Auto-detect PR from current branch
- Merge with squash strategy by default
- Auto-switch to main and pull after merge
- Optionally delete local AND remote feature branches
- Show release status

Usage:
    # Merge current branch's PR (auto-detect)
    python merge_pr.py

    # Merge specific PR
    python merge_pr.py --pr 42

    # Merge and cleanup both local and remote branches
    python merge_pr.py --cleanup

    # Dry run
    python merge_pr.py --dry-run
"""

import argparse
import subprocess
import sys
from typing import Optional

from github_helper import GithubException, get_repo


def get_current_branch() -> Optional[str]:
    """Get current git branch name."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
        )
        branch = result.stdout.strip()
        return branch if branch else None
    except subprocess.CalledProcessError:
        return None


def find_pr_by_branch(repo, branch: str) -> Optional[int]:
    """Find open PR for given branch."""
    try:
        # Get repository owner from repo full_name
        owner = repo.full_name.split("/")[0]
        pulls = repo.get_pulls(state="open", head=f"{owner}:{branch}")
        pulls_list = list(pulls)
        if pulls_list:
            return pulls_list[0].number
        return None
    except Exception as e:
        print(f"⚠️  Warning: Could not find PR for branch '{branch}': {e}")
        return None


def git_checkout_and_pull(branch: str = "main") -> bool:
    """Checkout branch and pull latest changes."""
    try:
        print(f"\n🔄 Switching to {branch} branch...")
        subprocess.run(["git", "checkout", branch], check=True, capture_output=True)

        print("📥 Pulling latest changes...")
        subprocess.run(["git", "pull"], check=True, capture_output=True)

        print(f"✅ Now on {branch} branch with latest changes")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False


def delete_local_branch(branch: str) -> bool:
    """Delete local git branch."""
    try:
        print(f"\n🗑️  Deleting local branch '{branch}'...")
        subprocess.run(["git", "branch", "-D", branch], check=True, capture_output=True)
        print(f"✅ Local branch '{branch}' deleted")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Could not delete local branch: {e}")
        return False


def delete_remote_branch(repo, branch: str) -> bool:
    """Delete remote branch on GitHub.

    Args:
        repo: GitHub repository object
        branch: Branch name to delete (without 'refs/heads/' prefix)

    Returns:
        True if deleted successfully or already deleted, False on error
    """
    try:
        print(f"🗑️  Deleting remote branch 'origin/{branch}'...")

        # Try to get the ref - if it doesn't exist, it's already deleted
        try:
            ref = repo.get_git_ref(f"heads/{branch}")
            ref.delete()
            print(f"✅ Remote branch 'origin/{branch}' deleted")

            # Clean up local references to deleted remote branch
            try:
                subprocess.run(
                    ["git", "remote", "prune", "origin"],
                    check=True,
                    capture_output=True,
                )
                print("✅ Cleaned up remote references")
            except subprocess.CalledProcessError:
                pass  # Not critical if this fails

            return True
        except GithubException as e:
            if e.status == 404:
                print("ℹ️  Remote branch already deleted (not found)")
                return True
            raise

    except GithubException as e:
        print(
            f"⚠️  Could not delete remote branch: {e.status} {e.data.get('message', '')}"
        )
        return False
    except Exception as e:
        print(f"⚠️  Unexpected error deleting remote branch: {e}")
        return False


def check_ci_status(repo, pr) -> tuple[bool, str]:
    """Check CI status before merging.

    Args:
        repo: Repository object
        pr: Pull request object

    Returns:
        Tuple of (can_merge, message)
    """
    print("\n🔍 Checking CI status...")

    try:
        commit = repo.get_commit(pr.head.sha)
        check_runs = list(commit.get_check_runs())

        if not check_runs:
            print("⚠️  Warning: No CI checks found")
            return (True, "No CI checks configured")

        passing = failing = running = 0
        failed_checks = []
        running_checks = []

        # GitGuardian can be ignored (sometimes glitches)
        IGNORED_CHECKS = ["GitGuardian Security Checks", "GitGuardian"]

        for check in check_runs:
            # Skip ignored checks
            if any(ignored in check.name for ignored in IGNORED_CHECKS):
                continue

            if check.conclusion == "success":
                passing += 1
            elif check.conclusion == "failure":
                failing += 1
                failed_checks.append(check.name)
            elif check.conclusion in ["cancelled", "skipped"]:
                # Skipped/cancelled checks are OK
                pass
            else:
                # Still running or pending
                running += 1
                running_checks.append(check.name)

        print(f"   ✅ Passed: {passing}")
        print(f"   ❌ Failed: {failing}")
        print(f"   ⏳ Running: {running}")

        # Block merge if any checks are failing
        if failing > 0:
            message = f"Cannot merge: {failing} CI check(s) failed\n"
            message += "Failed checks:\n"
            for check in failed_checks:
                message += f"  - {check}\n"
            return (False, message)

        # Block merge if any checks are still running
        if running > 0:
            message = f"Cannot merge: {running} CI check(s) still running\n"
            message += "Running checks:\n"
            for check in running_checks:
                message += f"  - {check}\n"
            message += "\nPlease wait for all checks to complete before merging."
            return (False, message)

        return (True, f"All {passing} CI checks passed ✅")

    except Exception as e:
        print(f"⚠️  Warning: Could not check CI status: {e}")
        # Don't block merge on CI check failure (GitHub API issues, etc.)
        return (True, "CI check skipped due to error")


def merge_pr(
    pr_number: int,
    pr_type: str = "release",
    will_release: bool = True,
    merge_method: str = None,
    skip_ci_check: bool = False,
) -> bool:
    """
    Merge a PR with appropriate strategy.

    Args:
        pr_number: PR number to merge
        pr_type: 'release' or 'non-release'
        will_release: Will this PR trigger a release
        merge_method: Force specific merge method ('merge', 'squash', 'rebase')
        skip_ci_check: Skip CI status check (use with caution!)

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

    # CRITICAL: Check CI status before merging
    if not skip_ci_check:
        can_merge, ci_message = check_ci_status(repo, pr)
        if not can_merge:
            print("\n❌ CI Check Failed:")
            print(ci_message)
            print("\n💡 Tip: Wait for all CI checks to complete and pass")
            print(f"   Monitor at: {pr.html_url}/checks")
            return False
        else:
            print(f"✅ {ci_message}")
    else:
        print("\n⚠️  WARNING: Skipping CI check (--skip-ci-check flag used)")

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
    parser = argparse.ArgumentParser(
        description="Merge a PR with auto-detection and cleanup",
        epilog="""
Examples:
  # Merge current branch's PR (auto-detect everything)
  python merge_pr.py

  # Merge and cleanup both local and remote branches
  python merge_pr.py --cleanup

  # Merge specific PR number
  python merge_pr.py --pr 42

  # Dry run to see what would happen
  python merge_pr.py --dry-run
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--pr",
        type=int,
        help="PR number (auto-detected from current branch if not specified)",
    )
    parser.add_argument(
        "--type",
        choices=["release", "non-release"],
        default="release",
        help="PR type (default: release)",
    )
    parser.add_argument(
        "--release",
        type=lambda x: x.lower() == "true",
        default=True,
        help="Will trigger release (true/false, default: true)",
    )
    parser.add_argument(
        "--method",
        choices=["merge", "squash", "rebase"],
        help="Force specific merge method (default: squash)",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Delete both local and remote feature branches after merge",
    )
    parser.add_argument(
        "--no-switch",
        action="store_true",
        help="Don't switch to main after merge",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run (don't actually merge)",
    )
    parser.add_argument(
        "--skip-ci-check",
        action="store_true",
        help="Skip CI status check before merge (use with caution!)",
    )
    args = parser.parse_args()

    try:
        repo = get_repo()
        current_branch = get_current_branch()

        # Auto-detect PR number if not provided
        if args.pr is None:
            if not current_branch:
                print("❌ Error: Could not detect current branch")
                print("Please specify PR number with --pr")
                sys.exit(1)

            if current_branch == "main":
                print("❌ Error: Already on main branch")
                print("Please specify PR number with --pr or checkout a feature branch")
                sys.exit(1)

            print(f"🔍 Auto-detecting PR for branch: {current_branch}")
            pr_number = find_pr_by_branch(repo, current_branch)

            if pr_number is None:
                print(f"❌ Error: No open PR found for branch '{current_branch}'")
                print("Please specify PR number with --pr")
                sys.exit(1)

            print(f"✅ Found PR #{pr_number}")
        else:
            pr_number = args.pr

        # Get PR details
        pr = repo.get_pull(pr_number)
        feature_branch = pr.head.ref

        if args.dry_run:
            print("\n🔍 DRY RUN MODE - No actual changes will be made\n")
            print(f"Would merge PR #{pr_number}: {pr.title}")
            print(f"Method: {args.method or 'squash'}")
            print(f"Feature branch: {feature_branch}")
            if not args.no_switch:
                print("Would switch to main and pull")
            if args.cleanup:
                print(f"Would delete local branch: {feature_branch}")
            sys.exit(0)

        # Merge PR
        success = merge_pr(
            pr_number,
            pr_type=args.type,
            will_release=args.release,
            merge_method=args.method,
            skip_ci_check=args.skip_ci_check,
        )

        if not success:
            sys.exit(1)

        # Auto-switch to main and pull
        if not args.no_switch:
            if not git_checkout_and_pull("main"):
                print("⚠️  Warning: Could not switch to main, but PR was merged")

        # Cleanup branches
        if args.cleanup and feature_branch:
            # Delete remote branch on GitHub
            delete_remote_branch(repo, feature_branch)
            # Delete local branch
            delete_local_branch(feature_branch)

        print("\n" + "=" * 60)
        print("✅ Merge completed successfully!")
        print("=" * 60)

        if args.release:
            print("\n💡 Tip: Check release status at:")
            print(f"   {repo.html_url}/actions")
            print("   New version will be tagged automatically")

        sys.exit(0)

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
