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


def regenerate_bot_framework_graphs(dry_run: bool = False) -> None:
    """Regenerate bot_framework sub-graphs."""
    project_root = get_project_root()
    graph_root = get_graph_root()

    print("📦 Regenerating bot_framework graphs...")

    bot_dir = project_root / "telegram_bot_stack"
    if not bot_dir.exists():
        print("⚠️  telegram_bot_stack directory not found")
        return

    # Define sub-graphs
    sub_graphs = {
        "core": {
            "files": [
                "bot_base.py",
                "user_manager.py",
                "admin_manager.py",
                "__init__.py"
            ],
            "name": "Core",
            "description": "Core bot framework components",
        },
        "storage": {
            "directory": "storage",
            "name": "Storage",
            "description": "Storage abstraction layer and implementations",
        },
        "utilities": {
            "files": ["decorators.py"],
            "directories": ["cli"],
            "name": "Utilities",
            "description": "Utility functions and CLI tools",
        },
    }

    for sub_id, sub_info in sub_graphs.items():
        print(f"\n📊 Generating {sub_id} sub-graph...")

        nodes = []
        python_files = []

        # Collect files for this sub-graph
        if "directory" in sub_info:
            sub_dir = bot_dir / sub_info["directory"]
            if sub_dir.exists():
                python_files = list(sub_dir.rglob("*.py"))
        else:
            if "files" in sub_info:
                for fname in sub_info["files"]:
                    fpath = bot_dir / fname
                    if fpath.exists():
                        python_files.append(fpath)
            if "directories" in sub_info:
                for dname in sub_info["directories"]:
                    dpath = bot_dir / dname
                    if dpath.exists():
                        python_files.extend(dpath.rglob("*.py"))

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
            print(f"   ✅ Saved: {output_file.name}")


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
