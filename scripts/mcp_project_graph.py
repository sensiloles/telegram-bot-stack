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

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".project-graph"))

from utils.graph_utils import (
    find_dependencies,
    find_dependents,
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

    def list_resources(self) -> List[Dict[str, str]]:
        """List all available graph resources.

        Returns:
            List of resource descriptors
        """
        self._ensure_router()

        resources = [
            {
                "uri": "graph://router",
                "name": "Graph Router",
                "description": "Main navigation router for all graphs (783 lines)",
                "mimeType": "application/json",
            }
        ]

        # Add main graphs
        for _graph_key, graph_info in self.router["graphs"].items():
            graph_id = graph_info["id"]
            resources.append(
                {
                    "uri": f"graph://{graph_id}",
                    "name": graph_info["name"],
                    "description": graph_info["description"],
                    "mimeType": "application/json",
                }
            )

            # Add sub-graphs if hierarchical
            if graph_info.get("has_sub_graphs"):
                for sub_name, sub_info in graph_info["sub_graphs"].items():
                    resources.append(
                        {
                            "uri": f"graph://{graph_id}/{sub_name}",
                            "name": f"{graph_info['name']} - {sub_info['name']}",
                            "description": sub_info["description"],
                            "mimeType": "application/json",
                        }
                    )

        # Add special resources
        resources.append(
            {
                "uri": "graph://recommend",
                "name": "Graph Recommendation",
                "description": "Get graph recommendation for a task (use ?task=description)",
                "mimeType": "text/plain",
            }
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

        # Parse URI
        if not uri.startswith("graph://"):
            raise ValueError(f"Invalid URI scheme: {uri}")

        path = uri[8:]  # Remove 'graph://'

        # Handle router
        if path == "router":
            return json.dumps(self.router, indent=2)

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

            impact = get_impact_analysis(graph, file_path)
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

            sub_graphs = list_sub_graphs(graph_type)
            return json.dumps({"sub_graphs": sub_graphs})

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
