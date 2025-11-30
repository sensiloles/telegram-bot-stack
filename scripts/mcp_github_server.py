#!/usr/bin/env python3
"""MCP Server for GitHub Issues and Pull Requests.

Provides comprehensive GitHub workflow management via Model Context Protocol (MCP).
Supports issues, pull requests, CI status, and batch operations.

MCP Protocol: https://modelcontextprotocol.io/

Version: 2.0.0 (Enhanced)
"""

import asyncio
import json
import os
import ssl
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

try:
    import urllib.error
    import urllib.request

    import requests
except ImportError:
    # Fallback to urllib if requests not available
    import urllib.error
    import urllib.request

    requests = None  # type: ignore[assignment]

# Setup paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / ".github" / "workflows" / "scripts"))


def log_debug(message: str) -> None:
    """Log debug message to stderr (won't interfere with JSON-RPC protocol)."""
    print(f"[MCP DEBUG] {message}", file=sys.stderr, flush=True)


def load_env_variables() -> None:
    """Load GITHUB_TOKEN and GITHUB_REPO from .env file if not in environment or is placeholder."""
    env_file = project_root / ".env"

    # Variables to load from .env
    variables = ["GITHUB_TOKEN", "GITHUB_REPO"]

    for var_name in variables:
        env_value = os.getenv(var_name)
        is_placeholder = env_value and (
            (env_value.startswith("${") and env_value.endswith("}"))
            or (var_name == "GITHUB_TOKEN" and len(env_value) < 20)
        )

        if is_placeholder:
            log_debug(f"{var_name} is placeholder, loading from .env")
            env_value = None

        if not env_value and env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{var_name}="):
                        value = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if value and not (
                            value.startswith("${") and value.endswith("}")
                        ):
                            os.environ[var_name] = value
                            log_debug(f"{var_name} loaded from .env")
                            break


def detect_repo_from_git() -> Optional[str]:
    """Detect repository name from git remote."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True,
        )
        remote_url = result.stdout.strip().rstrip(".git")

        if "github.com" not in remote_url:
            return None

        if remote_url.startswith("git@github.com:"):
            return remote_url.replace("git@github.com:", "")
        elif "github.com/" in remote_url:
            return remote_url.split("github.com/")[-1]
    except (subprocess.CalledProcessError, ValueError):
        pass
    return None


# Load environment variables before importing github_helper
load_env_variables()

from github_helper import (
    format_issue_detail,
    format_issue_list,
    get_github_client,
    get_repo,
)

try:
    from github import GithubException
except ImportError:
    # Fallback if PyGithub not installed
    GithubException = Exception  # type: ignore[misc,assignment]


class MCPServer:
    """MCP Server implementation for GitHub issues and pull requests."""

    def __init__(self) -> None:
        self.repo: Optional[Any] = None
        self.repo_name: Optional[str] = None
        self._repo_cache: dict[str, Any] = {}  # Cache for multiple repos
        self._gh_client: Optional[Any] = None  # Cached GitHub client

    async def initialize(self) -> dict:
        """Initialize the server and detect repository."""
        try:
            self.repo_name = os.getenv("GITHUB_REPO") or detect_repo_from_git()

            if self.repo_name:
                log_debug(f"Repository: {self.repo_name}")
                self.repo = get_repo(self.repo_name)
                self._repo_cache[self.repo_name] = self.repo
                log_debug(f"✅ Connected to {self.repo.full_name}")

            return {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}, "resources": {}},
                "serverInfo": {
                    "name": "github-workflow-mcp",
                    "version": "2.0.0",
                    "description": "GitHub Issues & Pull Requests Management",
                },
            }
        except Exception as e:
            log_debug(f"❌ Initialization failed: {e}")
            return {"error": {"code": -32000, "message": f"Failed to initialize: {e}"}}

    def get_repo_cached(self, repo_name: str) -> Any:
        """Get repository with caching.

        Args:
            repo_name: Repository name in format owner/repo

        Returns:
            Cached or newly fetched Repository object
        """
        if repo_name not in self._repo_cache:
            self._repo_cache[repo_name] = get_repo(repo_name)
        return self._repo_cache[repo_name]

    def _analyze_logs_for_errors(self, logs: str) -> dict:
        """Analyze logs and extract key error information.

        Args:
            logs: Raw log text

        Returns:
            Dictionary with error analysis
        """
        lines = logs.split("\n")
        errors: dict[str, list[str]] = {
            "tracebacks": [],
            "assertion_errors": [],
            "import_errors": [],
            "test_failures": [],
            "syntax_errors": [],
            "key_errors": [],
        }

        current_traceback = []
        in_traceback = False

        for i, line in enumerate(lines):
            # Detect tracebacks
            if "Traceback (most recent call last):" in line:
                in_traceback = True
                current_traceback = [line]
            elif in_traceback:
                current_traceback.append(line)
                # End of traceback - usually an exception line
                if (
                    line.strip()
                    and not line.startswith(" ")
                    and not line.startswith("File")
                ):
                    if current_traceback:
                        errors["tracebacks"].append(
                            "\n".join(current_traceback[-10:])
                        )  # Last 10 lines
                    in_traceback = False
                    current_traceback = []

            # Detect specific error types
            if "AssertionError" in line:
                errors["assertion_errors"].append(line)
                # Get context (previous 2 lines)
                if i >= 2:
                    errors["assertion_errors"].append(
                        f"  Context: {lines[i-2].strip()}"
                    )

            if "ImportError" in line or "ModuleNotFoundError" in line:
                errors["import_errors"].append(line)

            if "SyntaxError" in line:
                errors["syntax_errors"].append(line)
                if i < len(lines) - 1:
                    errors["syntax_errors"].append(f"  Next line: {lines[i+1].strip()}")

            if "FAILED" in line and "test" in line.lower():
                errors["test_failures"].append(line)

            if "AttributeError" in line:
                errors["key_errors"].append(line)

        return errors

    def _format_error_analysis(self, errors: dict, job_name: str) -> str:
        """Format error analysis into readable text.

        Args:
            errors: Error analysis dictionary
            job_name: Name of the job

        Returns:
            Formatted error summary
        """
        if not any(errors.values()):
            return ""

        summary = [f"\n🔍 Error Analysis for {job_name}:"]
        summary.append("-" * 80)

        if errors["tracebacks"]:
            summary.append("\n📋 Tracebacks found:")
            for i, tb in enumerate(errors["tracebacks"][:3], 1):  # Max 3 tracebacks
                summary.append(f"\n  Traceback {i}:")
                summary.append(tb[:500])  # Limit length

        if errors["assertion_errors"]:
            summary.append("\n❌ Assertion Errors:")
            for err in errors["assertion_errors"][:5]:
                summary.append(f"  {err}")

        if errors["import_errors"]:
            summary.append("\n📦 Import Errors:")
            for err in errors["import_errors"][:5]:
                summary.append(f"  {err}")

        if errors["syntax_errors"]:
            summary.append("\n🔤 Syntax Errors:")
            for err in errors["syntax_errors"][:5]:
                summary.append(f"  {err}")

        if errors["test_failures"]:
            summary.append("\n🧪 Test Failures:")
            for err in errors["test_failures"][:10]:
                summary.append(f"  {err}")

        if errors["key_errors"]:
            summary.append("\n🔑 Attribute Errors:")
            for err in errors["key_errors"][:5]:
                summary.append(f"  {err}")

        return "\n".join(summary)

    def _get_ci_logs_internal(
        self,
        repo_name: str,
        run_id: int,
        job_name: Optional[str] = None,
        max_lines: int = 100,
        analyze_errors: bool = True,
    ) -> Optional[str]:
        """Get logs from failed CI jobs using GitHub API.

        Args:
            repo_name: Repository name in format owner/repo
            run_id: Workflow run ID
            job_name: Optional specific job name to get logs for
            max_lines: Maximum lines to return per job

        Returns:
            Formatted logs text or None if error
        """
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            return None

        try:
            # Get workflow run jobs
            url = f"https://api.github.com/repos/{repo_name}/actions/runs/{run_id}/jobs"
            headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
            }

            if requests:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                jobs_data = response.json()
            else:
                req = urllib.request.Request(url)
                for key, value in headers.items():
                    req.add_header(key, value)
                # Create SSL context that doesn't verify certificates (for local dev)
                # In production, proper certificates should be used
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                with urllib.request.urlopen(req, context=ssl_context) as response:
                    jobs_data = json.loads(response.read())

            jobs = jobs_data.get("jobs", [])
            if not jobs:
                return None

            # Filter failed jobs
            failed_jobs = [j for j in jobs if j.get("conclusion") == "failure"]
            if job_name:
                failed_jobs = [j for j in failed_jobs if j.get("name") == job_name]

            if not failed_jobs:
                return "✅ No failed jobs found in this run."

            result_lines = []
            result_lines.append(f"📋 CI Logs for Run #{run_id}")
            result_lines.append("=" * 80)
            result_lines.append("")

            for job in failed_jobs:
                job_id = job.get("id")
                job_name_str = job.get("name", "Unknown")
                result_lines.append(f"❌ Job: {job_name_str} (ID: {job_id})")
                result_lines.append("-" * 80)

                # Get logs for this job
                try:
                    log_url = f"https://api.github.com/repos/{repo_name}/actions/jobs/{job_id}/logs"
                    log_headers = {
                        "Accept": "application/vnd.github+json",
                        "Authorization": f"Bearer {token}",
                        "X-GitHub-Api-Version": "2022-11-28",
                    }

                    if requests:
                        log_response = requests.get(
                            log_url, headers=log_headers, timeout=30
                        )
                        log_response.raise_for_status()
                        logs = log_response.text
                    else:
                        log_req = urllib.request.Request(log_url)
                        for key, value in log_headers.items():
                            log_req.add_header(key, value)
                        # Use SSL context
                        ssl_context = ssl.create_default_context()
                        ssl_context.check_hostname = False
                        ssl_context.verify_mode = ssl.CERT_NONE
                        with urllib.request.urlopen(
                            log_req, context=ssl_context
                        ) as log_response:
                            logs = log_response.read().decode("utf-8")

                    # Analyze errors if requested
                    if analyze_errors:
                        error_analysis = self._analyze_logs_for_errors(logs)
                        error_summary = self._format_error_analysis(
                            error_analysis, job_name_str
                        )
                        if error_summary:
                            result_lines.append(error_summary)
                            result_lines.append("")

                    # Get last N lines
                    log_lines = logs.split("\n")
                    if len(log_lines) > max_lines:
                        result_lines.append(
                            f"\n... (showing last {max_lines} of {len(log_lines)} lines) ..."
                        )
                        log_lines = log_lines[-max_lines:]

                    result_lines.extend(log_lines)
                    result_lines.append("")

                except Exception as e:
                    error_code = None
                    if requests:
                        if hasattr(e, "response") and hasattr(e, "response"):
                            response_obj = getattr(e, "response", None)
                            if response_obj is not None:
                                error_code = getattr(response_obj, "status_code", None)
                    else:
                        if hasattr(e, "code"):
                            error_code = getattr(e, "code", None)

                    if error_code == 403:
                        result_lines.append(
                            "⚠️  Permission denied. Token needs 'actions:read' scope."
                        )
                    elif error_code == 404:
                        result_lines.append("⚠️  Logs not available (may have expired).")
                    elif error_code:
                        result_lines.append(f"⚠️  Error fetching logs: {error_code}")
                    else:
                        result_lines.append(f"⚠️  Error: {e}")
                    result_lines.append("")

            return "\n".join(result_lines)

        except urllib.error.HTTPError as e:
            log_debug(f"HTTP error getting CI logs: {e.code} - {e.read().decode()}")
            return None
        except Exception as e:
            log_debug(f"Error getting CI logs: {e}")
            return None

    def format_github_error(self, e: Any) -> str:
        """Format GitHub API error with actionable hints.

        Args:
            e: GithubException

        Returns:
            Formatted error message with hints
        """
        error_msg = f"❌ GitHub API error: {e}"

        if hasattr(e, "status"):
            if e.status == 404:
                error_msg += "\n💡 Hint: Resource not found. Check issue/PR number or repo access."
            elif e.status == 403:
                error_msg += "\n💡 Hint: Rate limit exceeded or insufficient permissions. Check token scopes."
            elif e.status == 401:
                error_msg += (
                    "\n💡 Hint: Token invalid. Check GITHUB_TOKEN in .env file."
                )
            elif e.status == 422:
                error_msg += "\n💡 Hint: Validation failed. Check input parameters."
            else:
                error_msg += (
                    "\n💡 Hint: Check GitHub status: https://www.githubstatus.com/"
                )

        return error_msg

    def list_tools(self) -> dict:
        """List available tools."""
        return {
            "tools": [
                {
                    "name": "list_issues",
                    "description": "List GitHub issues with advanced filters",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "state": {
                                "type": "string",
                                "enum": ["open", "closed", "all"],
                                "description": "Filter by issue state",
                                "default": "open",
                            },
                            "labels": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter by labels",
                            },
                            "milestone": {
                                "type": "string",
                                "description": "Filter by milestone title",
                            },
                            "assignee": {
                                "type": "string",
                                "description": "Filter by assignee username",
                            },
                            "sort": {
                                "type": "string",
                                "enum": ["created", "updated", "comments"],
                                "description": "Sort by field",
                                "default": "created",
                            },
                            "direction": {
                                "type": "string",
                                "enum": ["asc", "desc"],
                                "description": "Sort direction",
                                "default": "desc",
                            },
                            "since": {
                                "type": "string",
                                "description": "Only issues updated after this date (ISO 8601 format)",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of issues to return",
                                "default": 30,
                            },
                            "repo": {
                                "type": "string",
                                "description": "Repository in format owner/repo (auto-detected if not provided)",
                            },
                        },
                    },
                },
                {
                    "name": "get_issue",
                    "description": "Get details of a specific GitHub issue",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "issue_number": {
                                "type": "integer",
                                "description": "Issue number",
                            },
                            "repo": {
                                "type": "string",
                                "description": "Repository in format owner/repo (auto-detected if not provided)",
                            },
                        },
                        "required": ["issue_number"],
                    },
                },
                {
                    "name": "create_issue",
                    "description": "Create a new GitHub issue",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Issue title"},
                            "body": {
                                "type": "string",
                                "description": "Issue body (markdown)",
                            },
                            "labels": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Labels to apply",
                            },
                            "assignees": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Usernames to assign",
                            },
                            "repo": {
                                "type": "string",
                                "description": "Repository in format owner/repo (auto-detected if not provided)",
                            },
                        },
                        "required": ["title", "body"],
                    },
                },
                {
                    "name": "update_issue",
                    "description": "Update an existing GitHub issue (labels, priority, state, comments)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "issue_number": {
                                "type": "integer",
                                "description": "Issue number to update",
                            },
                            "set_priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "critical"],
                                "description": "Set priority (replaces existing priority label)",
                            },
                            "add_labels": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Labels to add",
                            },
                            "remove_labels": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Labels to remove",
                            },
                            "set_labels": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Replace all labels with these",
                            },
                            "comment": {
                                "type": "string",
                                "description": "Add comment to issue",
                            },
                            "close": {
                                "type": "boolean",
                                "description": "Close the issue",
                                "default": False,
                            },
                            "reopen": {
                                "type": "boolean",
                                "description": "Reopen the issue",
                                "default": False,
                            },
                            "repo": {
                                "type": "string",
                                "description": "Repository in format owner/repo (auto-detected if not provided)",
                            },
                        },
                        "required": ["issue_number"],
                    },
                },
                {
                    "name": "batch_update_issues",
                    "description": "Update multiple issues at once (batch operation)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "issue_numbers": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "List of issue numbers to update",
                            },
                            "add_labels": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Labels to add to all issues",
                            },
                            "remove_labels": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Labels to remove from all issues",
                            },
                            "comment": {
                                "type": "string",
                                "description": "Add same comment to all issues",
                            },
                            "close": {
                                "type": "boolean",
                                "description": "Close all issues",
                                "default": False,
                            },
                            "repo": {
                                "type": "string",
                                "description": "Repository in format owner/repo (auto-detected if not provided)",
                            },
                        },
                        "required": ["issue_numbers"],
                    },
                },
                {
                    "name": "create_pr",
                    "description": "Create a new Pull Request",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "PR title (should follow conventional commit format)",
                            },
                            "body": {
                                "type": "string",
                                "description": "PR description (markdown)",
                            },
                            "head": {
                                "type": "string",
                                "description": "Source branch (auto-detected from current branch if not provided)",
                            },
                            "base": {
                                "type": "string",
                                "description": "Target branch",
                                "default": "main",
                            },
                            "draft": {
                                "type": "boolean",
                                "description": "Create as draft PR",
                                "default": False,
                            },
                            "closes_issue": {
                                "type": "integer",
                                "description": "Issue number to close (adds 'Closes #N' to description)",
                            },
                            "auto_assign": {
                                "type": "boolean",
                                "description": "Automatically assign current user to PR (default: true)",
                                "default": True,
                            },
                            "assignee": {
                                "type": "string",
                                "description": "Specific user to assign (defaults to current user if auto_assign=true)",
                            },
                            "repo": {
                                "type": "string",
                                "description": "Repository in format owner/repo (auto-detected if not provided)",
                            },
                        },
                        "required": ["title"],
                    },
                },
                {
                    "name": "merge_pr",
                    "description": "Merge a Pull Request",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "pr_number": {
                                "type": "integer",
                                "description": "PR number to merge (auto-detected from current branch if not provided)",
                            },
                            "merge_method": {
                                "type": "string",
                                "enum": ["merge", "squash", "rebase"],
                                "description": "Merge method",
                                "default": "squash",
                            },
                            "delete_branch": {
                                "type": "boolean",
                                "description": "Delete branch after merge",
                                "default": False,
                            },
                            "repo": {
                                "type": "string",
                                "description": "Repository in format owner/repo (auto-detected if not provided)",
                            },
                        },
                    },
                },
                {
                    "name": "check_ci",
                    "description": "Check CI/CD status for a PR or commit",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "pr_number": {
                                "type": "integer",
                                "description": "PR number to check",
                            },
                            "commit_sha": {
                                "type": "string",
                                "description": "Commit SHA to check (alternative to pr_number)",
                            },
                            "repo": {
                                "type": "string",
                                "description": "Repository in format owner/repo (auto-detected if not provided)",
                            },
                        },
                    },
                },
                {
                    "name": "get_ci_logs",
                    "description": "Get logs from failed CI jobs for a workflow run",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "run_id": {
                                "type": "integer",
                                "description": "Workflow run ID (from check_ci or GitHub Actions URL)",
                            },
                            "job_name": {
                                "type": "string",
                                "description": "Optional: specific job name to get logs for (default: all failed jobs)",
                            },
                            "max_lines": {
                                "type": "integer",
                                "description": "Maximum lines of logs to return per job (default: 100)",
                                "default": 100,
                            },
                            "repo": {
                                "type": "string",
                                "description": "Repository in format owner/repo (auto-detected if not provided)",
                            },
                        },
                        "required": ["run_id"],
                    },
                },
                {
                    "name": "list_prs",
                    "description": "List Pull Requests with filters",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "state": {
                                "type": "string",
                                "enum": ["open", "closed", "all"],
                                "description": "Filter by PR state",
                                "default": "open",
                            },
                            "sort": {
                                "type": "string",
                                "enum": [
                                    "created",
                                    "updated",
                                    "popularity",
                                    "long-running",
                                ],
                                "description": "Sort by field",
                                "default": "created",
                            },
                            "direction": {
                                "type": "string",
                                "enum": ["asc", "desc"],
                                "description": "Sort direction",
                                "default": "desc",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of PRs to return",
                                "default": 20,
                            },
                            "repo": {
                                "type": "string",
                                "description": "Repository in format owner/repo (auto-detected if not provided)",
                            },
                        },
                    },
                },
                {
                    "name": "list_milestones",
                    "description": "List GitHub milestones",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "state": {
                                "type": "string",
                                "enum": ["open", "closed", "all"],
                                "description": "Filter by milestone state",
                                "default": "open",
                            },
                            "sort": {
                                "type": "string",
                                "enum": ["due_on", "completeness"],
                                "description": "Sort by field",
                                "default": "due_on",
                            },
                            "direction": {
                                "type": "string",
                                "enum": ["asc", "desc"],
                                "description": "Sort direction",
                                "default": "asc",
                            },
                            "repo": {
                                "type": "string",
                                "description": "Repository in format owner/repo (auto-detected if not provided)",
                            },
                        },
                    },
                },
                {
                    "name": "create_milestone",
                    "description": "Create a new GitHub milestone",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Milestone title",
                            },
                            "description": {
                                "type": "string",
                                "description": "Milestone description (markdown)",
                            },
                            "due_on": {
                                "type": "string",
                                "description": "Due date (ISO 8601 format: YYYY-MM-DD)",
                            },
                            "state": {
                                "type": "string",
                                "enum": ["open", "closed"],
                                "description": "Milestone state",
                                "default": "open",
                            },
                            "repo": {
                                "type": "string",
                                "description": "Repository in format owner/repo (auto-detected if not provided)",
                            },
                        },
                        "required": ["title"],
                    },
                },
                {
                    "name": "update_milestone",
                    "description": "Update an existing milestone",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "milestone_number": {
                                "type": "integer",
                                "description": "Milestone number",
                            },
                            "title": {
                                "type": "string",
                                "description": "New milestone title",
                            },
                            "description": {
                                "type": "string",
                                "description": "New milestone description",
                            },
                            "due_on": {
                                "type": "string",
                                "description": "New due date (ISO 8601 format)",
                            },
                            "state": {
                                "type": "string",
                                "enum": ["open", "closed"],
                                "description": "New milestone state",
                            },
                            "repo": {
                                "type": "string",
                                "description": "Repository in format owner/repo (auto-detected if not provided)",
                            },
                        },
                        "required": ["milestone_number"],
                    },
                },
                {
                    "name": "set_issue_milestone",
                    "description": "Set milestone for one or more issues",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "issue_numbers": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "Issue number(s) to update",
                            },
                            "milestone_number": {
                                "type": "integer",
                                "description": "Milestone number to assign (or null to remove)",
                            },
                            "repo": {
                                "type": "string",
                                "description": "Repository in format owner/repo (auto-detected if not provided)",
                            },
                        },
                        "required": ["issue_numbers", "milestone_number"],
                    },
                },
            ]
        }

    async def call_tool(self, name: str, arguments: dict) -> dict:
        """Call a tool by name with arguments."""
        repo_name = arguments.get("repo") or self.repo_name

        if not repo_name:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "❌ Repository not specified. Provide 'repo' parameter or set GITHUB_REPO.",
                    }
                ],
                "isError": True,
            }

        # Use cached repo
        repo = self.get_repo_cached(repo_name)

        try:
            if name == "list_issues":
                # Build query parameters
                query_params = {
                    "state": arguments.get("state", "open"),
                    "sort": arguments.get("sort", "created"),
                    "direction": arguments.get("direction", "desc"),
                }

                # Add optional filters
                if arguments.get("labels"):
                    query_params["labels"] = arguments["labels"]
                if arguments.get("milestone"):
                    query_params["milestone"] = arguments["milestone"]
                if arguments.get("assignee"):
                    query_params["assignee"] = arguments["assignee"]
                if arguments.get("since"):
                    try:
                        query_params["since"] = datetime.fromisoformat(
                            arguments["since"].replace("Z", "+00:00")
                        )
                    except ValueError:
                        pass  # Skip invalid date

                issues = repo.get_issues(**query_params)
                result = [
                    issue
                    for i, issue in enumerate(issues)
                    if i < arguments.get("limit", 30)
                ]
                return {
                    "content": [{"type": "text", "text": format_issue_list(result)}],
                    "isError": False,
                }

            elif name == "get_issue":
                issue = repo.get_issue(arguments["issue_number"])
                return {
                    "content": [{"type": "text", "text": format_issue_detail(issue)}],
                    "isError": False,
                }

            elif name == "create_issue":
                issue = repo.create_issue(
                    title=arguments["title"],
                    body=arguments["body"],
                    labels=arguments.get("labels") or [],
                    assignees=arguments.get("assignees") or [],
                )
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"✅ Issue created: #{issue.number}\n"
                            f"   URL: {issue.html_url}\n"
                            f"   Title: {issue.title}",
                        }
                    ],
                    "isError": False,
                }

            elif name == "update_issue":
                issue = repo.get_issue(arguments["issue_number"])
                changes = []

                current_labels = [label.name for label in issue.labels]

                if "set_labels" in arguments:
                    issue.set_labels(*arguments["set_labels"])
                    changes.append(f"Set labels: {', '.join(arguments['set_labels'])}")

                if "add_labels" in arguments:
                    new_labels = list(set(current_labels + arguments["add_labels"]))
                    issue.set_labels(*new_labels)
                    changes.append(
                        f"Added labels: {', '.join(arguments['add_labels'])}"
                    )

                if "remove_labels" in arguments:
                    new_labels = [
                        label
                        for label in current_labels
                        if label not in arguments["remove_labels"]
                    ]
                    issue.set_labels(*new_labels)
                    changes.append(
                        f"Removed labels: {', '.join(arguments['remove_labels'])}"
                    )

                if "set_priority" in arguments:
                    priority = arguments["set_priority"]
                    new_labels = [
                        label
                        for label in current_labels
                        if not label.startswith("priority:")
                    ]
                    new_labels.append(f"priority:{priority}")
                    issue.set_labels(*new_labels)
                    changes.append(f"Set priority: {priority}")

                if arguments.get("close") and issue.state == "open":
                    issue.edit(state="closed")
                    changes.append("Closed issue")

                if arguments.get("reopen") and issue.state == "closed":
                    issue.edit(state="open")
                    changes.append("Reopened issue")

                if "comment" in arguments:
                    issue.create_comment(arguments["comment"])
                    changes.append("Added comment")

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"✅ Issue #{issue.number} updated\n"
                            f"   Changes: {', '.join(changes) if changes else 'None'}\n"
                            f"   URL: {issue.html_url}",
                        }
                    ],
                    "isError": False,
                }

            elif name == "batch_update_issues":
                issue_numbers = arguments["issue_numbers"]
                results = []
                errors = []

                for issue_num in issue_numbers:
                    try:
                        issue = repo.get_issue(issue_num)
                        changes = []

                        current_labels = [label.name for label in issue.labels]

                        if "add_labels" in arguments:
                            new_labels = list(
                                set(current_labels + arguments["add_labels"])
                            )
                            issue.set_labels(*new_labels)
                            changes.append("Added labels")

                        if "remove_labels" in arguments:
                            new_labels = [
                                label
                                for label in current_labels
                                if label not in arguments["remove_labels"]
                            ]
                            issue.set_labels(*new_labels)
                            changes.append("Removed labels")

                        if arguments.get("close") and issue.state == "open":
                            issue.edit(state="closed")
                            changes.append("Closed")

                        if "comment" in arguments:
                            issue.create_comment(arguments["comment"])
                            changes.append("Added comment")

                        results.append(
                            f"✅ #{issue_num}: {', '.join(changes) if changes else 'No changes'}"
                        )
                    except Exception as e:
                        errors.append(f"❌ #{issue_num}: {str(e)}")

                response_text = "📦 Batch update completed\n\n"  # noqa: F541
                response_text += f"✅ Successful: {len(results)}/{len(issue_numbers)}\n"
                if errors:
                    response_text += f"❌ Failed: {len(errors)}/{len(issue_numbers)}\n"
                response_text += "\n" + "\n".join(results)
                if errors:
                    response_text += "\n\nErrors:\n" + "\n".join(errors)

                return {
                    "content": [{"type": "text", "text": response_text}],
                    "isError": len(errors) > 0,
                }

            elif name == "create_pr":
                # Get head branch
                head = arguments.get("head")
                if not head:
                    # Try to detect from git
                    try:
                        git_result = subprocess.run(
                            ["git", "branch", "--show-current"],
                            capture_output=True,
                            text=True,
                            check=True,
                        )
                        head = git_result.stdout.strip()
                    except subprocess.CalledProcessError:
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": "❌ Could not detect current branch. Provide 'head' parameter.",
                                }
                            ],
                            "isError": True,
                        }

                # Build PR body
                body = arguments.get("body", "")
                if arguments.get("closes_issue"):
                    body += f"\n\nCloses #{arguments['closes_issue']}"

                # Create PR
                pr = repo.create_pull(
                    title=arguments["title"],
                    body=body,
                    head=head,
                    base=arguments.get("base", "main"),
                    draft=arguments.get("draft", False),
                )

                # Auto-assign to user
                assignee_info = ""
                auto_assign = arguments.get("auto_assign", True)
                assignee = arguments.get("assignee")

                if auto_assign or assignee:
                    try:
                        # Get user to assign
                        if assignee:
                            user_to_assign = assignee
                        else:
                            # Get current authenticated user
                            gh = get_github_client()
                            current_user = gh.get_user()
                            user_to_assign = current_user.login

                        # Add assignee to PR
                        pr.add_to_assignees(user_to_assign)
                        assignee_info = f"\n   Assigned to: @{user_to_assign}"
                    except Exception as e:
                        assignee_info = f"\n   ⚠️  Could not assign user: {e}"

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"✅ Pull Request created\n"
                            f"   Number: #{pr.number}\n"
                            f"   Title: {pr.title}\n"
                            f"   From: {head} → {arguments.get('base', 'main')}\n"
                            f"   URL: {pr.html_url}{assignee_info}",
                        }
                    ],
                    "isError": False,
                }

            elif name == "merge_pr":
                # Get PR number
                pr_number = arguments.get("pr_number")
                if not pr_number:
                    # Try to detect from current branch
                    try:
                        git_result = subprocess.run(
                            ["git", "branch", "--show-current"],
                            capture_output=True,
                            text=True,
                            check=True,
                        )
                        branch = git_result.stdout.strip()
                        owner = repo.full_name.split("/")[0]
                        pulls = list(
                            repo.get_pulls(state="open", head=f"{owner}:{branch}")
                        )
                        if pulls:
                            pr_number = pulls[0].number
                        else:
                            return {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"❌ No open PR found for branch '{branch}'",
                                    }
                                ],
                                "isError": True,
                            }
                    except subprocess.CalledProcessError:
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": "❌ Could not detect PR. Provide 'pr_number' parameter.",
                                }
                            ],
                            "isError": True,
                        }

                pr = repo.get_pull(pr_number)

                # Check if mergeable
                if not pr.mergeable:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"❌ PR #{pr_number} has conflicts and cannot be merged",
                            }
                        ],
                        "isError": True,
                    }

                # Merge PR
                merge_method = arguments.get("merge_method", "squash")
                result = pr.merge(
                    commit_title=pr.title,
                    commit_message=pr.body or "",
                    merge_method=merge_method,
                )

                response_text = f"✅ PR #{pr_number} merged successfully\n"
                response_text += f"   Method: {merge_method}\n"
                response_text += f"   Commit: {result.sha[:7]}\n"

                # Delete branch if requested
                if arguments.get("delete_branch"):
                    try:
                        ref = repo.get_git_ref(f"heads/{pr.head.ref}")
                        ref.delete()
                        response_text += f"   Branch '{pr.head.ref}' deleted\n"
                    except Exception as e:
                        response_text += f"   ⚠️ Could not delete branch: {e}\n"

                return {
                    "content": [{"type": "text", "text": response_text}],
                    "isError": False,
                }

            elif name == "check_ci":
                # Get commit SHA
                if arguments.get("pr_number"):
                    pr = repo.get_pull(arguments["pr_number"])
                    commit_sha = pr.head.sha
                    context = f"PR #{pr.number}"
                elif arguments.get("commit_sha"):
                    commit_sha = arguments["commit_sha"]
                    context = f"Commit {commit_sha[:8]}"
                else:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": "❌ Provide either 'pr_number' or 'commit_sha'",
                            }
                        ],
                        "isError": True,
                    }

                # Get check runs
                commit = repo.get_commit(commit_sha)
                check_runs = list(commit.get_check_runs())

                if not check_runs:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"ℹ️ No CI checks found for {context}",
                            }
                        ],
                        "isError": False,
                    }

                # Analyze checks
                passing = sum(1 for c in check_runs if c.conclusion == "success")
                failing = sum(1 for c in check_runs if c.conclusion == "failure")
                running = sum(
                    1
                    for c in check_runs
                    if c.conclusion is None and c.status != "completed"
                )

                response_text = f"📊 CI Status for {context}\n\n"
                response_text += f"✅ Passed: {passing} | ❌ Failed: {failing} | ⏳ Running: {running}\n\n"

                # Get workflow run ID for failed checks (for log retrieval)
                failed_run_ids = []
                for check in check_runs:
                    if check.conclusion == "success":
                        icon = "✅"
                    elif check.conclusion == "failure":
                        icon = "❌"
                        # Try to get run_id from check details
                        if hasattr(check, "details_url") and check.details_url:
                            # Extract run_id from URL if possible
                            try:
                                # URL format: https://github.com/owner/repo/actions/runs/RUN_ID/job/JOB_ID
                                if "/actions/runs/" in check.details_url:
                                    run_id = check.details_url.split("/actions/runs/")[
                                        1
                                    ].split("/")[0]
                                    failed_run_ids.append(int(run_id))
                            except (ValueError, IndexError):
                                pass
                    else:
                        icon = "⏳"
                    response_text += (
                        f"{icon} {check.name}: {check.conclusion or 'running'}\n"
                    )

                # If there are failures, suggest getting logs
                if failing > 0 and failed_run_ids:
                    response_text += f"\n💡 Use 'get_ci_logs' with run_id={failed_run_ids[0]} to see error details"

                # If there are failures, automatically get and analyze logs
                if failing > 0:
                    workflow_run_id = None
                    # Try to get workflow run ID from commit
                    try:
                        # Get workflow runs for this commit
                        workflow_runs = list(
                            repo.get_workflow_runs(head_sha=commit_sha)
                        )
                        if workflow_runs:
                            # Get the most recent run
                            latest_run = workflow_runs[0]
                            workflow_run_id = latest_run.id
                    except Exception as e:
                        log_debug(f"Could not get workflow runs: {e}")
                        # Fallback: try to extract from check details_url
                        for check in check_runs:
                            if check.conclusion == "failure" and hasattr(
                                check, "details_url"
                            ):
                                try:
                                    if "/actions/runs/" in check.details_url:
                                        run_id_str = check.details_url.split(
                                            "/actions/runs/"
                                        )[1].split("/")[0]
                                        workflow_run_id = int(run_id_str)
                                        break
                                except (ValueError, IndexError, AttributeError):
                                    pass

                    # If we found a run_id, get and analyze logs
                    if workflow_run_id:
                        try:
                            logs_result = self._get_ci_logs_internal(
                                repo_name,
                                workflow_run_id,
                                max_lines=100,
                                analyze_errors=True,
                            )
                            if logs_result:
                                response_text += "\n\n📋 Error Logs & Analysis:\n"
                                response_text += "=" * 80 + "\n"
                                response_text += logs_result
                        except Exception as e:
                            log_debug(f"Could not fetch logs: {e}")
                            response_text += f"\n💡 Use 'get_ci_logs' with run_id={workflow_run_id} to see detailed error logs"
                    else:
                        response_text += "\n💡 Use 'get_ci_logs' with run_id to see detailed error logs"

                return {
                    "content": [{"type": "text", "text": response_text}],
                    "isError": failing > 0,
                }

            elif name == "get_ci_logs":
                run_id = arguments["run_id"]
                job_name = arguments.get("job_name")
                max_lines = arguments.get("max_lines", 100)

                logs_text = self._get_ci_logs_internal(
                    repo_name, run_id, job_name, max_lines
                )

                if not logs_text:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"❌ Could not retrieve logs for run {run_id}. Check token permissions.",
                            }
                        ],
                        "isError": True,
                    }

                return {
                    "content": [{"type": "text", "text": logs_text}],
                    "isError": False,
                }

            elif name == "list_prs":
                # Get PRs with filters
                query_params = {
                    "state": arguments.get("state", "open"),
                    "sort": arguments.get("sort", "created"),
                    "direction": arguments.get("direction", "desc"),
                }

                prs = repo.get_pulls(**query_params)
                result = [
                    pr for i, pr in enumerate(prs) if i < arguments.get("limit", 20)
                ]

                if not result:
                    return {
                        "content": [
                            {"type": "text", "text": "No pull requests found."}
                        ],
                        "isError": False,
                    }

                response_text = f"Found {len(result)} pull request(s):\n\n"
                for pr in result:
                    state = "OPEN" if pr.state == "open" else "CLOSED"
                    response_text += f"#{pr.number} [{state}] {pr.title}\n"
                    response_text += f"   {pr.head.ref} → {pr.base.ref}\n"
                    if pr.draft:
                        response_text += "   🚧 Draft\n"
                    response_text += f"   {pr.html_url}\n\n"

                return {
                    "content": [{"type": "text", "text": response_text}],
                    "isError": False,
                }

            elif name == "list_milestones":
                # Get milestones with filters
                query_params = {
                    "state": arguments.get("state", "open"),
                    "sort": arguments.get("sort", "due_on"),
                    "direction": arguments.get("direction", "asc"),
                }

                milestones = list(repo.get_milestones(**query_params))

                if not milestones:
                    return {
                        "content": [{"type": "text", "text": "No milestones found."}],
                        "isError": False,
                    }

                response_text = f"Found {len(milestones)} milestone(s):\n\n"
                for milestone in milestones:
                    state = "OPEN" if milestone.state == "open" else "CLOSED"
                    response_text += (
                        f"#{milestone.number} [{state}] {milestone.title}\n"
                    )

                    # Progress
                    total = milestone.open_issues + milestone.closed_issues
                    if total > 0:
                        percent = int((milestone.closed_issues / total) * 100)
                        response_text += f"   Progress: {milestone.closed_issues}/{total} ({percent}%)\n"

                    # Due date
                    if milestone.due_on:
                        due_date = milestone.due_on.strftime("%Y-%m-%d")
                        response_text += f"   Due: {due_date}\n"

                    # Description (first line only)
                    if milestone.description:
                        first_line = milestone.description.split("\n")[0][:60]
                        response_text += f"   {first_line}\n"

                    response_text += f"   URL: {milestone.html_url}\n\n"

                return {
                    "content": [{"type": "text", "text": response_text}],
                    "isError": False,
                }

            elif name == "create_milestone":
                # Parse due_on if provided
                due_on = None
                if arguments.get("due_on"):
                    try:
                        due_on = datetime.fromisoformat(arguments["due_on"])
                    except ValueError:
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": "❌ Invalid due_on format. Use YYYY-MM-DD",
                                }
                            ],
                            "isError": True,
                        }

                # Create milestone
                milestone = repo.create_milestone(
                    title=arguments["title"],
                    state=arguments.get("state", "open"),
                    description=arguments.get("description", ""),
                    due_on=due_on,
                )

                response_text = f"✅ Milestone created: #{milestone.number}\n"
                response_text += f"   Title: {milestone.title}\n"
                response_text += f"   State: {milestone.state}\n"
                if milestone.due_on:
                    response_text += (
                        f"   Due: {milestone.due_on.strftime('%Y-%m-%d')}\n"
                    )
                response_text += f"   URL: {milestone.html_url}"

                return {
                    "content": [{"type": "text", "text": response_text}],
                    "isError": False,
                }

            elif name == "update_milestone":
                milestone = repo.get_milestone(arguments["milestone_number"])

                # Build update parameters
                update_params = {}
                if "title" in arguments:
                    update_params["title"] = arguments["title"]
                if "description" in arguments:
                    update_params["description"] = arguments["description"]
                if "state" in arguments:
                    update_params["state"] = arguments["state"]
                if "due_on" in arguments:
                    try:
                        update_params["due_on"] = datetime.fromisoformat(
                            arguments["due_on"]
                        )
                    except ValueError:
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": "❌ Invalid due_on format. Use YYYY-MM-DD",
                                }
                            ],
                            "isError": True,
                        }

                # Update milestone
                milestone.edit(**update_params)

                response_text = f"✅ Milestone #{milestone.number} updated\n"
                response_text += f"   Title: {milestone.title}\n"
                response_text += f"   State: {milestone.state}\n"
                if milestone.due_on:
                    response_text += (
                        f"   Due: {milestone.due_on.strftime('%Y-%m-%d')}\n"
                    )
                response_text += f"   URL: {milestone.html_url}"

                return {
                    "content": [{"type": "text", "text": response_text}],
                    "isError": False,
                }

            elif name == "set_issue_milestone":
                issue_numbers = arguments["issue_numbers"]
                milestone_number = arguments.get("milestone_number")

                # Get milestone object or None
                milestone = None
                if milestone_number is not None:
                    try:
                        milestone = repo.get_milestone(milestone_number)
                    except Exception as e:
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"❌ Milestone #{milestone_number} not found: {e}",
                                }
                            ],
                            "isError": True,
                        }

                # Update issues
                results = []
                errors = []

                for issue_num in issue_numbers:
                    try:
                        issue = repo.get_issue(issue_num)
                        issue.edit(milestone=milestone)

                        if milestone:
                            results.append(
                                f"✅ #{issue_num}: Set milestone to '{milestone.title}'"
                            )
                        else:
                            results.append(f"✅ #{issue_num}: Removed milestone")
                    except Exception as e:
                        errors.append(f"❌ #{issue_num}: {str(e)}")

                # Format response
                response_text = "📦 Milestone assignment completed\n\n"
                response_text += f"✅ Successful: {len(results)}/{len(issue_numbers)}\n"
                if errors:
                    response_text += f"❌ Failed: {len(errors)}/{len(issue_numbers)}\n"
                response_text += "\n" + "\n".join(results)
                if errors:
                    response_text += "\n\nErrors:\n" + "\n".join(errors)

                return {
                    "content": [{"type": "text", "text": response_text}],
                    "isError": len(errors) > 0,
                }

            else:
                return {
                    "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
                    "isError": True,
                }

        except GithubException as e:
            return {
                "content": [{"type": "text", "text": self.format_github_error(e)}],
                "isError": True,
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"❌ Error: {e}"}],
                "isError": True,
            }

    async def handle_request(self, request: dict) -> Optional[dict]:
        """Handle MCP protocol request."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        # JSON-RPC: if id is None, this is a notification and we shouldn't respond
        if request_id is None:
            # Still process notifications, but don't return response
            if method == "initialize":
                await self.initialize()  # Process but don't respond
            return None

        if method == "initialize":
            result = await self.initialize()
            if isinstance(result, dict) and "error" in result:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": result["error"],
                }
            return {"jsonrpc": "2.0", "id": request_id, "result": result}
        elif method == "tools/list":
            result = self.list_tools()
        elif method == "tools/call":
            result = await self.call_tool(
                params.get("name"), params.get("arguments", {})
            )
        elif method == "resources/list":
            result = {"resources": []}
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}",
                },
            }

        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    async def run(self) -> None:
        """Run the MCP server (stdio protocol)."""
        init_line = await asyncio.to_thread(sys.stdin.readline)
        if not init_line:
            return

        try:
            init_request = json.loads(init_line.strip())
            init_response = await self.handle_request(init_request)
            if init_response is not None:
                print(json.dumps(init_response), flush=True)
        except json.JSONDecodeError as e:
            # For parse errors, we can't determine the request ID
            # Return error response without id field (allowed for parse errors per JSON-RPC 2.0)
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": f"Parse error: {e}"},
            }
            print(json.dumps(error_response), flush=True)
            return

        while True:
            request: Optional[Any] = None
            try:
                line = await asyncio.to_thread(sys.stdin.readline)
                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                request = json.loads(line)
                if request is not None:
                    response = await self.handle_request(request)
                    if response is not None:
                        print(json.dumps(response), flush=True)
            except json.JSONDecodeError:
                continue
            except Exception as e:
                request_id = request.get("id") if request is not None else None
                # Only send error response if request has an id (not a notification)
                if request_id is not None:
                    print(
                        json.dumps(
                            {
                                "jsonrpc": "2.0",
                                "id": request_id,
                                "error": {
                                    "code": -32603,
                                    "message": f"Internal error: {e}",
                                },
                            }
                        ),
                        flush=True,
                    )


def main() -> None:
    """Main entry point."""
    server = MCPServer()
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
