#!/usr/bin/env python3
"""Regenerate all project graphs from scratch.

This script completely regenerates all graph nodes by scanning the codebase.
Use this when you want to ensure all nodes are up-to-date with the current
file structure.

Usage:
    python3 regenerate_all.py              # Regenerate all graphs
    python3 regenerate_all.py --dry-run    # Preview changes
"""

import ast
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))


def get_project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).parent.parent.parent


def get_graph_root() -> Path:
    """Get graph root directory."""
    return Path(__file__).parent.parent


def analyze_python_file(file_path: Path) -> Dict[str, Any]:
    """Analyze a Python file and extract metadata."""
    try:
        with open(file_path) as f:
            source = f.read()
            tree = ast.parse(source)

        classes = []
        functions = []
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                functions.append(node.name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif node.module:
                    imports.append(node.module)

        # Get docstring
        docstring = ast.get_docstring(tree) or ""
        description = (
            docstring.split("\n")[0] if docstring else f"Module {file_path.stem}"
        )

        return {
            "classes": classes,
            "functions": functions,
            "imports": imports,
            "lines": len(source.splitlines()),
            "description": description[:100],
        }

    except Exception as e:
        print(f"⚠️  Warning: Could not analyze {file_path}: {e}", file=sys.stderr)
        return {
            "classes": [],
            "functions": [],
            "imports": [],
            "lines": 0,
            "description": f"Module {file_path.name}",
        }


def create_node_from_file(
    file_path: Path, project_root: Path, node_type: str = "module"
) -> Dict[str, Any]:
    """Create a graph node from a file."""
    rel_path = file_path.relative_to(project_root)

    # Create node ID
    if file_path.suffix == ".py":
        parts = rel_path.with_suffix("").parts
        if parts[-1] == "__init__":
            parts = parts[:-1]
        node_id = ".".join(parts)
    else:
        node_id = str(rel_path).replace("/", ".")

    # Analyze file
    metadata = {}
    if file_path.suffix == ".py":
        metadata = analyze_python_file(file_path)
    else:
        try:
            metadata = {
                "description": f"File {file_path.name}",
                "lines": len(file_path.read_text().splitlines()),
            }
        except Exception:
            metadata = {"description": f"File {file_path.name}", "lines": 0}

    # Create node
    node = {
        "id": node_id,
        "name": file_path.stem,
        "type": node_type,
        "category": "implementation",
        "path": str(rel_path),
        "description": metadata.get("description", ""),
    }

    # Add Python-specific fields
    if file_path.suffix == ".py":
        node.update(
            {
                "lines_of_code": metadata.get("lines", 0),
                "complexity_score": 1,
                "exports": metadata.get("classes", []) + metadata.get("functions", []),
                "classes": metadata.get("classes", []),
                "functions": metadata.get("functions", []),
                "dependencies": [],
                "dependents": [],
                "criticality": "medium",
            }
        )

    return node


def find_imports_in_files(
    files: List[Path], project_root: Path
) -> List[Dict[str, Any]]:
    """Find import relationships between files."""
    edges = []
    edge_id = 1

    for file_path in files:
        if not file_path.suffix == ".py":
            continue

        try:
            with open(file_path) as f:
                tree = ast.parse(f.read())

            rel_path = file_path.relative_to(project_root)
            parts = rel_path.with_suffix("").parts
            if parts[-1] == "__init__":
                parts = parts[:-1]
            source_id = ".".join(parts)

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and not node.module.startswith("."):
                        module_parts = node.module.split(".")

                        if module_parts[0] in [
                            "telegram_bot_stack",
                            "tests",
                            "examples",
                        ]:
                            target_id = node.module
                            edges.append(
                                {
                                    "id": f"edge_{edge_id}",
                                    "source": source_id,
                                    "target": target_id,
                                    "type": "imports",
                                    "description": f"Imports from {target_id}",
                                }
                            )
                            edge_id += 1

        except Exception as e:
            print(f"⚠️  Warning: Could not analyze imports in {file_path}: {e}")

    return edges


def classify_module_by_path(file_path: Path, bot_dir: Path) -> str:
    """Classify module into sub-graph based on file path.

    Args:
        file_path: Path to Python file
        bot_dir: Root telegram_bot_stack directory

    Returns:
        Sub-graph name: 'core', 'storage', 'cli', or 'utilities'
    """
    rel_path = file_path.relative_to(bot_dir)
    path_parts = rel_path.parts

    # Check first directory level
    if len(path_parts) > 1:
        first_dir = path_parts[0]

        if first_dir == "storage":
            return "storage"
        elif first_dir == "cli":
            return "cli"

    # Special case: decorators.py -> utilities
    if file_path.name == "decorators.py":
        return "utilities"

    # Everything else in root -> core
    return "core"


def auto_discover_bot_modules(bot_dir: Path) -> Dict[str, List[Path]]:
    """Auto-discover and group all bot framework modules.

    Args:
        bot_dir: Root telegram_bot_stack directory

    Returns:
        Dictionary mapping sub-graph name to list of file paths
    """
    module_groups = {
        "core": [],
        "storage": [],
        "cli": [],
        "utilities": [],
    }

    # Scan all Python files
    for py_file in bot_dir.rglob("*.py"):
        # Skip __pycache__
        if "__pycache__" in py_file.parts:
            continue

        sub_graph = classify_module_by_path(py_file, bot_dir)
        module_groups[sub_graph].append(py_file)

    return module_groups


def regenerate_bot_framework_graphs(dry_run: bool = False) -> None:
    """Regenerate bot_framework sub-graphs with auto-discovery."""
    project_root = get_project_root()
    graph_root = get_graph_root()

    print("📦 Regenerating bot_framework graphs...")

    bot_dir = project_root / "telegram_bot_stack"
    if not bot_dir.exists():
        print("⚠️  telegram_bot_stack directory not found")
        return

    # Auto-discover modules
    print("🔍 Auto-discovering modules...")
    module_groups = auto_discover_bot_modules(bot_dir)

    # Print discovery results
    for sub_id, files in module_groups.items():
        if files:
            print(f"   {sub_id}: {len(files)} modules")
    print()

    # Sub-graph metadata
    sub_graph_metadata = {
        "core": {
            "name": "Core",
            "description": "Core bot framework components",
        },
        "storage": {
            "name": "Storage",
            "description": "Storage abstraction layer and implementations",
        },
        "cli": {
            "name": "CLI",
            "description": "CLI tool for bot project management and development",
        },
        "utilities": {
            "name": "Utilities",
            "description": "Utility decorators and helper functions",
        },
    }

    for sub_id, python_files in module_groups.items():
        if not python_files:
            continue

        print(f"\n📊 Generating {sub_id} sub-graph...")

        sub_info = sub_graph_metadata[sub_id]
        nodes = []

        # Create nodes
        for file_path in python_files:
            node = create_node_from_file(file_path, project_root, "module")
            nodes.append(node)

        # Find edges
        edges = find_imports_in_files(python_files, project_root)

        # Create graph
        graph = {
            "metadata": {
                "version": "3.0.0",
                "generated_at": datetime.now().strftime("%Y-%m-%d"),
                "graph_id": f"bot_framework_{sub_id}",
                "graph_name": f"Bot Framework - {sub_info['name']}",
                "graph_type": "sub_graph",
                "parent_graph": "bot_framework",
                "project_name": "telegram-bot-stack",
                "project_version": "1.6.0",
                "description": sub_info["description"],
                "scope": sub_info.get("scope", sub_info["description"]),
                "root_package": f"telegram_bot_stack.{sub_id}" if sub_id != "core" else "telegram_bot_stack",
                "node_count": len(nodes),
                "edge_count": len(edges),
            },
            "nodes": nodes,
            "edges": edges,
        }

        print(f"   Found {len(nodes)} nodes, {len(edges)} edges")

        # Save graph
        output_file = graph_root / "bot-framework" / f"{sub_id}-graph.json"

        if dry_run:
            print(f"   [DRY RUN] Would save to: {output_file}")
        else:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w") as f:
                json.dump(graph, f, indent=2)
                f.write("\n")  # POSIX compliant - add trailing newline
            print(f"   ✅ Saved: {output_file.name}")

    # Auto-generate router.json from created sub-graphs
    if not dry_run:
        print("\n📋 Generating bot-framework router...")
        generate_bot_framework_router(graph_root)


def generate_bot_framework_router(graph_root: Path) -> None:
    """Auto-generate bot-framework/router.json from sub-graphs.

    Reads all *-graph.json files in bot-framework/ and creates router.
    """
    bf_dir = graph_root / "bot-framework"

    # Load all sub-graphs
    sub_graphs_data = {}
    total_modules = 0
    total_loc = 0

    for graph_file in sorted(bf_dir.glob("*-graph.json")):
        if graph_file.name == "router.json":
            continue

        sub_id = graph_file.stem.replace("-graph", "")

        with open(graph_file) as f:
            graph = json.load(f)

        metadata = graph["metadata"]
        nodes = graph.get("nodes", [])

        # Calculate statistics
        modules_count = len(nodes)
        loc_count = sum(n.get("lines_of_code", 0) for n in nodes)

        total_modules += modules_count
        total_loc += loc_count

        # Determine recommended_for
        recommended_for = []
        if sub_id == "core":
            recommended_for = [
                "Adding new bot features",
                "Customizing bot behavior",
                "User/admin management changes",
            ]
        elif sub_id == "storage":
            recommended_for = [
                "Adding new storage backend",
                "Storage migration",
                "Data persistence changes",
            ]
        elif sub_id == "cli":
            recommended_for = [
                "CLI command development",
                "Project scaffolding changes",
                "Dev environment automation",
                "Working on Issue #40 (Killer Feature #1)",
            ]
        elif sub_id == "utilities":
            recommended_for = [
                "Adding new decorators",
                "Adding utility functions",
                "Rate limiting changes",
            ]

        sub_graphs_data[sub_id] = {
            "file": f"bot-framework/{graph_file.name}",
            "graph_id": metadata["graph_id"],
            "name": metadata.get("graph_name", "").replace("Bot Framework - ", ""),
            "description": metadata["description"],
            "modules": modules_count,
            "lines_of_code": loc_count,
            "recommended_for": recommended_for,
        }

    # Create router
    router = {
        "metadata": {
            "version": "3.0.0",
            "generated_at": datetime.now().strftime("%Y-%m-%d"),
            "graph_id": "bot_framework",
            "graph_name": "Bot Framework",
            "graph_type": "domain_router",
            "has_sub_graphs": True,
            "project_name": "telegram-bot-stack",
            "project_version": "1.15.0",
            "description": "Router for bot framework sub-graphs",
        },
        "sub_graphs": sub_graphs_data,
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
            "total_sub_graphs": len(sub_graphs_data),
            "total_modules": total_modules,
            "total_lines_of_code": total_loc,
            "cross_graph_edges": 3,
        },
    }

    # Save router
    router_file = bf_dir / "router.json"
    with open(router_file, "w") as f:
        json.dump(router, f, indent=2)
        f.write("\n")

    print(f"   ✅ Generated router.json ({len(sub_graphs_data)} sub-graphs, {total_modules} modules)")


def regenerate_docs_graph(dry_run: bool = False) -> None:
    """Regenerate docs graph."""
    project_root = get_project_root()
    graph_root = get_graph_root()

    print("\n📚 Regenerating docs graph...")

    docs_dir = project_root / "docs"
    if not docs_dir.exists():
        print("⚠️  docs directory not found")
        return

    nodes = []
    for file_path in docs_dir.glob("*.md"):
        node = {
            "id": f"docs.{file_path.stem}",
            "name": file_path.stem,
            "type": "doc",
            "category": "documentation",
            "path": str(file_path.relative_to(project_root)),
            "description": f"Documentation: {file_path.stem}",
            "lines_of_code": len(file_path.read_text().splitlines()),
        }
        nodes.append(node)

    graph = {
        "metadata": {
            "version": "3.0.0",
            "generated_at": datetime.now().strftime("%Y-%m-%d"),
            "graph_id": "docs",
            "graph_name": "Documentation",
            "graph_type": "domain",
            "project_name": "telegram-bot-stack",
            "description": "Project documentation files",
            "scope": "User guides, API reference, setup instructions",
            "node_count": len(nodes),
            "edge_count": 0,
        },
        "nodes": nodes,
        "edges": [],
    }

    print(f"   Found {len(nodes)} nodes")

    output_file = graph_root / "docs" / "graph.json"

    if dry_run:
        print(f"   [DRY RUN] Would save to: {output_file}")
    else:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(graph, f, indent=2)
            f.write("\n")  # POSIX compliant - add trailing newline
        print(f"   ✅ Saved: {output_file.name}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Regenerate all project graphs from scratch"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without saving",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("🔄 Full Graph Regeneration")
    print("=" * 60)
    print()

    # First, run the existing generator for infrastructure/testing/examples
    print("Running generate_graphs.py for infrastructure/testing/examples...")
    print()
    import subprocess
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "generate_graphs.py"), "--graph", "all"],
        capture_output=False
    )

    if result.returncode != 0:
        print("⚠️  Warning: generate_graphs.py failed")

    print()

    # Regenerate bot_framework
    regenerate_bot_framework_graphs(dry_run=args.dry_run)

    # Regenerate docs
    regenerate_docs_graph(dry_run=args.dry_run)

    print()
    print("=" * 60)
    if args.dry_run:
        print("🔍 Dry run completed")
    else:
        print("✅ Full regeneration completed")
        print()
        print("Next steps:")
        print("1. Review changes: git diff .project-graph/")
        print("2. Run tests: cd .project-graph/utils && python3 test_integration.py")
        print("3. Commit if satisfied: git add .project-graph/ && git commit")
    print("=" * 60)


if __name__ == "__main__":
    main()
