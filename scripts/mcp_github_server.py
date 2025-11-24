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
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

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

from github_helper import (  # type: ignore[import-untyped]
    format_issue_detail,
    format_issue_list,
    get_repo,
)

try:
    from github import GithubException
except ImportError:

    class GithubException(Exception):
        pass


class MCPServer:
    """MCP Server implementation for GitHub issues and pull requests."""

    def __init__(self):
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
                        result = subprocess.run(
                            ["git", "branch", "--show-current"],
                            capture_output=True,
                            text=True,
                            check=True,
                        )
                        head = result.stdout.strip()
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

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"✅ Pull Request created\n"
                            f"   Number: #{pr.number}\n"
                            f"   Title: {pr.title}\n"
                            f"   From: {head} → {arguments.get('base', 'main')}\n"
                            f"   URL: {pr.html_url}",
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
                        result = subprocess.run(
                            ["git", "branch", "--show-current"],
                            capture_output=True,
                            text=True,
                            check=True,
                        )
                        branch = result.stdout.strip()
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

                for check in check_runs:
                    if check.conclusion == "success":
                        icon = "✅"
                    elif check.conclusion == "failure":
                        icon = "❌"
                    else:
                        icon = "⏳"
                    response_text += (
                        f"{icon} {check.name}: {check.conclusion or 'running'}\n"
                    )

                return {
                    "content": [{"type": "text", "text": response_text}],
                    "isError": failing > 0,
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

    async def run(self):
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
            try:
                line = await asyncio.to_thread(sys.stdin.readline)
                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                request = json.loads(line)
                response = await self.handle_request(request)
                if response is not None:
                    print(json.dumps(response), flush=True)
            except json.JSONDecodeError:
                continue
            except Exception as e:
                request_id = request.get("id") if "request" in locals() else None
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


def main():
    """Main entry point."""
    server = MCPServer()
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
