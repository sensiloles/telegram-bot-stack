#!/usr/bin/env python3
"""
Project Overview - Quick status snapshot.

Shows:
- Current branch and status
- Open issues
- Open PRs with CI status
- Recent commits
- Test coverage
- Project metrics

Usage:
    python project_overview.py
    python project_overview.py --detailed
"""

import argparse
import subprocess
import sys
from pathlib import Path

from github_helper import get_repo


def run_command(cmd, capture=True):
    """Run command and return output."""
    try:
        if capture:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, timeout=10
            )
            return result.stdout.strip()
        else:
            subprocess.run(cmd, check=True)
            return ""
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def get_git_info():
    """Get current git information."""
    branch = run_command(["git", "branch", "--show-current"])
    commit = run_command(["git", "log", "-1", "--oneline"])
    status = run_command(["git", "status", "--porcelain"])

    uncommitted = len(status.split("\n")) if status else 0

    return {
        "branch": branch,
        "commit": commit,
        "uncommitted": uncommitted,
    }


def get_test_coverage():
    """Get test coverage from last run."""
    coverage_file = Path("coverage.xml")
    if not coverage_file.exists():
        return None

    try:
        import xml.etree.ElementTree as ET

        tree = ET.parse(coverage_file)
        root = tree.getroot()
        coverage = float(root.attrib.get("line-rate", 0)) * 100
        return f"{coverage:.2f}%"
    except Exception:
        return None


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Project overview")
    parser.add_argument(
        "--detailed", "-d", action="store_true", help="Show detailed information"
    )
    args = parser.parse_args()

    print("╔═══════════════════════════════════════════════════════════╗")
    print("║          📊 telegram-bot-stack - Project Overview        ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()

    # Git info
    print("🌿 Git Status:")
    print("─" * 60)
    git_info = get_git_info()
    print(f"   Branch: {git_info['branch']}")
    print(f"   Latest: {git_info['commit']}")
    if git_info["uncommitted"] > 0:
        print(f"   ⚠️  {git_info['uncommitted']} uncommitted changes")
    else:
        print("   ✅ Working tree clean")
    print()

    # Coverage
    print("📈 Test Coverage:")
    print("─" * 60)
    coverage = get_test_coverage()
    if coverage:
        print(f"   Coverage: {coverage}")
    else:
        print("   Run 'make test-cov' to generate coverage report")
    print()

    # GitHub info (if token available)
    try:
        repo = get_repo()

        # Open PRs
        print("📝 Pull Requests:")
        print("─" * 60)
        prs = list(repo.get_pulls(state="open"))[:5]
        if prs:
            for pr in prs:
                # Get CI status
                commit = repo.get_commit(pr.head.sha)
                check_runs = list(commit.get_check_runs())

                passing = sum(1 for c in check_runs if c.conclusion == "success")
                failing = sum(1 for c in check_runs if c.conclusion == "failure")

                if failing > 0:
                    status = f"❌ {failing} failing"
                elif check_runs:
                    status = f"✅ {passing} passing"
                else:
                    status = "⚪ No checks"

                print(f"   #{pr.number}: {pr.title[:50]}")
                print(f"           {status}")
                if args.detailed:
                    print(f"           URL: {pr.html_url}")
        else:
            print("   No open PRs")
        print()

        # Open Issues
        print("📋 Issues:")
        print("─" * 60)
        issues = list(repo.get_issues(state="open"))[:5]
        if issues:
            for issue in issues:
                labels = [label.name for label in issue.labels]
                label_str = f" [{', '.join(labels)}]" if labels else ""
                print(f"   #{issue.number}: {issue.title[:50]}{label_str}")
                if args.detailed:
                    print(f"           URL: {issue.html_url}")
        else:
            print("   No open issues")
        print()

    except Exception as e:
        print(f"⚠️  Could not fetch GitHub data: {e}")
        print("   Set GITHUB_TOKEN to see PRs and issues")
        print()

    # Quick commands
    print("🚀 Quick Commands:")
    print("─" * 60)
    print("   ./dev test        - Run tests")
    print("   ./dev lint        - Check code")
    print("   ./dev status      - Detailed status")
    print("   make help         - All commands")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
