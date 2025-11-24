#!/usr/bin/env python3
"""Generate project graphs automatically by scanning the codebase.

This script scans the project structure and generates graph JSON files
for different domains (infrastructure, testing, examples, etc.).

Usage:
    python3 generate_graphs.py              # Generate all graphs
    python3 generate_graphs.py --graph infrastructure  # Generate specific graph
    python3 generate_graphs.py --dry-run    # Preview changes
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
    """Analyze a Python file and extract metadata.

    Args:
        file_path: Path to Python file

    Returns:
        Dictionary with file metadata
    """
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
            "description": f"File {file_path.name}",
        }


def create_node_from_file(
    file_path: Path, project_root: Path, node_type: str = "module"
) -> Dict[str, Any]:
    """Create a graph node from a file.

    Args:
        file_path: Path to file
        project_root: Project root path
        node_type: Type of node (module, script, doc, config)

    Returns:
        Node dictionary
    """
    rel_path = file_path.relative_to(project_root)

    # Create node ID
    if file_path.suffix == ".py":
        # Python module: convert path to dotted notation
        parts = rel_path.with_suffix("").parts
        if parts[-1] == "__init__":
            parts = parts[:-1]
        node_id = ".".join(parts)
    else:
        # Other files: use path with dots
        node_id = str(rel_path).replace("/", ".")

    # Analyze file
    metadata = {}
    if file_path.suffix == ".py":
        metadata = analyze_python_file(file_path)
    else:
        metadata = {
            "description": f"Configuration file {file_path.name}",
            "lines": len(file_path.read_text().splitlines())
            if file_path.exists()
            else 0,
        }

    # Create node
    node = {
        "id": node_id,
        "name": file_path.stem,
        "type": node_type,
        "path": str(rel_path),
        "description": metadata.get("description", ""),
    }

    # Add Python-specific fields
    if file_path.suffix == ".py":
        node.update(
            {
                "lines_of_code": metadata.get("lines", 0),
                "exports": metadata.get("classes", []) + metadata.get("functions", []),
                "classes": metadata.get("classes", []),
                "functions": metadata.get("functions", []),
            }
        )

    return node


def find_imports_in_files(
    files: List[Path], project_root: Path
) -> List[Dict[str, Any]]:
    """Find import relationships between files.

    Args:
        files: List of Python files
        project_root: Project root path

    Returns:
        List of edges (import relationships)
    """
    edges = []
    edge_id = 1

    for file_path in files:
        if not file_path.suffix == ".py":
            continue

        try:
            with open(file_path) as f:
                tree = ast.parse(f.read())

            # Get source node ID
            rel_path = file_path.relative_to(project_root)
            parts = rel_path.with_suffix("").parts
            if parts[-1] == "__init__":
                parts = parts[:-1]
            source_id = ".".join(parts)

            # Find imports
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and not node.module.startswith("."):
                        # Check if it's internal import
                        module_parts = node.module.split(".")

                        # For telegram_bot_stack, tests, examples imports
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
            print(
                f"⚠️  Warning: Could not analyze imports in {file_path}: {e}",
                file=sys.stderr,
            )

    return edges


def generate_infrastructure_graph() -> Dict[str, Any]:
    """Generate infrastructure graph (CI/CD, scripts)."""
    project_root = get_project_root()

    print("📦 Generating infrastructure graph...")

    nodes = []

    # Scan .github directory
    github_dir = project_root / ".github"
    if github_dir.exists():
        for file_path in github_dir.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith("."):
                if file_path.suffix in [".yml", ".yaml", ".py", ".sh", ".md"]:
                    node_type = (
                        "workflow"
                        if file_path.suffix in [".yml", ".yaml"]
                        else "script"
                    )
                    nodes.append(
                        create_node_from_file(file_path, project_root, node_type)
                    )

    # Scan scripts directory
    scripts_dir = project_root / "scripts"
    if scripts_dir.exists():
        for file_path in scripts_dir.glob("*.py"):
            if not file_path.name.startswith("__"):
                nodes.append(create_node_from_file(file_path, project_root, "script"))

    # Find edges
    python_files = [
        f
        for f in (list(github_dir.rglob("*.py")) if github_dir.exists() else [])
        + list((scripts_dir.glob("*.py")) if scripts_dir.exists() else [])
    ]
    edges = find_imports_in_files(python_files, project_root)

    print(f"   Found {len(nodes)} nodes, {len(edges)} edges")

    return {
        "metadata": {
            "version": "3.0.0",
            "generated_at": datetime.now().strftime("%Y-%m-%d"),
            "graph_id": "infrastructure",
            "graph_name": "Infrastructure",
            "graph_type": "domain",
            "project_name": "telegram-bot-stack",
            "description": "CI/CD workflows, automation scripts, and tooling",
            "scope": "GitHub Actions, automation scripts, deployment",
            "node_count": len(nodes),
            "edge_count": len(edges),
        },
        "nodes": nodes,
        "edges": edges,
    }


def generate_testing_graph() -> Dict[str, Any]:
    """Generate testing graph."""
    project_root = get_project_root()

    print("🧪 Generating testing graph...")

    nodes = []

    # Scan tests directory
    tests_dir = project_root / "tests"
    if tests_dir.exists():
        for file_path in tests_dir.rglob("*.py"):
            if not file_path.name.startswith("__"):
                node_type = "test_module"
                nodes.append(create_node_from_file(file_path, project_root, node_type))

    # Find edges
    python_files = list(tests_dir.rglob("*.py")) if tests_dir.exists() else []
    edges = find_imports_in_files(python_files, project_root)

    print(f"   Found {len(nodes)} nodes, {len(edges)} edges")

    return {
        "metadata": {
            "version": "3.0.0",
            "generated_at": datetime.now().strftime("%Y-%m-%d"),
            "graph_id": "testing",
            "graph_name": "Testing Infrastructure",
            "graph_type": "domain",
            "project_name": "telegram-bot-stack",
            "description": "Test suite, fixtures, and testing utilities",
            "scope": "Unit tests, integration tests, fixtures",
            "node_count": len(nodes),
            "edge_count": len(edges),
        },
        "nodes": nodes,
        "edges": edges,
    }


def generate_examples_graph() -> Dict[str, Any]:
    """Generate examples graph."""
    project_root = get_project_root()

    print("📚 Generating examples graph...")

    nodes = []

    # Scan examples directory
    examples_dir = project_root / "examples"
    if examples_dir.exists():
        for bot_dir in examples_dir.iterdir():
            if bot_dir.is_dir() and not bot_dir.name.startswith("."):
                # Add bot node
                bot_file = bot_dir / "bot.py"
                if bot_file.exists():
                    nodes.append(
                        create_node_from_file(bot_file, project_root, "example_bot")
                    )

                # Add other files in bot directory
                for file_path in bot_dir.glob("*.py"):
                    if file_path.name not in ["bot.py", "__init__.py"]:
                        nodes.append(
                            create_node_from_file(
                                file_path, project_root, "example_module"
                            )
                        )

    # Find edges
    python_files = list(examples_dir.rglob("*.py")) if examples_dir.exists() else []
    edges = find_imports_in_files(python_files, project_root)

    print(f"   Found {len(nodes)} nodes, {len(edges)} edges")

    return {
        "metadata": {
            "version": "3.0.0",
            "generated_at": datetime.now().strftime("%Y-%m-%d"),
            "graph_id": "examples",
            "graph_name": "Example Bots",
            "graph_type": "domain",
            "project_name": "telegram-bot-stack",
            "description": "Example bot implementations and usage patterns",
            "scope": "Example bots demonstrating framework features",
            "node_count": len(nodes),
            "edge_count": len(edges),
        },
        "nodes": nodes,
        "edges": edges,
    }


def save_graph(graph: Dict[str, Any], graph_name: str, dry_run: bool = False) -> None:
    """Save graph to file.

    Args:
        graph: Graph dictionary
        graph_name: Graph name (e.g., 'infrastructure')
        dry_run: If True, only print what would be saved
    """
    graph_root = get_graph_root()
    output_file = graph_root / graph_name / "graph.json"

    if dry_run:
        print(f"\n📄 Would save to: {output_file}")
        print(f"   Nodes: {len(graph['nodes'])}")
        print(f"   Edges: {len(graph['edges'])}")
    else:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(graph, f, indent=2)
        print(f"✅ Saved: {output_file}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate project graphs automatically"
    )
    parser.add_argument(
        "--graph",
        choices=["infrastructure", "testing", "examples", "all"],
        default="all",
        help="Which graph to generate (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without saving",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("🔧 Project Graph Generator")
    print("=" * 60)
    print()

    generators = {
        "infrastructure": generate_infrastructure_graph,
        "testing": generate_testing_graph,
        "examples": generate_examples_graph,
    }

    if args.graph == "all":
        graphs_to_generate = list(generators.keys())
    else:
        graphs_to_generate = [args.graph]

    for graph_name in graphs_to_generate:
        try:
            graph = generators[graph_name]()
            save_graph(graph, graph_name, dry_run=args.dry_run)
        except Exception as e:
            print(f"❌ Error generating {graph_name}: {e}", file=sys.stderr)
            import traceback

            traceback.print_exc()

    print()
    print("=" * 60)
    if args.dry_run:
        print("🔍 Dry run completed")
    else:
        print("✅ Graph generation completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
