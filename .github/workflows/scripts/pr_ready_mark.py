#!/usr/bin/env python3
"""Mark Draft PR as Ready for Review.

This script marks a draft Pull Request as ready for review using GitHub GraphQL API.
The REST API doesn't support changing draft status, so we use GraphQL.

Features:
- Mark draft PR as ready for review
- Check current draft status
- Validate PR exists and is open

Usage:
    # Mark PR as ready
    python pr_ready_mark.py --pr 36

    # Check status first
    python pr_ready_mark.py --pr 36 --check

Environment Variables:
    GITHUB_TOKEN: GitHub personal access token (required)
"""

import argparse
import sys
from typing import Optional

from github_helper import GithubException, get_repo, load_token


def get_pr_node_id(repo, pr_number: int) -> Optional[str]:
    """Get PR node ID for GraphQL API.

    Args:
        repo: Repository object
        pr_number: PR number

    Returns:
        PR node ID or None if not found
    """
    try:
        pr = repo.get_pull(pr_number)
        # PyGithub doesn't expose node_id directly, so we use raw_data
        return pr.raw_data.get("node_id")
    except GithubException as e:
        print(f"❌ Error: PR #{pr_number} not found", file=sys.stderr)
        return None


def mark_pr_ready(pr_number: int, check_only: bool = False) -> bool:
    """Mark draft PR as ready for review.

    Args:
        pr_number: PR number
        check_only: Only check status, don't update

    Returns:
        True if successful or already ready
    """
    repo = get_repo()
    token = load_token()

    try:
        pr = repo.get_pull(pr_number)

        print(f"\n{'=' * 60}")
        print(f"📝 PR #{pr_number}: {pr.title}")
        print(f"{'=' * 60}\n")
        print(f"URL: {pr.html_url}")
        print(f"State: {pr.state}")
        print(f"Draft: {'✓ YES' if pr.draft else '✗ NO'}")
        print(f"Mergeable: {pr.mergeable}")

        if not pr.draft:
            print("\n✅ PR is already ready for review (not a draft)")
            return True

        if check_only:
            print("\n⚠️  PR is still a draft")
            return False

        # Get PR node ID for GraphQL
        node_id = pr.raw_data.get("node_id")
        if not node_id:
            print("\n❌ Error: Could not get PR node ID", file=sys.stderr)
            return False

        print(f"\nPR Node ID: {node_id}")

        # Use GitHub GraphQL API to mark PR as ready
        import requests

        graphql_url = "https://api.github.com/graphql"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # GraphQL mutation to mark PR as ready
        mutation = """
        mutation($pullRequestId: ID!) {
          markPullRequestReadyForReview(input: {pullRequestId: $pullRequestId}) {
            pullRequest {
              id
              number
              isDraft
              state
            }
          }
        }
        """

        payload = {"query": mutation, "variables": {"pullRequestId": node_id}}

        print("\n⏳ Marking PR as ready for review...")
        response = requests.post(graphql_url, json=payload, headers=headers)

        if response.status_code != 200:
            print(f"\n❌ GraphQL API error: {response.status_code}", file=sys.stderr)
            print(response.text, file=sys.stderr)
            return False

        result = response.json()

        if "errors" in result:
            print("\n❌ GraphQL errors:", file=sys.stderr)
            for error in result["errors"]:
                print(f"   {error.get('message', 'Unknown error')}", file=sys.stderr)
            return False

        if "data" in result and result["data"]["markPullRequestReadyForReview"]:
            pr_data = result["data"]["markPullRequestReadyForReview"]["pullRequest"]
            print(f"\n✅ PR #{pr_data['number']} marked as ready for review!")
            print(f"   Draft: {pr_data['isDraft']}")
            print(f"   State: {pr_data['state']}")
            return True
        else:
            print("\n❌ Unexpected response from GraphQL API", file=sys.stderr)
            return False

    except GithubException as e:
        print(f"\n❌ GitHub API error: {e}", file=sys.stderr)
        if e.status == 404:
            print(f"PR #{pr_number} not found", file=sys.stderr)
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Mark draft PR as ready for review",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Mark PR #36 as ready
  python pr_ready_mark.py --pr 36

  # Check PR status without updating
  python pr_ready_mark.py --pr 36 --check

  # Use with specific repo
  python pr_ready_mark.py --pr 36 --repo owner/repo

Notes:
  - Requires GITHUB_TOKEN environment variable
  - Uses GitHub GraphQL API (REST API doesn't support draft status changes)
  - PR must be in draft state to be marked as ready
        """,
    )

    parser.add_argument(
        "--pr", type=int, required=True, help="Pull Request number to mark as ready"
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check draft status, don't update",
    )

    parser.add_argument(
        "--repo",
        type=str,
        help="Repository in format owner/repo (auto-detected if not specified)",
    )

    args = parser.parse_args()

    try:
        success = mark_pr_ready(args.pr, check_only=args.check)
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
