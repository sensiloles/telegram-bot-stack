#!/usr/bin/env python3
"""Check CI Status - View GitHub Actions check runs.

This script checks CI/CD status for Pull Requests or commits in the repository.

Usage:
    # Check PR status
    python check_ci.py --pr 5

    # Check specific commit
    python check_ci.py --commit abc123

    # Check latest commit on branch
    python check_ci.py --branch main

    # Check all recent PRs
    python check_ci.py --list-prs

    # JSON output
    python check_ci.py --pr 5 --json

Environment Variables:
    GITHUB_TOKEN: GitHub personal access token (required)
                  Needs 'repo' scope for private repos
                  or 'public_repo' for public repos

Requirements:
    - Classic token with 'repo' scope (for check runs access)
    - Fine-grained token with 'Commit statuses: Read' permission
"""

import argparse
import json
import sys

from github_helper import GithubException, get_repo


def format_duration(started, completed):
    """Format duration between two timestamps."""
    if not started or not completed:
        return "N/A"
    duration = (completed - started).total_seconds()
    if duration < 60:
        return f"{int(duration)}s"
    elif duration < 3600:
        return f"{int(duration / 60)}m {int(duration % 60)}s"
    else:
        hours = int(duration / 3600)
        minutes = int((duration % 3600) / 60)
        return f"{hours}h {minutes}m"


def check_pr_status(repo, pr_number: int, json_output: bool = False):
    """Check CI status for a Pull Request.

    Args:
        repo: Repository object
        pr_number: PR number
        json_output: Output as JSON
    """
    try:
        pr = repo.get_pull(pr_number)

        if json_output:
            result = {
                "pr_number": pr.number,
                "title": pr.title,
                "state": pr.state,
                "mergeable": pr.mergeable,
                "mergeable_state": pr.mergeable_state,
                "checks": [],
            }
        else:
            print(f"📝 PR #{pr.number}: {pr.title}")
            print(f"   State: {pr.state}")
            print(f"   Mergeable: {pr.mergeable}")
            print(f"   Mergeable state: {pr.mergeable_state}")
            print(f"   URL: {pr.html_url}")
            print("\n📊 CI Status:")
            print("=" * 80)

        # Get check runs
        commit = repo.get_commit(pr.head.sha)
        check_runs = list(commit.get_check_runs())

        if not check_runs:
            if json_output:
                result["message"] = "No check runs found"
                print(json.dumps(result, indent=2))
            else:
                print("No check runs found")
            return

        passing = failing = running = 0

        for check in check_runs:
            if check.conclusion == "success":
                passing += 1
                status = "success"
                icon = "✅"
            elif check.conclusion == "failure":
                failing += 1
                status = "failure"
                icon = "❌"
            elif check.conclusion == "cancelled":
                status = "cancelled"
                icon = "⏹️"
            elif check.conclusion == "skipped":
                status = "skipped"
                icon = "⏭️"
            else:
                running += 1
                status = check.status or "unknown"
                icon = "⏳"

            duration = format_duration(check.started_at, check.completed_at)

            if json_output:
                result["checks"].append(
                    {
                        "name": check.name,
                        "status": check.status,
                        "conclusion": check.conclusion,
                        "url": check.html_url,
                        "started_at": (
                            check.started_at.isoformat() if check.started_at else None
                        ),
                        "completed_at": (
                            check.completed_at.isoformat()
                            if check.completed_at
                            else None
                        ),
                        "duration": duration,
                    }
                )
            else:
                print(f"{icon} {check.name}")
                print(f"   Status: {check.status}")
                print(f"   Conclusion: {check.conclusion}")
                print(f"   Duration: {duration}")
                if check.conclusion == "failure":
                    print(f"   URL: {check.html_url}")
                print()

        if json_output:
            result["summary"] = {
                "total": len(check_runs),
                "passing": passing,
                "failing": failing,
                "running": running,
            }
            print(json.dumps(result, indent=2, default=str))
        else:
            print("=" * 80)
            print(
                f"📈 Summary: ✅ {passing} passed | ❌ {failing} failed | ⏳ {running} running"
            )

            if failing > 0:
                print(f"\n⚠️  {failing} check(s) failing!")
                sys.exit(1)
            elif running > 0:
                print(f"\n⏳ {running} check(s) still running...")
            else:
                print("\n✅ All checks passed!")

    except GithubException as e:
        print("❌ Error: Failed to get PR status", file=sys.stderr)
        if e.status == 404:
            print(f"PR #{pr_number} not found", file=sys.stderr)
        elif e.status == 403:
            print("Token missing required permissions", file=sys.stderr)
            print(
                "Required: 'repo' scope (classic) or 'Commit statuses: Read'",
                file=sys.stderr,
            )
        else:
            print(f"GitHub API error: {e}", file=sys.stderr)
        sys.exit(1)


def check_commit_status(repo, commit_sha: str, json_output: bool = False):
    """Check CI status for a specific commit.

    Args:
        repo: Repository object
        commit_sha: Commit SHA
        json_output: Output as JSON
    """
    try:
        commit = repo.get_commit(commit_sha)

        if json_output:
            result = {
                "commit": commit_sha,
                "message": commit.commit.message.split("\n")[0],
                "author": commit.commit.author.name,
                "date": commit.commit.author.date.isoformat(),
                "checks": [],
            }
        else:
            print(f"📝 Commit: {commit_sha[:8]}")
            print(f"   Message: {commit.commit.message.split(chr(10))[0]}")
            print(f"   Author: {commit.commit.author.name}")
            print(f"   Date: {commit.commit.author.date}")
            print("\n📊 CI Status:")
            print("=" * 80)

        check_runs = list(commit.get_check_runs())

        if not check_runs:
            if json_output:
                result["message"] = "No check runs found"
                print(json.dumps(result, indent=2))
            else:
                print("No check runs found")
            return

        passing = failing = running = 0

        for check in check_runs:
            if check.conclusion == "success":
                passing += 1
                icon = "✅"
            elif check.conclusion == "failure":
                failing += 1
                icon = "❌"
            else:
                running += 1
                icon = "⏳"

            if json_output:
                result["checks"].append(
                    {
                        "name": check.name,
                        "status": check.status,
                        "conclusion": check.conclusion,
                        "url": check.html_url,
                    }
                )
            else:
                print(f"{icon} {check.name}: {check.conclusion or check.status}")

        if json_output:
            result["summary"] = {
                "total": len(check_runs),
                "passing": passing,
                "failing": failing,
                "running": running,
            }
            print(json.dumps(result, indent=2, default=str))
        else:
            print()
            print(
                f"📈 Summary: ✅ {passing} passed | ❌ {failing} failed | ⏳ {running} running"
            )

    except GithubException as e:
        print("❌ Error: Failed to get commit status", file=sys.stderr)
        print(f"GitHub API error: {e}", file=sys.stderr)
        sys.exit(1)


def check_branch_status(repo, branch_name: str, json_output: bool = False):
    """Check CI status for latest commit on a branch.

    Args:
        repo: Repository object
        branch_name: Branch name
        json_output: Output as JSON
    """
    try:
        branch = repo.get_branch(branch_name)
        commit_sha = branch.commit.sha

        if not json_output:
            print(f"🌿 Branch: {branch_name}")
            print(f"   Latest commit: {commit_sha[:8]}\n")

        check_commit_status(repo, commit_sha, json_output)

    except GithubException as e:
        print("❌ Error: Failed to get branch status", file=sys.stderr)
        if e.status == 404:
            print(f"Branch '{branch_name}' not found", file=sys.stderr)
        else:
            print(f"GitHub API error: {e}", file=sys.stderr)
        sys.exit(1)


def list_recent_prs(repo, state: str = "open", limit: int = 10):
    """List recent Pull Requests with their CI status.

    Args:
        repo: Repository object
        state: PR state ('open', 'closed', 'all')
        limit: Maximum number of PRs to show
    """
    try:
        print(f"📋 Recent Pull Requests ({state}):")
        print("=" * 80)

        prs = repo.get_pulls(state=state, sort="updated", direction="desc")

        for pr in prs[:limit]:
            # Get check runs for PR
            commit = repo.get_commit(pr.head.sha)
            check_runs = list(commit.get_check_runs())

            passing = sum(1 for c in check_runs if c.conclusion == "success")
            failing = sum(1 for c in check_runs if c.conclusion == "failure")
            running = sum(
                1
                for c in check_runs
                if c.conclusion is None and c.status != "completed"
            )

            # Status indicator
            if failing > 0:
                status = f"❌ {failing} failing"
            elif running > 0:
                status = f"⏳ {running} running"
            elif passing > 0:
                status = f"✅ {passing} passing"
            else:
                status = "⚪ No checks"

            print(f"#{pr.number} [{pr.state.upper()}] {pr.title}")
            print(f"   CI: {status}")
            print(f"   URL: {pr.html_url}")
            print()

    except GithubException as e:
        print("❌ Error: Failed to list PRs", file=sys.stderr)
        print(f"GitHub API error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check GitHub Actions CI status",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check PR #5
  python check_ci.py --pr 5

  # Check specific commit
  python check_ci.py --commit abc123def

  # Check latest on main branch
  python check_ci.py --branch main

  # List recent open PRs
  python check_ci.py --list-prs

  # List all PRs
  python check_ci.py --list-prs --state all

  # JSON output
  python check_ci.py --pr 5 --json
        """,
    )

    parser.add_argument("--pr", type=int, help="Pull Request number to check")

    parser.add_argument("--commit", type=str, help="Commit SHA to check")

    parser.add_argument(
        "--branch", type=str, help="Branch name to check (latest commit)"
    )

    parser.add_argument(
        "--list-prs", action="store_true", help="List recent Pull Requests"
    )

    parser.add_argument(
        "--state",
        type=str,
        default="open",
        choices=["open", "closed", "all"],
        help="PR state filter (for --list-prs)",
    )

    parser.add_argument(
        "--limit", type=int, default=10, help="Number of PRs to show (for --list-prs)"
    )

    parser.add_argument(
        "--json", action="store_true", help="Output as JSON (for --pr or --commit)"
    )

    parser.add_argument(
        "--repo",
        type=str,
        help="Repository in format owner/repo (auto-detected if not specified)",
    )

    args = parser.parse_args()

    # Validate arguments
    if not any([args.pr, args.commit, args.branch, args.list_prs]):
        parser.error("One of --pr, --commit, --branch, or --list-prs must be specified")

    try:
        # Get repository
        repo = get_repo(args.repo)

        if not args.json:
            print(f"🔍 Repository: {repo.full_name}\n")

        # Execute requested action
        if args.pr:
            check_pr_status(repo, args.pr, args.json)
        elif args.commit:
            check_commit_status(repo, args.commit, args.json)
        elif args.branch:
            check_branch_status(repo, args.branch, args.json)
        elif args.list_prs:
            list_recent_prs(repo, args.state, args.limit)

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
