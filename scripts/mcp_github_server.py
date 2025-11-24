#!/usr/bin/env python3
"""MCP Server for GitHub Issues.

Provides GitHub issue management via Model Context Protocol (MCP).
MCP Protocol: https://modelcontextprotocol.io/
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

# Setup paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / ".github" / "workflows" / "scripts"))


def log_debug(message: str) -> None:
    """Log debug message to stderr (won't interfere with JSON-RPC protocol)."""
    print(f"[MCP DEBUG] {message}", file=sys.stderr, flush=True)


def load_token_from_env() -> None:
    """Load GITHUB_TOKEN from .env file if not in environment or is placeholder."""
    env_token = os.getenv("GITHUB_TOKEN")
    is_placeholder = env_token and (
        (env_token.startswith("${") and env_token.endswith("}")) or len(env_token) < 20
    )

    if is_placeholder:
        log_debug("Token is placeholder, loading from .env")
        env_token = None

    if not env_token:
        env_file = project_root / ".env"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GITHUB_TOKEN="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if token and not (
                            token.startswith("${") and token.endswith("}")
                        ):
                            os.environ["GITHUB_TOKEN"] = token
                            log_debug("Token loaded from .env")
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


# Load token before importing github_helper
load_token_from_env()

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
    """MCP Server implementation for GitHub issues."""

    def __init__(self):
        self.repo: Optional[Any] = None
        self.repo_name: Optional[str] = None

    async def initialize(self) -> dict:
        """Initialize the server and detect repository."""
        try:
            self.repo_name = os.getenv("GITHUB_REPO") or detect_repo_from_git()

            if self.repo_name:
                log_debug(f"Repository: {self.repo_name}")
                self.repo = get_repo(self.repo_name)
                log_debug(f"✅ Connected to {self.repo.full_name}")

            return {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}, "resources": {}},
                "serverInfo": {"name": "github-issues-mcp", "version": "1.0.0"},
            }
        except Exception as e:
            log_debug(f"❌ Initialization failed: {e}")
            return {"error": {"code": -32000, "message": f"Failed to initialize: {e}"}}

    def list_tools(self) -> dict:
        """List available tools."""
        return {
            "tools": [
                {
                    "name": "list_issues",
                    "description": "List GitHub issues with optional filters",
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

        repo = self.repo if repo_name == self.repo_name else get_repo(repo_name)

        try:
            if name == "list_issues":
                issues = repo.get_issues(
                    state=arguments.get("state", "open"),
                    labels=arguments.get("labels") or [],
                )
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

            else:
                return {
                    "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
                    "isError": True,
                }

        except GithubException as e:
            return {
                "content": [{"type": "text", "text": f"❌ GitHub API error: {e}"}],
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
