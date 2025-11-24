#!/usr/bin/env python3
"""Split bot-framework-graph.json into hierarchical sub-graphs.

Auto-discovers modules by directory structure to avoid manual maintenance.
"""

import json
from pathlib import Path
from typing import Any, Dict, List


def load_graph(path: Path) -> Dict[str, Any]:
    """Load graph from JSON file."""
    with open(path) as f:
        return json.load(f)


def save_graph(graph: Dict[str, Any], path: Path):
    """Save graph to JSON file with pretty printing."""
    with open(path, "w") as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)
        f.write("\n")  # Add newline at end


def classify_module(module_id: str) -> str:
    """Classify module into a sub-graph based on its path.

    Args:
        module_id: Module identifier (e.g., 'telegram_bot_stack.storage.json')

    Returns:
        Sub-graph name: 'core', 'storage', 'cli', or 'utilities'
    """
    # Storage: anything in telegram_bot_stack/storage/
    if ".storage" in module_id:
        return "storage"

    # CLI: anything in telegram_bot_stack/cli/
    if ".cli" in module_id:
        return "cli"

    # Utilities: decorators module
    if module_id == "telegram_bot_stack.decorators":
        return "utilities"

    # Core: everything else in telegram_bot_stack (root level modules)
    # This includes: __init__, bot_base, user_manager, admin_manager
    return "core"


def auto_discover_modules(graph: Dict[str, Any]) -> Dict[str, List[str]]:
    """Auto-discover and classify all modules from graph.

    Args:
        graph: Full bot-framework graph

    Returns:
        Dictionary mapping sub-graph name to list of module IDs
    """
    module_groups = {
        "core": [],
        "storage": [],
        "cli": [],
        "utilities": [],
    }

    for node in graph["nodes"]:
        module_id = node["id"]
        sub_graph = classify_module(module_id)
        module_groups[sub_graph].append(module_id)

    return module_groups


def split_graph():
    """Split bot-framework-graph into sub-graphs with auto-discovery."""

    # Load original graph
    graph_path = Path(__file__).parent / "bot-framework-graph.json"
    graph = load_graph(graph_path)

    # Auto-discover module groups
    print("🔍 Auto-discovering modules...")
    module_groups = auto_discover_modules(graph)

    core_modules = module_groups["core"]
    storage_modules = module_groups["storage"]
    cli_modules = module_groups["cli"]
    utilities_modules = module_groups["utilities"]

    print(f"  Core: {len(core_modules)} modules")
    print(f"  Storage: {len(storage_modules)} modules")
    print(f"  CLI: {len(cli_modules)} modules")
    print(f"  Utilities: {len(utilities_modules)} modules")
    print()

    # Split nodes
    core_nodes = [n for n in graph["nodes"] if n["id"] in core_modules]
    storage_nodes = [n for n in graph["nodes"] if n["id"] in storage_modules]
    utilities_nodes = [n for n in graph["nodes"] if n["id"] in utilities_modules]
    cli_nodes = [n for n in graph["nodes"] if n["id"] in cli_modules]

    # Split edges
    def get_edges_for_modules(module_ids: List[str]) -> List[Dict]:
        """Get edges where both source and target are in module_ids."""
        return [
            e
            for e in graph["edges"]
            if e["source"] in module_ids and e["target"] in module_ids
        ]

    core_edges = get_edges_for_modules(core_modules)
    storage_edges = get_edges_for_modules(storage_modules)
    utilities_edges = get_edges_for_modules(utilities_modules)
    cli_edges = get_edges_for_modules(cli_modules)

    # Create core graph
    core_graph = {
        "metadata": {
            "version": "3.0.0",
            "generated_at": "2025-11-19",
            "graph_id": "bot_framework_core",
            "graph_name": "Bot Framework - Core",
            "graph_type": "sub_graph",
            "parent_graph": "bot_framework",
            "project_name": "telegram-bot-stack",
            "project_version": "1.6.0",
            "description": "Core bot framework modules (BotBase, UserManager, AdminManager)",
            "scope": "Core bot implementation and management",
            "root_package": "telegram_bot_stack",
            "node_count": len(core_nodes),
            "edge_count": len(core_edges),
        },
        "nodes": core_nodes,
        "edges": core_edges,
        "external_dependencies": {
            "description": "Dependencies to modules in other sub-graphs",
            "storage": [
                "telegram_bot_stack.storage.base",
                "telegram_bot_stack.storage",
            ],
            "utilities": ["telegram_bot_stack.decorators"],
        },
    }

    # Create storage graph
    storage_graph = {
        "metadata": {
            "version": "3.0.0",
            "generated_at": "2025-11-19",
            "graph_id": "bot_framework_storage",
            "graph_name": "Bot Framework - Storage",
            "graph_type": "sub_graph",
            "parent_graph": "bot_framework",
            "project_name": "telegram-bot-stack",
            "project_version": "1.6.0",
            "description": "Storage abstraction layer and implementations",
            "scope": "All storage backends (JSON, Memory, SQL)",
            "root_package": "telegram_bot_stack.storage",
            "node_count": len(storage_nodes),
            "edge_count": len(storage_edges),
        },
        "nodes": storage_nodes,
        "edges": storage_edges,
        "external_dependencies": {
            "description": "Dependencies to modules in other sub-graphs",
            "core": [],
            "utilities": [],
        },
    }

    # Create utilities graph
    utilities_graph = {
        "metadata": {
            "version": "3.0.0",
            "generated_at": "2025-11-24",
            "graph_id": "bot_framework_utilities",
            "graph_name": "Bot Framework - Utilities",
            "graph_type": "sub_graph",
            "parent_graph": "bot_framework",
            "project_name": "telegram-bot-stack",
            "project_version": "1.15.0",
            "description": "Utility decorators and helper functions",
            "scope": "Decorators (rate_limit) and utilities",
            "root_package": "telegram_bot_stack",
            "node_count": len(utilities_nodes),
            "edge_count": len(utilities_edges),
        },
        "nodes": utilities_nodes,
        "edges": utilities_edges,
        "external_dependencies": {
            "description": "Dependencies to modules in other sub-graphs",
            "core": [],
            "storage": [],
        },
    }

    # Create CLI graph (new in v2.0.0 - Killer Feature #1)
    cli_graph = {
        "metadata": {
            "version": "3.0.0",
            "generated_at": "2025-11-24",
            "graph_id": "bot_framework_cli",
            "graph_name": "Bot Framework - CLI",
            "graph_type": "sub_graph",
            "parent_graph": "bot_framework",
            "project_name": "telegram-bot-stack",
            "project_version": "1.15.0",
            "description": "CLI tool for bot project management and development",
            "scope": "Commands (init, new, dev, validate) and utilities (venv, git, linting, testing, IDE)",
            "root_package": "telegram_bot_stack.cli",
            "node_count": len(cli_nodes),
            "edge_count": len(cli_edges),
        },
        "nodes": cli_nodes,
        "edges": cli_edges,
        "external_dependencies": {
            "description": "Dependencies to modules in other sub-graphs",
            "core": [],
            "storage": [],
            "utilities": [],
        },
    }

    # Create domain router
    router = {
        "metadata": {
            "version": "3.0.0",
            "generated_at": "2025-11-24",
            "graph_id": "bot_framework",
            "graph_name": "Bot Framework",
            "graph_type": "domain_router",
            "has_sub_graphs": True,
            "project_name": "telegram-bot-stack",
            "project_version": "1.15.0",
            "description": "Router for bot framework sub-graphs",
        },
        "sub_graphs": {
            "core": {
                "file": "bot-framework/core-graph.json",
                "graph_id": "bot_framework_core",
                "name": "Core",
                "description": "BotBase, UserManager, AdminManager",
                "modules": len(core_nodes),
                "lines_of_code": sum(n.get("lines_of_code", 0) for n in core_nodes),
                "recommended_for": [
                    "Adding new bot features",
                    "Customizing bot behavior",
                    "User/admin management changes",
                ],
            },
            "storage": {
                "file": "bot-framework/storage-graph.json",
                "graph_id": "bot_framework_storage",
                "name": "Storage",
                "description": "Storage backends (JSON, Memory, SQL)",
                "modules": len(storage_nodes),
                "lines_of_code": sum(n.get("lines_of_code", 0) for n in storage_nodes),
                "recommended_for": [
                    "Adding new storage backend",
                    "Storage migration",
                    "Data persistence changes",
                ],
            },
            "utilities": {
                "file": "bot-framework/utilities-graph.json",
                "graph_id": "bot_framework_utilities",
                "name": "Utilities",
                "description": "Decorators and helper functions",
                "modules": len(utilities_nodes),
                "lines_of_code": sum(
                    n.get("lines_of_code", 0) for n in utilities_nodes
                ),
                "recommended_for": [
                    "Adding new decorators",
                    "Adding utility functions",
                    "Rate limiting changes",
                ],
            },
            "cli": {
                "file": "bot-framework/cli-graph.json",
                "graph_id": "bot_framework_cli",
                "name": "CLI",
                "description": "CLI tool for bot project management (init, new, dev, validate)",
                "modules": len(cli_nodes),
                "lines_of_code": sum(n.get("lines_of_code", 0) for n in cli_nodes),
                "recommended_for": [
                    "CLI command development",
                    "Project scaffolding changes",
                    "Dev environment automation",
                    "Working on Issue #40 (Killer Feature #1)",
                ],
            },
        },
        "cross_graph_edges": [
            {
                "id": "cross_edge_1",
                "source_graph": "core",
                "source_node": "telegram_bot_stack.bot_base",
                "target_graph": "storage",
                "target_node": "telegram_bot_stack.storage.base",
                "type": "uses",
                "description": "BotBase uses StorageBackend interface",
            },
            {
                "id": "cross_edge_2",
                "source_graph": "core",
                "source_node": "telegram_bot_stack.__init__",
                "target_graph": "storage",
                "target_node": "telegram_bot_stack.storage",
                "type": "imports",
                "description": "Public API imports storage factories",
            },
            {
                "id": "cross_edge_3",
                "source_graph": "core",
                "source_node": "telegram_bot_stack.__init__",
                "target_graph": "utilities",
                "target_node": "telegram_bot_stack.decorators",
                "type": "imports",
                "description": "Public API imports decorators",
            },
        ],
        "statistics": {
            "total_sub_graphs": 4,
            "total_modules": len(core_nodes)
            + len(storage_nodes)
            + len(utilities_nodes)
            + len(cli_nodes),
            "total_lines_of_code": sum(
                n.get("lines_of_code", 0) for n in graph["nodes"]
            ),
            "cross_graph_edges": 3,
            "total_nodes": len(core_nodes) + len(storage_nodes) + len(utilities_nodes) + len(cli_nodes),
            "total_edges": len(core_edges) + len(storage_edges) + len(utilities_edges) + len(cli_edges),
        },
    }

    # Save sub-graphs
    output_dir = Path(__file__).parent / "bot-framework"
    output_dir.mkdir(exist_ok=True)

    save_graph(core_graph, output_dir / "core-graph.json")
    print(
        f"✅ Created bot-framework/core-graph.json ({len(core_nodes)} nodes, {len(core_edges)} edges)"
    )

    save_graph(storage_graph, output_dir / "storage-graph.json")
    print(
        f"✅ Created bot-framework/storage-graph.json ({len(storage_nodes)} nodes, {len(storage_edges)} edges)"
    )

    save_graph(utilities_graph, output_dir / "utilities-graph.json")
    print(
        f"✅ Created bot-framework/utilities-graph.json ({len(utilities_nodes)} nodes, {len(utilities_edges)} edges)"
    )

    save_graph(cli_graph, output_dir / "cli-graph.json")
    print(
        f"✅ Created bot-framework/cli-graph.json ({len(cli_nodes)} nodes, {len(cli_edges)} edges)"
    )

    save_graph(router, output_dir / "router.json")
    print(f"✅ Created bot-framework/router.json ({router['statistics']['total_sub_graphs']} sub-graphs)")

    # Print summary
    print("\n📊 Summary:")
    print(
        f"  Core: {len(core_nodes)} modules, {sum(n.get('lines_of_code', 0) for n in core_nodes)} LOC"
    )
    print(
        f"  Storage: {len(storage_nodes)} modules, {sum(n.get('lines_of_code', 0) for n in storage_nodes)} LOC"
    )
    print(
        f"  Utilities: {len(utilities_nodes)} modules, {sum(n.get('lines_of_code', 0) for n in utilities_nodes)} LOC"
    )
    print(
        f"  CLI: {len(cli_nodes)} modules, {sum(n.get('lines_of_code', 0) for n in cli_nodes)} LOC"
    )
    print(
        f"  Total: {len(graph['nodes'])} modules, {sum(n.get('lines_of_code', 0) for n in graph['nodes'])} LOC"
    )


if __name__ == "__main__":
    split_graph()
