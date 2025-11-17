#!/usr/bin/env python3
"""Analyze PR to determine if it will trigger a release."""

import argparse
import os
import re
import sys

from github_helper import get_repo


def analyze_commits(pr_number: int) -> dict:
    """
    Analyze PR commits to determine release type.

    Returns:
        dict with:
        - pr_type: 'release' or 'non-release'
        - will_release: bool
        - version_bump: 'major', 'minor', 'patch', or 'none'
        - commit_types: list of commit types found
        - merge_strategy: recommended merge strategy
    """
    repo = get_repo()
    pr = repo.get_pull(pr_number)

    # Get all commits in PR
    commits = pr.get_commits()

    commit_types = {
        "feat": 0,
        "fix": 0,
        "perf": 0,
        "docs": 0,
        "style": 0,
        "refactor": 0,
        "test": 0,
        "chore": 0,
        "ci": 0,
        "breaking": 0,
    }

    breaking_changes = False

    # Analyze each commit
    for commit in commits:
        message = commit.commit.message
        first_line = message.split("\n")[0]

        # Check for breaking changes
        if "BREAKING CHANGE" in message or "!" in first_line:
            breaking_changes = True
            commit_types["breaking"] += 1

        # Parse conventional commit type
        match = re.match(r"^(\w+)(?:\([^)]+\))?!?:", first_line)
        if match:
            commit_type = match.group(1)
            if commit_type in commit_types:
                commit_types[commit_type] += 1

    # Determine version bump
    if breaking_changes:
        version_bump = "major"
    elif commit_types["feat"] > 0:
        version_bump = "minor"
    elif commit_types["fix"] > 0 or commit_types["perf"] > 0:
        version_bump = "patch"
    else:
        version_bump = "none"

    # Determine if will trigger release
    will_release = version_bump != "none"

    # PR type
    pr_type = "release" if will_release else "non-release"

    # Recommended merge strategy
    # Always use squash for clean history
    merge_strategy = "squash"

    result = {
        "pr_type": pr_type,
        "will_release": will_release,
        "version_bump": version_bump,
        "commit_types": {k: v for k, v in commit_types.items() if v > 0},
        "merge_strategy": merge_strategy,
    }

    return result


def main():
    parser = argparse.ArgumentParser(description="Analyze PR for release impact")
    parser.add_argument("--pr", type=int, required=True, help="PR number")
    args = parser.parse_args()

    try:
        result = analyze_commits(args.pr)

        print(f"\n{'=' * 60}")
        print(f"📊 PR Analysis for #{args.pr}")
        print(f"{'=' * 60}\n")

        print(f"PR Type: {result['pr_type'].upper()}")
        print(
            f"Will Trigger Release: {'✅ YES' if result['will_release'] else '❌ NO'}"
        )
        print(f"Version Bump: {result['version_bump'].upper()}")
        print(f"Merge Strategy: {result['merge_strategy']}")

        print("\nCommit Types Found:")
        for ctype, count in result["commit_types"].items():
            print(f"  - {ctype}: {count}")

        print(f"\n{'=' * 60}\n")

        # Output for GitHub Actions
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write(f"pr_type={result['pr_type']}\n")
                f.write(f"will_release={str(result['will_release']).lower()}\n")
                f.write(f"version_bump={result['version_bump']}\n")
                f.write(f"merge_strategy={result['merge_strategy']}\n")

        sys.exit(0)

    except Exception as e:
        print(f"❌ Error analyzing PR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
