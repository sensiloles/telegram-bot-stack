"""Auto-update graphs when files change.

This module provides functionality to automatically update project graphs
when source files are modified. It uses file watching and AST parsing
to detect changes and update the relevant graphs.

Usage:
    # As a CLI tool
    python3 auto_update.py --watch

    # As a library
    from auto_update import update_graph_for_file
    update_graph_for_file('telegram_bot_stack/storage/redis.py')
"""

import ast
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def get_project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).parent.parent.parent


def get_graph_root() -> Path:
    """Get graph root directory."""
    return Path(__file__).parent.parent


def determine_graph_for_file(file_path: str) -> Optional[str]:
    """Determine which graph a file belongs to.

    Args:
        file_path: Path to file (relative to project root)

    Returns:
        Graph name or None if file doesn't belong to any graph
    """
    path = Path(file_path)
    path_str = str(path)

    # Bot framework
    if path_str.startswith("telegram_bot_stack/"):
        return "bot_framework"

    # Infrastructure
    if path_str.startswith(".github/") or path_str.startswith("scripts/"):
        return "infrastructure"

    # Testing
    if path_str.startswith("tests/"):
        return "testing"

    # Examples
    if path_str.startswith("examples/"):
        return "examples"

    # Documentation
    if path_str.startswith("docs/"):
        return "docs"

    # Configuration
    if path_str in [
        "pyproject.toml",
        ".pre-commit-config.yaml",
        "Makefile",
        "setup.py",
        "setup.cfg",
    ]:
        return "configuration"

    # Archive
    if path_str.startswith("archive/"):
        return "archive"

    return None


def determine_sub_graph_for_file(file_path: str) -> Optional[str]:
    """Determine which bot-framework sub-graph a file belongs to.

    Args:
        file_path: Path to file in telegram_bot_stack/

    Returns:
        Sub-graph name ('core', 'storage', 'utilities') or None
    """
    path = Path(file_path)

    # Storage
    if "storage/" in str(path):
        return "storage"

    # Core (bot_base, managers)
    if path.name in ["bot_base.py", "user_manager.py", "admin_manager.py"]:
        return "core"

    # Utilities (decorators, etc)
    if path.name in ["decorators.py"]:
        return "utilities"

    # CLI is utilities
    if "cli/" in str(path):
        return "utilities"

    return "core"  # Default to core


def analyze_python_file(file_path: Path) -> Dict:
    """Analyze Python file and extract metadata.

    Args:
        file_path: Path to Python file

    Returns:
        Dictionary with file metadata (classes, functions, imports, etc.)
    """
    try:
        with open(file_path) as f:
            source = f.read()
            tree = ast.parse(source)

        metadata = {
            "classes": [],
            "functions": [],
            "imports": [],
            "lines": len(source.splitlines()),
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                metadata["classes"].append(node.name)
            elif isinstance(node, ast.FunctionDef):
                if not node.name.startswith("_"):  # Skip private
                    metadata["functions"].append(node.name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        metadata["imports"].append(alias.name)
                elif node.module:
                    metadata["imports"].append(node.module)

        return metadata

    except Exception as e:
        print(f"⚠️  Warning: Could not analyze {file_path}: {e}", file=sys.stderr)
        return {"classes": [], "functions": [], "imports": [], "lines": 0}


def update_graph_metadata(graph_path: Path) -> None:
    """Update graph metadata (generated_at, etc.).

    Args:
        graph_path: Path to graph JSON file
    """
    with open(graph_path) as f:
        graph = json.load(f)

    # Update metadata
    if "metadata" in graph:
        graph["metadata"]["generated_at"] = datetime.now().strftime("%Y-%m-%d")
        graph["metadata"]["node_count"] = len(graph.get("nodes", []))
        graph["metadata"]["edge_count"] = len(graph.get("edges", []))

    # Save
    with open(graph_path, "w") as f:
        json.dump(graph, f, indent=2)


def find_graph_file(graph_name: str, sub_graph: Optional[str] = None) -> Optional[Path]:
    """Find graph JSON file for given graph name.

    Args:
        graph_name: Graph name (e.g., 'bot_framework')
        sub_graph: Optional sub-graph name (e.g., 'storage')

    Returns:
        Path to graph file or None
    """
    graph_root = get_graph_root()

    # Map graph names to files
    graph_files = {
        "bot_framework": {
            "core": "bot-framework/core-graph.json",
            "storage": "bot-framework/storage-graph.json",
            "utilities": "bot-framework/utilities-graph.json",
        },
        "infrastructure": "infrastructure/graph.json",
        "testing": "testing/graph.json",
        "examples": "examples/graph.json",
        "docs": "docs/graph.json",
        "configuration": "configuration/graph.json",
        "archive": "archive/graph.json",
        "project_meta": "project-meta/graph.json",
    }

    if graph_name == "bot_framework" and sub_graph:
        file_path = graph_files["bot_framework"].get(sub_graph)
    else:
        file_path = graph_files.get(graph_name)

    if file_path:
        full_path = graph_root / file_path
        return full_path if full_path.exists() else None

    return None


def update_graph_for_file(file_path: str, dry_run: bool = False) -> bool:
    """Update graph when a file changes.

    Args:
        file_path: Path to changed file (relative to project root)
        dry_run: If True, only print what would be updated

    Returns:
        True if graph was updated, False otherwise
    """
    # Determine which graph
    graph_name = determine_graph_for_file(file_path)
    if not graph_name:
        print(f"ℹ️  File {file_path} doesn't belong to any graph")
        return False

    # Determine sub-graph for bot_framework
    sub_graph = None
    if graph_name == "bot_framework":
        sub_graph = determine_sub_graph_for_file(file_path)

    # Find graph file
    graph_file = find_graph_file(graph_name, sub_graph)
    if not graph_file:
        print(f"❌ Graph file not found for {graph_name}/{sub_graph}")
        return False

    print(f"\n📝 File changed: {file_path}")
    print(f"📊 Updating graph: {graph_file.relative_to(get_graph_root())}")

    if dry_run:
        print("🔍 DRY RUN - Would update metadata")
        return False

    # Analyze file if Python
    if file_path.endswith(".py"):
        full_path = get_project_root() / file_path
        if full_path.exists():
            metadata = analyze_python_file(full_path)
            print(f"   Classes: {len(metadata['classes'])}")
            print(f"   Functions: {len(metadata['functions'])}")
            print(f"   Lines: {metadata['lines']}")

    # Update metadata
    try:
        update_graph_metadata(graph_file)
        print(f"✅ Updated: {graph_file.relative_to(get_graph_root())}")
        return True
    except Exception as e:
        print(f"❌ Failed to update: {e}", file=sys.stderr)
        return False


def watch_files(patterns: Optional[List[str]] = None, dry_run: bool = False) -> None:
    """Watch files for changes and auto-update graphs.

    Args:
        patterns: File patterns to watch (default: all Python files)
        dry_run: If True, only print what would be updated

    Requires:
        watchdog library (pip install watchdog)
    """
    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError:
        print("❌ watchdog not installed. Install with: pip install watchdog")
        sys.exit(1)

    class GraphUpdateHandler(FileSystemEventHandler):
        """Handler for file system events."""

        def on_modified(self, event):
            """Handle file modification."""
            if event.is_directory:
                return

            # Get relative path
            file_path = Path(event.src_path).relative_to(get_project_root())

            # Skip graph files themselves
            if ".project-graph/" in str(file_path):
                return

            # Skip generated files
            if any(x in str(file_path) for x in ["__pycache__", ".pyc", ".egg-info"]):
                return

            # Update graph
            update_graph_for_file(str(file_path), dry_run=dry_run)

    print("👁️  Watching for file changes...")
    print(f"📁 Root: {get_project_root()}")
    print("Press Ctrl+C to stop\n")

    event_handler = GraphUpdateHandler()
    observer = Observer()

    # Watch main directories
    directories = [
        "telegram_bot_stack",
        "tests",
        "examples",
        "docs",
        ".github",
        "scripts",
    ]

    for directory in directories:
        dir_path = get_project_root() / directory
        if dir_path.exists():
            observer.schedule(event_handler, str(dir_path), recursive=True)
            print(f"   Watching: {directory}/")

    observer.start()

    try:
        import time

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n\n✅ Stopped watching")

    observer.join()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Auto-update project graphs when files change"
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch files and auto-update graphs",
    )
    parser.add_argument(
        "--file",
        help="Update graph for specific file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without updating",
    )

    args = parser.parse_args()

    if args.watch:
        watch_files(dry_run=args.dry_run)
    elif args.file:
        update_graph_for_file(args.file, dry_run=args.dry_run)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
