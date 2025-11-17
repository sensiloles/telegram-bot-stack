#!/usr/bin/env python3
"""Check if auto-merge is enabled for a PR."""

import argparse
import os
import sys

from github_helper import get_repo


def check_automerge(pr_number: int) -> bool:
    """Check if PR has automerge enabled (via label or setting)."""
    try:
        repo = get_repo()
        pr = repo.get_pull(pr_number)

        # Check if PR has 'automerge' label
        labels = [label.name for label in pr.labels]
        has_automerge_label = "automerge" in labels

        # Check if PR is in draft
        if pr.draft:
            print(f"❌ PR #{pr_number} is in draft mode")
            print("automerge_enabled=false", file=sys.stderr)
            return False

        # Check if PR is mergeable
        if pr.mergeable is False:
            print(f"❌ PR #{pr_number} has merge conflicts")
            print("automerge_enabled=false", file=sys.stderr)
            return False

        if has_automerge_label:
            print(f"✅ Auto-merge enabled for PR #{pr_number}")
            print("automerge_enabled=true", file=sys.stderr)
            return True
        else:
            print(f"ℹ️ Auto-merge not enabled for PR #{pr_number}")
            print("Add 'automerge' label to enable")
            print("automerge_enabled=false", file=sys.stderr)
            return False

    except Exception as e:
        print(f"❌ Error checking auto-merge: {e}", file=sys.stderr)
        print("automerge_enabled=false", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Check if auto-merge is enabled")
    parser.add_argument("--pr", type=int, required=True, help="PR number")
    args = parser.parse_args()

    enabled = check_automerge(args.pr)

    # Output for GitHub Actions
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"automerge_enabled={'true' if enabled else 'false'}\n")

    sys.exit(0 if enabled else 1)


if __name__ == "__main__":
    main()
