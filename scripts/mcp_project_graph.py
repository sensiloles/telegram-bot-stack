#!/usr/bin/env python3
"""
MCP Server for Project Graph Navigation.

Exposes .project-graph/ system through MCP protocol for AI agents.
This allows agents to efficiently navigate large codebases using
the hierarchical graph system.

Resources:
    graph://router              - Main router (783 lines)
    graph://bot_framework       - Bot framework graph
    graph://infrastructure      - Infrastructure graph
    graph://testing             - Testing graph
    graph://examples            - Examples graph
    graph://docs                - Documentation graph
    graph://configuration       - Configuration graph
    graph://archive             - Archive graph
    graph://project_meta        - Project meta graph

    graph://bot_framework/core      - Core sub-graph
    graph://bot_framework/storage   - Storage sub-graph
    graph://bot_framework/utilities - Utilities sub-graph

    graph://recommend?task=<description>  - Get recommendation

Tools:
    analyze_impact      - Analyze impact of changing a file
    find_dependencies   - Find dependencies of a node
    find_dependents     - Find dependents of a node
    recommend_graph     - Recommend graph for task

Usage:
    # In Cursor AI config:
    {
      "mcpServers": {
        "project-graph": {
          "command": "python3",
          "args": ["/path/to/scripts/mcp_project_graph.py"]
        }
      }
    }
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from mcp import types

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".project-graph"))

from utils.graph_utils import (
    find_dependencies,
    find_dependents,
    find_node_by_path,
    get_impact_analysis,
    get_recommended_graph,
    list_sub_graphs,
    load_full_hierarchical_graph,
    load_graph_by_type,
    load_router,
    load_sub_graph,
)


def get_project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).parent.parent


class ProjectGraphMCPServer:
    """MCP Server for project graph navigation."""

    def __init__(self):
        """Initialize server."""
        self.project_root = get_project_root()
        self.graph_root = self.project_root / ".project-graph"
        self.router = None  # Lazy load

    def _ensure_router(self):
        """Ensure router is loaded."""
        if self.router is None:
            self.router = load_router()

    def _get_agent_context(self) -> str:
        """Get minimal agent context for quick orientation.

        Returns:
            JSON string with essential project info
        """
        import subprocess

        # Get current branch
        try:
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )
            current_branch = branch_result.stdout.strip()
        except Exception:
            current_branch = "unknown"

        # Get project version from pyproject.toml
        try:
            pyproject_path = self.project_root / "pyproject.toml"
            if pyproject_path.exists():
                import re

                content = pyproject_path.read_text()
                version_match = re.search(r'version\s*=\s*"([^"]+)"', content)
                version = version_match.group(1) if version_match else "unknown"
            else:
                version = "unknown"
        except Exception:
            version = "unknown"

        # Build context
        context = {
            "current_state": {
                "version": version,
                "branch": current_branch,
                "phase": "Phase 2 - PyPI Publication"
                if "main" in current_branch
                else "Development",
            },
            "quick_commands": {
                "list_issues": "mcp_github-workflow_list_issues()",
                "get_issue": "mcp_github-workflow_get_issue(issue_number=N)",
                "create_pr": "mcp_github-workflow_create_pr(title='...', closes_issue=N)",
                "merge_pr": "mcp_github-workflow_merge_pr(pr_number=N, delete_branch=true)",
                "test": "python3 -m pytest --cov=telegram_bot_stack",
            },
            "critical_rules": [
                "Use Tool Priority: MCP > CLI Scripts > Manual Git",
                "NEVER push to main - use feature branches",
                "Test coverage >=80% for telegram_bot_stack/",
                "Conventional commits: type(scope): description",
                "Update docs BEFORE committing code",
            ],
            "available_graphs": [
                {"id": "router", "description": "Navigation router (783 lines)"},
                {"id": "bot_framework", "description": "Core framework code"},
                {"id": "infrastructure", "description": "CI/CD automation (639 lines)"},
                {"id": "testing", "description": "Test structure (539 lines)"},
                {"id": "examples", "description": "Example bots (471 lines)"},
                {"id": "docs", "description": "Documentation files"},
                {"id": "configuration", "description": "Build configs"},
                {
                    "id": "project_meta",
                    "description": "Architecture overview (493 lines)",
                },
            ],
            "workflow_summary": {
                "step_1": "Check branch (not main) & open issues",
                "step_2": "Load relevant graph: fetch_mcp_resource('project-graph', 'graph://...')",
                "step_3": "Implement changes + tests (>=80% coverage)",
                "step_4": "Commit with conventional format",
                "step_5": "Create PR: mcp_github-workflow_create_pr(...)",
                "step_6": "Merge: mcp_github-workflow_merge_pr(...)",
            },
            "reference_docs": {
                "full_rules": ".cursorrules",
                "project_status": ".github/PROJECT_STATUS.md",
                "automation_guide": ".github/workflows/scripts/README.md",
                "mcp_setup": "docs/mcp-github-setup.md",
            },
        }

        return json.dumps(context, indent=2)

    def list_resources(self) -> List[types.Resource]:
        """List all available graph resources.

        Returns:
            List of resource descriptors
        """
        self._ensure_router()

        resources = [
            types.Resource(
                uri="graph://router",
                name="Graph Router",
                description="Main navigation router for all graphs (783 lines)",
                mimeType="application/json",
            )
        ]

        # Add main graphs
        for _graph_key, graph_info in self.router["graphs"].items():
            graph_id = graph_info["id"]
            resources.append(
                types.Resource(
                    uri=f"graph://{graph_id}",
                    name=graph_info["name"],
                    description=graph_info["description"],
                    mimeType="application/json",
                )
            )

            # Add sub-graphs if hierarchical
            if graph_info.get("has_sub_graphs"):
                for sub_name, sub_info in graph_info["sub_graphs"].items():
                    resources.append(
                        types.Resource(
                            uri=f"graph://{graph_id}/{sub_name}",
                            name=f"{graph_info['name']} - {sub_info['name']}",
                            description=sub_info["description"],
                            mimeType="application/json",
                        )
                    )

        # Add special resources
        resources.append(
            types.Resource(
                uri="graph://recommend",
                name="Graph Recommendation",
                description="Get graph recommendation for a task (use ?task=description)",
                mimeType="text/plain",
            )
        )

        resources.append(
            types.Resource(
                uri="graph://agent_context",
                name="Agent Quick Context",
                description="Minimal context for agent orientation (~100 lines)",
                mimeType="application/json",
            )
        )

        return resources

    def read_resource(self, uri: str) -> str:
        """Read a specific graph resource.

        Args:
            uri: Resource URI (e.g., 'graph://router', 'graph://bot_framework')

        Returns:
            Resource content as string

        Raises:
            ValueError: If URI is invalid
        """
        self._ensure_router()

        # Convert URI to string (in case it's AnyUrl from pydantic)
        uri_str = str(uri)

        # Parse URI
        if not uri_str.startswith("graph://"):
            raise ValueError(f"Invalid URI scheme: {uri_str}")

        path = uri_str[8:]  # Remove 'graph://'

        # Handle router
        if path == "router":
            return json.dumps(self.router, indent=2)

        # Handle agent context
        if path == "agent_context":
            return self._get_agent_context()

        # Handle recommendation requests
        if path.startswith("recommend"):
            # Parse query parameter
            if "?task=" in path:
                task = path.split("?task=", 1)[1]
                recommendation = get_recommended_graph(self.router, task)
                return json.dumps(
                    {
                        "task": task,
                        "recommended_graph": recommendation,
                        "next_step": f"Load with: graph://{recommendation}",
                    },
                    indent=2,
                )
            else:
                return json.dumps(
                    {
                        "error": "Missing task parameter. Use: graph://recommend?task=your task description"
                    },
                    indent=2,
                )

        # Handle sub-graphs (e.g., 'bot_framework/storage')
        if "/" in path:
            graph_type, sub_graph_name = path.split("/", 1)
            graph = load_sub_graph(graph_type, sub_graph_name)
            return json.dumps(graph, indent=2)

        # Handle main graphs
        graph = load_graph_by_type(path)
        return json.dumps(graph, indent=2)

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Call a tool/function.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result as JSON string
        """
        if name == "recommend_graph":
            task = arguments.get("task", "")
            self._ensure_router()
            recommendation = get_recommended_graph(self.router, task)
            return json.dumps({"recommended_graph": recommendation})

        elif name == "analyze_impact":
            file_path = arguments.get("file_path", "")
            graph_type = arguments.get("graph_type", "bot_framework")

            # Load full hierarchical graph for bot_framework
            if graph_type == "bot_framework":
                graph = load_full_hierarchical_graph(graph_type)
            else:
                graph = load_graph_by_type(graph_type)

            # Convert file_path to node_id
            node = find_node_by_path(graph, file_path)
            if node:
                node_id = node["id"]
                impact = get_impact_analysis(graph, node_id)
            else:
                impact = {
                    "error": f"Node not found for path: {file_path}",
                    "direct_dependents": [],
                    "transitive_dependents": [],
                    "total_impact": 0,
                    "impact_level": "unknown",
                }
            return json.dumps(impact, indent=2)

        elif name == "find_dependencies":
            node_id = arguments.get("node_id", "")
            graph_type = arguments.get("graph_type", "bot_framework")

            # Load full hierarchical graph for bot_framework
            if graph_type == "bot_framework":
                graph = load_full_hierarchical_graph(graph_type)
            else:
                graph = load_graph_by_type(graph_type)

            deps = find_dependencies(graph, node_id)
            return json.dumps({"dependencies": deps})

        elif name == "find_dependents":
            node_id = arguments.get("node_id", "")
            graph_type = arguments.get("graph_type", "bot_framework")

            # Load full hierarchical graph for bot_framework
            if graph_type == "bot_framework":
                graph = load_full_hierarchical_graph(graph_type)
            else:
                graph = load_graph_by_type(graph_type)

            dependents = find_dependents(graph, node_id)
            return json.dumps({"dependents": dependents})

        elif name == "list_sub_graphs":
            graph_type = arguments.get("graph_type", "bot_framework")
            self._ensure_router()

            sub_graphs_dict = list_sub_graphs(graph_type)
            # Convert dict to list format expected by client
            sub_graphs_list = [
                {"name": name, "lines": info.get("lines", "N/A"), **info}
                for name, info in sub_graphs_dict.items()
            ]
            return json.dumps({"sub_graphs": sub_graphs_list})

        else:
            return json.dumps({"error": f"Unknown tool: {name}"})

    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools.

        Returns:
            List of tool descriptors
        """
        return [
            {
                "name": "recommend_graph",
                "description": "Recommend which graph to load for a given task",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": "Description of the task you want to perform",
                        }
                    },
                    "required": ["task"],
                },
            },
            {
                "name": "analyze_impact",
                "description": "Analyze impact of modifying a file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to file to analyze",
                        },
                        "graph_type": {
                            "type": "string",
                            "description": "Graph type (default: bot_framework)",
                            "default": "bot_framework",
                        },
                    },
                    "required": ["file_path"],
                },
            },
            {
                "name": "find_dependencies",
                "description": "Find dependencies of a node",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "node_id": {
                            "type": "string",
                            "description": "Node ID to find dependencies for",
                        },
                        "graph_type": {
                            "type": "string",
                            "description": "Graph type (default: bot_framework)",
                            "default": "bot_framework",
                        },
                    },
                    "required": ["node_id"],
                },
            },
            {
                "name": "find_dependents",
                "description": "Find dependents of a node (who uses this node)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "node_id": {
                            "type": "string",
                            "description": "Node ID to find dependents for",
                        },
                        "graph_type": {
                            "type": "string",
                            "description": "Graph type (default: bot_framework)",
                            "default": "bot_framework",
                        },
                    },
                    "required": ["node_id"],
                },
            },
            {
                "name": "list_sub_graphs",
                "description": "List available sub-graphs for hierarchical graphs",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "graph_type": {
                            "type": "string",
                            "description": "Graph type (e.g., bot_framework)",
                        }
                    },
                    "required": ["graph_type"],
                },
            },
        ]


def main():
    """Run MCP server."""
    import asyncio

    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
    except ImportError:
        print(
            "Error: MCP SDK not installed. Install with: pip install mcp",
            file=sys.stderr,
        )
        sys.exit(1)

    server = ProjectGraphMCPServer()
    app = Server("project-graph")

    @app.list_resources()
    async def handle_list_resources():
        return server.list_resources()

    @app.read_resource()
    async def handle_read_resource(uri: str):
        content = server.read_resource(uri)
        return content

    @app.list_tools()
    async def handle_list_tools():
        return server.list_tools()

    @app.call_tool()
    async def handle_call_tool(name: str, arguments: Dict[str, Any]):
        result = server.call_tool(name, arguments)
        return [{"type": "text", "text": result}]

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream, write_stream, app.create_initialization_options()
            )

    asyncio.run(run())


if __name__ == "__main__":
    main()
