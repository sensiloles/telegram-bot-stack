#!/usr/bin/env python3
"""
Check if PR is ready to merge.

Checks:
- All CI checks passing
- PR is approved (if branch protection enabled)
- No merge conflicts
- Required reviewers approved

Usage:
    python pr_ready.py --pr 5
    python pr_ready.py --pr 5 --verbose
"""

import argparse
import sys

from github_helper import GithubException, get_repo


def check_pr_ready(repo, pr_number: int, verbose: bool = False):
    """Check if PR is ready to merge.

    Args:
        repo: Repository object
        pr_number: PR number
        verbose: Show detailed output

    Returns:
        True if ready, False otherwise
    """
    try:
        pr = repo.get_pull(pr_number)

        if verbose:
            print(f"📝 Checking PR #{pr.number}: {pr.title}")
            print(f"   URL: {pr.html_url}")
            print()

        ready = True
        checks = []

        # Check 1: PR state
        if pr.state != "open":
            checks.append(("❌", f"PR is {pr.state}, not open"))
            ready = False
        else:
            checks.append(("✅", "PR is open"))

        # Check 2: Mergeable
        if pr.mergeable is False:
            checks.append(("❌", "PR has merge conflicts"))
            ready = False
        elif pr.mergeable is None:
            checks.append(("⏳", "Mergeability unknown (GitHub is calculating)"))
        else:
            checks.append(("✅", "No merge conflicts"))

        # Check 3: CI Status
        commit = repo.get_commit(pr.head.sha)
        check_runs = list(commit.get_check_runs())

        if check_runs:
            passing = sum(1 for c in check_runs if c.conclusion == "success")
            failing = sum(1 for c in check_runs if c.conclusion == "failure")
            running = sum(
                1
                for c in check_runs
                if c.conclusion is None and c.status != "completed"
            )

            if failing > 0:
                checks.append(
                    (
                        "❌",
                        f"CI checks failing ({failing} failed, {passing} passed)",
                    )
                )
                ready = False
            elif running > 0:
                checks.append(
                    (
                        "⏳",
                        f"CI checks running ({running} running, {passing} passed)",
                    )
                )
                ready = False
            else:
                checks.append(("✅", f"All CI checks passed ({passing} checks)"))
        else:
            checks.append(("⚪", "No CI checks configured"))

        # Check 4: Reviews
        reviews = list(pr.get_reviews())
        if reviews:
            approved = any(r.state == "APPROVED" for r in reviews)
            changes_requested = any(r.state == "CHANGES_REQUESTED" for r in reviews)

            if changes_requested:
                checks.append(("❌", "Changes requested by reviewers"))
                ready = False
            elif approved:
                checks.append(("✅", "PR approved by reviewers"))
            else:
                checks.append(("⏳", "No approvals yet"))
        else:
            checks.append(("⚪", "No reviews yet"))

        # Check 5: Mergeable state
        if pr.mergeable_state == "clean":
            checks.append(("✅", "Ready to merge (clean state)"))
        elif pr.mergeable_state == "unstable":
            checks.append(("⏳", "CI checks not all passed"))
        elif pr.mergeable_state == "blocked":
            checks.append(("❌", "Merge blocked (check branch protection rules)"))
            ready = False
        elif pr.mergeable_state == "behind":
            checks.append(("⚠️", "Branch is behind base branch"))
        elif pr.mergeable_state == "dirty":
            checks.append(("❌", "Merge conflicts detected"))
            ready = False
        else:
            checks.append(("❓", f"Unknown state: {pr.mergeable_state}"))

        # Print results
        print("🔍 PR Readiness Check:")
        print("=" * 60)
        for icon, msg in checks:
            print(f"{icon} {msg}")
        print("=" * 60)

        if ready:
            print("✅ PR is ready to merge!")
            return True
        else:
            print("❌ PR is NOT ready to merge")
            print("\nResolve the issues above before merging.")
            return False

    except GithubException as e:
        print("❌ Error: Failed to check PR", file=sys.stderr)
        if e.status == 404:
            print(f"PR #{pr_number} not found", file=sys.stderr)
        else:
            print(f"GitHub API error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check if PR is ready to merge",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check PR #5
  python pr_ready.py --pr 5

  # Verbose output
  python pr_ready.py --pr 5 --verbose

  # Use in scripts
  if python pr_ready.py --pr 5 --quiet; then
    echo "Ready to merge!"
  fi
        """,
    )

    parser.add_argument("--pr", type=int, required=True, help="Pull Request number")

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed output"
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Quiet mode (exit code only)",
    )

    parser.add_argument(
        "--repo",
        type=str,
        help="Repository in format owner/repo (auto-detected if not specified)",
    )

    args = parser.parse_args()

    try:
        repo = get_repo(args.repo)

        if not args.quiet:
            print(f"📦 Repository: {repo.full_name}\n")

        ready = check_pr_ready(repo, args.pr, args.verbose or not args.quiet)

        sys.exit(0 if ready else 1)

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        if not args.quiet:
            print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
