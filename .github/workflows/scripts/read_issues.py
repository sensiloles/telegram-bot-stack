#!/usr/bin/env python3
"""GitHub Issues Reader Script.

This script reads GitHub issues using the GitHub API and provides
formatted output for automation and manual review.

Usage:
    python read_issues.py <issue_number>
    python read_issues.py --list
    python read_issues.py --list --state open
    python read_issues.py --list --labels "refactor,priority:high"

Environment Variables:
    GITHUB_TOKEN: GitHub personal access token (required for private repos)
    GITHUB_REPOSITORY: Repository in format "owner/repo" (auto-detected from git)
"""

import argparse
import json
import os
import subprocess
import sys
from typing import Optional


class GitHubIssuesReader:
    """Reader for GitHub issues using GitHub CLI or API."""

    def __init__(self, repo: Optional[str] = None, token: Optional[str] = None):
        """Initialize the issues reader.

        Args:
            repo: Repository in format "owner/repo". If None, auto-detected from git.
            token: GitHub token. If None, uses GITHUB_TOKEN or gh CLI auth.
        """
        self.repo = repo or self._get_repo_from_git()
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.use_gh_cli = self._check_gh_cli()

    def _get_repo_from_git(self) -> str:
        """Get repository from git remote."""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=True,
            )
            remote_url = result.stdout.strip()

            # Parse git@github.com:owner/repo.git or https://github.com/owner/repo.git
            if "github.com" in remote_url:
                # Remove .git suffix
                remote_url = remote_url.rstrip(".git")
                # Extract owner/repo
                if remote_url.startswith("git@github.com:"):
                    return remote_url.replace("git@github.com:", "")
                elif "github.com/" in remote_url:
                    return remote_url.split("github.com/")[-1]

            raise ValueError(f"Could not parse GitHub repo from: {remote_url}")
        except (subprocess.CalledProcessError, ValueError) as e:
            print(f"Error: Could not detect repository from git: {e}", file=sys.stderr)
            print("Please specify repository with --repo owner/repo", file=sys.stderr)
            sys.exit(1)

    def _check_gh_cli(self) -> bool:
        """Check if GitHub CLI is available and authenticated."""
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def get_issue(self, issue_number: int) -> dict:
        """Get a specific issue by number.

        Args:
            issue_number: Issue number

        Returns:
            Issue data as dict
        """
        if self.use_gh_cli:
            return self._get_issue_gh_cli(issue_number)
        else:
            return self._get_issue_api(issue_number)

    def _get_issue_gh_cli(self, issue_number: int) -> dict:
        """Get issue using GitHub CLI."""
        try:
            result = subprocess.run(
                [
                    "gh",
                    "issue",
                    "view",
                    str(issue_number),
                    "--json",
                    "number,title,state,body,labels,assignees,milestone,comments,author,url",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(
                f"Error: Failed to get issue #{issue_number}: {e.stderr}",
                file=sys.stderr,
            )
            sys.exit(1)

    def _get_issue_api(self, issue_number: int) -> dict:
        """Get issue using GitHub API."""
        import urllib.error
        import urllib.request

        url = f"https://api.github.com/repos/{self.repo}/issues/{issue_number}"
        headers = {"Accept": "application/vnd.github.v3+json"}

        if self.token:
            headers["Authorization"] = f"token {self.token}"

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"Error: Issue #{issue_number} not found", file=sys.stderr)
            else:
                print(f"Error: API request failed: {e}", file=sys.stderr)
            sys.exit(1)

    def list_issues(
        self, state: str = "open", labels: Optional[str] = None, limit: int = 30
    ) -> list:
        """List issues with filters.

        Args:
            state: Issue state (open, closed, all)
            labels: Comma-separated labels to filter by
            limit: Maximum number of issues to return

        Returns:
            List of issue dicts
        """
        if self.use_gh_cli:
            return self._list_issues_gh_cli(state, labels, limit)
        else:
            return self._list_issues_api(state, labels, limit)

    def _list_issues_gh_cli(
        self, state: str, labels: Optional[str], limit: int
    ) -> list:
        """List issues using GitHub CLI."""
        cmd = [
            "gh",
            "issue",
            "list",
            "--json",
            "number,title,state,labels,assignees",
            "--limit",
            str(limit),
        ]

        if state != "all":
            cmd.extend(["--state", state])

        if labels:
            cmd.extend(["--label", labels])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to list issues: {e.stderr}", file=sys.stderr)
            sys.exit(1)

    def _list_issues_api(self, state: str, labels: Optional[str], limit: int) -> list:
        """List issues using GitHub API."""
        import urllib.parse
        import urllib.request

        params = {
            "state": state,
            "per_page": limit,
        }
        if labels:
            params["labels"] = labels

        url = f"https://api.github.com/repos/{self.repo}/issues?{urllib.parse.urlencode(params)}"
        headers = {"Accept": "application/vnd.github.v3+json"}

        if self.token:
            headers["Authorization"] = f"token {self.token}"

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as e:
            print(f"Error: API request failed: {e}", file=sys.stderr)
            sys.exit(1)

    def format_issue(self, issue: dict, detailed: bool = True) -> str:
        """Format issue for display.

        Args:
            issue: Issue data dict
            detailed: Whether to include full body

        Returns:
            Formatted string
        """
        output = []
        output.append("=" * 80)
        output.append(
            f"Issue #{issue.get('number', 'N/A')}: {issue.get('title', 'N/A')}"
        )
        output.append("=" * 80)
        output.append(f"State: {issue.get('state', 'N/A').upper()}")

        # Labels
        labels = issue.get("labels", [])
        if labels:
            if isinstance(labels[0], dict):
                label_names = [label["name"] for label in labels]
            else:
                label_names = labels
            output.append(f"Labels: {', '.join(label_names)}")

        # Assignees
        assignees = issue.get("assignees", [])
        if assignees:
            if isinstance(assignees[0], dict):
                assignee_names = [a.get("login", "unknown") for a in assignees]
            else:
                assignee_names = assignees
            output.append(f"Assignees: {', '.join(assignee_names)}")

        # Author
        author = issue.get("author") or issue.get("user")
        if author:
            if isinstance(author, dict):
                output.append(f"Author: {author.get('login', 'unknown')}")
            else:
                output.append(f"Author: {author}")

        # URL
        if "url" in issue or "html_url" in issue:
            url = issue.get("url") or issue.get("html_url")
            output.append(f"URL: {url}")

        output.append("")

        # Body
        if detailed and issue.get("body"):
            output.append("Description:")
            output.append("-" * 80)
            output.append(issue["body"])
            output.append("-" * 80)

        # Comments
        comments = issue.get("comments")
        if isinstance(comments, list) and comments:
            output.append(f"\nComments ({len(comments)}):")
            for i, comment in enumerate(comments, 1):
                output.append(f"\n--- Comment {i} ---")
                output.append(
                    f"Author: {comment.get('author', {}).get('login', 'unknown')}"
                )
                output.append(comment.get("body", ""))

        return "\n".join(output)

    def format_issue_list(self, issues: list) -> str:
        """Format list of issues for display.

        Args:
            issues: List of issue dicts

        Returns:
            Formatted string
        """
        if not issues:
            return "No issues found."

        output = []
        output.append(f"Found {len(issues)} issue(s):")
        output.append("")

        for issue in issues:
            number = issue.get("number", "N/A")
            title = issue.get("title", "N/A")
            state = issue.get("state", "N/A").upper()

            # Get labels
            labels = issue.get("labels", [])
            if labels:
                if isinstance(labels[0], dict):
                    label_str = ", ".join([label["name"] for label in labels])
                else:
                    label_str = ", ".join(labels)
                label_info = f" [{label_str}]"
            else:
                label_info = ""

            output.append(f"#{number} [{state}] {title}{label_info}")

        return "\n".join(output)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Read GitHub issues from the repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get specific issue
  python read_issues.py 1

  # List all open issues
  python read_issues.py --list

  # List closed issues
  python read_issues.py --list --state closed

  # List issues with specific labels
  python read_issues.py --list --labels "bug,priority:high"

  # Export issue to JSON
  python read_issues.py 1 --json > issue_1.json
        """,
    )

    parser.add_argument(
        "issue_number",
        type=int,
        nargs="?",
        help="Issue number to read",
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List issues instead of reading a specific one",
    )

    parser.add_argument(
        "--state",
        choices=["open", "closed", "all"],
        default="open",
        help="Filter issues by state (default: open)",
    )

    parser.add_argument(
        "--labels",
        type=str,
        help="Filter issues by labels (comma-separated)",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=30,
        help="Maximum number of issues to list (default: 30)",
    )

    parser.add_argument(
        "--repo",
        type=str,
        help="Repository in format owner/repo (auto-detected if not specified)",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON instead of formatted text",
    )

    parser.add_argument(
        "--brief",
        action="store_true",
        help="Show brief output without full body",
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.list and args.issue_number is None:
        parser.error("Either provide an issue number or use --list")

    # Initialize reader
    reader = GitHubIssuesReader(repo=args.repo)

    try:
        if args.list:
            # List issues
            issues = reader.list_issues(
                state=args.state,
                labels=args.labels,
                limit=args.limit,
            )

            if args.json:
                print(json.dumps(issues, indent=2))
            else:
                print(reader.format_issue_list(issues))
        else:
            # Get specific issue
            issue = reader.get_issue(args.issue_number)

            if args.json:
                print(json.dumps(issue, indent=2))
            else:
                print(reader.format_issue(issue, detailed=not args.brief))

    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
