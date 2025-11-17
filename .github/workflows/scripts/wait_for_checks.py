#!/usr/bin/env python3
"""Wait for all CI checks to complete."""

import argparse
import sys
import time
from typing import Tuple

from github_helper import get_repo


def wait_for_checks(pr_number: int, timeout: int = 1800) -> Tuple[bool, str]:
    """
    Wait for all checks to complete.

    Returns:
        (success, message): True if all checks passed, False otherwise
    """
    repo = get_repo()
    pr = repo.get_pull(pr_number)

    start_time = time.time()
    check_interval = 30  # Check every 30 seconds

    print(f"⏳ Waiting for checks on PR #{pr_number}...")
    print(f"Timeout: {timeout}s ({timeout // 60} minutes)")

    while True:
        elapsed = time.time() - start_time

        if elapsed > timeout:
            return False, f"⏱️ Timeout after {timeout}s"

        # Get latest commit
        commit = repo.get_commit(pr.head.sha)

        # Get all check runs and statuses
        check_runs = commit.get_check_runs()
        statuses = commit.get_statuses()

        # Analyze check runs
        total_checks = check_runs.totalCount
        if total_checks == 0:
            print("ℹ️ No check runs found yet, waiting...")
            time.sleep(check_interval)
            continue

        completed = 0
        failed = 0
        pending = 0

        for check in check_runs:
            if check.status == "completed":
                completed += 1
                if check.conclusion not in ("success", "neutral", "skipped"):
                    failed += 1
                    print(f"❌ Check failed: {check.name} - {check.conclusion}")
            else:
                pending += 1
                print(f"⏳ Check pending: {check.name} - {check.status}")

        # Check if all completed
        if pending == 0 and completed > 0:
            if failed > 0:
                return False, f"❌ {failed} check(s) failed"
            else:
                return True, f"✅ All {completed} checks passed"

        # Progress update
        print(
            f"📊 Progress: {completed}/{total_checks} completed, {pending} pending, {failed} failed"
        )
        print(f"   Elapsed: {int(elapsed)}s / {timeout}s")

        time.sleep(check_interval)


def main():
    parser = argparse.ArgumentParser(description="Wait for CI checks to complete")
    parser.add_argument("--pr", type=int, required=True, help="PR number")
    parser.add_argument(
        "--timeout", type=int, default=1800, help="Timeout in seconds (default: 1800)"
    )
    args = parser.parse_args()

    try:
        success, message = wait_for_checks(args.pr, args.timeout)
        print(message)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
