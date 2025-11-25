"""Auto-update graphs when files change.

This module provides functionality to automatically update project graphs
when source files are modified. It uses file watching, AST parsing, and
file hashing to detect changes and update the relevant graphs.

Features:
    - File hash tracking to detect actual changes
    - AST-based analysis for Python files
    - Cross-graph update support (updates all related graphs)
    - Full graph regeneration on structural changes

Usage:
    # As a CLI tool
    python3 auto_update.py --watch

    # As a library
    from auto_update import update_graph_for_file
    update_graph_for_file('telegram_bot_stack/storage/redis.py')
"""

import ast
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from edge_updater import cleanup_orphan_edges, update_edges_for_file


def get_project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).parent.parent.parent


def get_graph_root() -> Path:
    """Get graph root directory."""
    return Path(__file__).parent.parent


def get_hash_cache_path() -> Path:
    """Get path to hash cache file."""
    return get_graph_root() / ".file_hashes.json"


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of file contents.

    Args:
        file_path: Path to file

    Returns:
        Hex digest of file hash
    """
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        # Read in chunks to handle large files
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_hash_cache() -> Dict[str, str]:
    """Load file hash cache.

    Returns:
        Dictionary mapping file paths to hashes
    """
    cache_path = get_hash_cache_path()
    if cache_path.exists():
        try:
            with open(cache_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_hash_cache(cache: Dict[str, str]) -> None:
    """Save file hash cache.

    Args:
        cache: Dictionary mapping file paths to hashes
    """
    cache_path = get_hash_cache_path()
    try:
        with open(cache_path, 'w') as f:
            json.dump(cache, f, indent=2)
            f.write("\n")
    except OSError as e:
        print(f"⚠️  Warning: Could not save hash cache: {e}", file=sys.stderr)


def has_file_changed(file_path: str) -> bool:
    """Check if file has changed based on hash.

    Args:
        file_path: Path to file (relative to project root)

    Returns:
        True if file changed or is new, False if unchanged
    """
    full_path = get_project_root() / file_path
    if not full_path.exists():
        return False

    cache = load_hash_cache()
    current_hash = compute_file_hash(full_path)
    cached_hash = cache.get(file_path)

    return current_hash != cached_hash


def update_file_hash(file_path: str) -> None:
    """Update hash for a file in cache.

    Args:
        file_path: Path to file (relative to project root)
    """
    full_path = get_project_root() / file_path
    if not full_path.exists():
        return

    cache = load_hash_cache()
    current_hash = compute_file_hash(full_path)
    cache[file_path] = current_hash
    save_hash_cache(cache)


def determine_graph_for_file(file_path: str) -> Optional[str]:
    """Determine which graph a file belongs to.

    Args:
        file_path: Path to file (relative to project root)

    Returns:
        Graph name or None if file doesn't belong to any graph
    """
    path = Path(file_path)
    path_str = str(path)

    # Bot framework (source code)
    if path_str.startswith("telegram_bot_stack/"):
        return "bot_framework"

    # Infrastructure (CI/CD, automation)
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

    # Archive
    if path_str.startswith("archive/"):
        return "archive"

    # Configuration files (build system, dependencies, IDE)
    if path_str in [
        "pyproject.toml",
        ".pre-commit-config.yaml",
        "Makefile",
        "setup.py",
        "setup.cfg",
        "requirements.txt",
        "requirements-dev.txt",
        ".env.example",
    ] or path_str.startswith(".vscode/") or path_str.startswith(".cursor/") or path_str.startswith(".idea/"):
        return "configuration"

    # Project meta (root level documentation and meta files)
    if path_str in [
        "README.md",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "LICENSE",
        "CODE_OF_CONDUCT.md",
        ".gitignore",
        ".gitattributes",
        ".cursorrules",
    ]:
        return "project_meta"

    # Project graph files themselves
    if path_str.startswith(".project-graph/"):
        return "project_meta"  # Graph files are meta-information about project

    return None


def determine_sub_graph_for_file(file_path: str) -> Optional[str]:
    """Determine which bot-framework sub-graph a file belongs to.

    Args:
        file_path: Path to file in telegram_bot_stack/

    Returns:
        Sub-graph name ('core', 'storage', 'utilities', 'cli') or None
    """
    path = Path(file_path)

    # CLI (has its own sub-graph with 2096 lines!)
    if "cli/" in str(path):
        return "cli"

    # Storage
    if "storage/" in str(path):
        return "storage"

    # Core (bot_base, managers)
    if path.name in ["bot_base.py", "user_manager.py", "admin_manager.py"]:
        return "core"

    # Utilities (decorators, etc)
    if path.name in ["decorators.py"]:
        return "utilities"

    return "core"  # Default to core


def determine_all_affected_graphs(file_path: str) -> List[Tuple[str, Optional[str]]]:
    """Determine all graphs that should be updated when a file changes.

    Args:
        file_path: Path to changed file (relative to project root)

    Returns:
        List of (graph_name, sub_graph) tuples that need updating
    """
    affected = []

    # Add primary graph
    primary_graph = determine_graph_for_file(file_path)
    if primary_graph:
        sub_graph = None
        if primary_graph == "bot_framework":
            sub_graph = determine_sub_graph_for_file(file_path)
        affected.append((primary_graph, sub_graph))

    # Check for cross-graph dependencies
    path_str = str(file_path)

    # If bot framework changes, tests might be affected
    if path_str.startswith("telegram_bot_stack/"):
        if ("testing", None) not in affected:
            affected.append(("testing", None))

    # If tests change, check if they're example tests
    if path_str.startswith("tests/examples/"):
        if ("examples", None) not in affected:
            affected.append(("examples", None))

    # If example changes, tests are affected
    if path_str.startswith("examples/"):
        if ("testing", None) not in affected:
            affected.append(("testing", None))

    # If infrastructure scripts change
    if path_str.startswith("scripts/") or path_str.startswith(".github/"):
        if ("infrastructure", None) not in affected:
            affected.append(("infrastructure", None))

    return affected


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
        f.write("\n")


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
            "cli": "bot-framework/cli-graph.json",
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


def create_node_from_metadata(file_path: str, metadata: Dict) -> Dict:
    """Create a new graph node from file metadata.

    Args:
        file_path: File path (relative to project root)
        metadata: Metadata from file analysis

    Returns:
        Node dictionary
    """
    path = Path(file_path)

    # Create node ID (convert path to dotted notation for Python files)
    if path.suffix == ".py":
        parts = path.with_suffix("").parts
        if parts[-1] == "__init__":
            parts = parts[:-1]
        node_id = ".".join(parts)
    else:
        node_id = str(path).replace("/", ".")

    # Determine node type
    if path.suffix == ".py":
        if path.name.startswith("test_"):
            node_type = "test_module"
        elif "examples/" in str(path) and path.name == "bot.py":
            node_type = "example_bot"
        else:
            node_type = "module"
    elif path.suffix in [".yml", ".yaml"]:
        node_type = "workflow"
    elif path.suffix == ".md":
        node_type = "doc"
    else:
        node_type = "config"

    # Create base node
    node = {
        "id": node_id,
        "name": path.stem,
        "type": node_type,
        "category": "implementation",
        "path": file_path,
        "description": metadata.get("description", f"Module {path.stem}"),
    }

    # Add Python-specific fields
    if path.suffix == ".py":
        node.update({
            "lines_of_code": metadata.get("lines", 0),
            "complexity_score": 1,  # Default, can be calculated later
            "exports": metadata.get("classes", []) + metadata.get("functions", []),
            "classes": metadata.get("classes", []),
            "functions": metadata.get("functions", []),
            "dependencies": [],  # Will be populated by import analysis
            "dependents": [],
            "criticality": "medium",  # Default
        })

    return node


def update_node_in_graph(graph_path: Path, file_path: str, metadata: Dict) -> bool:
    """Update a specific node in the graph with new metadata.

    If node doesn't exist, creates it.

    Args:
        graph_path: Path to graph JSON file
        file_path: File path (relative to project root)
        metadata: Metadata from file analysis

    Returns:
        True if node was updated/created, False otherwise
    """
    try:
        with open(graph_path) as f:
            graph = json.load(f)

        # Find node by path
        node_found = False
        for node in graph.get("nodes", []):
            if node.get("path") == file_path:
                node_found = True
                # Update node metadata
                if "lines" in metadata:
                    node["lines_of_code"] = metadata["lines"]
                if "classes" in metadata:
                    node["classes"] = metadata["classes"]
                if "functions" in metadata:
                    node["functions"] = metadata["functions"]
                if "description" in metadata:
                    node["description"] = metadata["description"]
                # Update exports (classes + functions)
                if "classes" in metadata and "functions" in metadata:
                    node["exports"] = metadata["classes"] + metadata["functions"]
                print(f"   ✅ Updated existing node: {node['id']}")
                break

        # If node not found, create it
        if not node_found:
            new_node = create_node_from_metadata(file_path, metadata)
            graph.setdefault("nodes", []).append(new_node)
            print(f"   ✨ Created new node: {new_node['id']}")
            node_found = True

        if node_found:
            # Update graph metadata
            graph["metadata"]["generated_at"] = datetime.now().strftime("%Y-%m-%d")
            graph["metadata"]["node_count"] = len(graph.get("nodes", []))
            graph["metadata"]["edge_count"] = len(graph.get("edges", []))

            # Save updated graph
            with open(graph_path, 'w') as f:
                json.dump(graph, f, indent=2)
                f.write("\n")
            return True
        else:
            return False

    except Exception as e:
        print(f"   ❌ Error updating node: {e}", file=sys.stderr)
        return False


def update_graph_for_file(file_path: str, dry_run: bool = False, force: bool = False) -> bool:
    """Update graph when a file changes.

    Args:
        file_path: Path to changed file (relative to project root)
        dry_run: If True, only print what would be updated
        force: If True, update even if hash hasn't changed

    Returns:
        True if graph was updated, False otherwise
    """
    # Check if file actually changed (via hash)
    if not force and not has_file_changed(file_path):
        print(f"⏭️  Skipping {file_path} - no changes detected (hash match)")
        return False

    # Get all affected graphs
    affected_graphs = determine_all_affected_graphs(file_path)
    if not affected_graphs:
        print(f"ℹ️  File {file_path} doesn't belong to any graph")
        return False

    print(f"\n📝 File changed: {file_path}")
    print(f"   Hash: Changed ✓")

    # Analyze file if Python
    metadata = {}
    if file_path.endswith(".py"):
        full_path = get_project_root() / file_path
        if full_path.exists():
            metadata = analyze_python_file(full_path)
            print(f"   Classes: {len(metadata.get('classes', []))}")
            print(f"   Functions: {len(metadata.get('functions', []))}")
            print(f"   Lines: {metadata.get('lines', 0)}")

    if dry_run:
        print(f"\n🔍 DRY RUN - Would update {len(affected_graphs)} graph(s):")
        for graph_name, sub_graph in affected_graphs:
            graph_label = f"{graph_name}/{sub_graph}" if sub_graph else graph_name
            print(f"   • {graph_label}")
        return False

    # Update all affected graphs
    updated_count = 0
    for graph_name, sub_graph in affected_graphs:
        graph_label = f"{graph_name}/{sub_graph}" if sub_graph else graph_name
        print(f"\n📊 Updating graph: {graph_label}")

        # Find graph file
        graph_file = find_graph_file(graph_name, sub_graph)
        if not graph_file:
            print(f"   ⚠️  Graph file not found for {graph_label}")
            continue

        # Update node in graph if metadata available
        if metadata and graph_file.exists():
            if update_node_in_graph(graph_file, file_path, metadata):
                print(f"   ✅ Updated node in {graph_file.name}")

                # Update edges if Python file
                if file_path.endswith('.py'):
                    try:
                        with open(graph_file) as f:
                            graph = json.load(f)

                        added, removed = update_edges_for_file(
                            file_path, graph, get_project_root()
                        )

                        if added > 0 or removed > 0:
                            print(f"   🔗 Updated edges: +{added}, -{removed}")

                            # Cleanup orphan edges
                            cleanup_orphan_edges(graph)

                            # Update metadata
                            graph["metadata"]["edge_count"] = len(graph.get("edges", []))

                            # Save
                            with open(graph_file, 'w') as f:
                                json.dump(graph, f, indent=2)
                                f.write("\n")
                    except Exception as e:
                        print(f"   ⚠️  Could not update edges: {e}", file=sys.stderr)

                updated_count += 1
            else:
                # If node not found, still update metadata
                try:
                    update_graph_metadata(graph_file)
                    print(f"   ✅ Updated metadata in {graph_file.name}")
                    updated_count += 1
                except Exception as e:
                    print(f"   ❌ Failed to update: {e}", file=sys.stderr)
        else:
            # Just update metadata
            try:
                update_graph_metadata(graph_file)
                print(f"   ✅ Updated metadata in {graph_file.name}")
                updated_count += 1
            except Exception as e:
                print(f"   ❌ Failed to update: {e}", file=sys.stderr)

    # Update hash cache
    if updated_count > 0:
        update_file_hash(file_path)
        print(f"\n✅ Successfully updated {updated_count} graph(s)")
        return True
    else:
        print(f"\n⚠️  No graphs were updated")
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

        def on_created(self, event):
            """Handle file creation."""
            if event.is_directory:
                return

            # Get relative path
            file_path = Path(event.src_path).relative_to(get_project_root())

            # Skip unwanted files
            if ".project-graph/" in str(file_path):
                return
            if any(x in str(file_path) for x in ["__pycache__", ".pyc", ".egg-info"]):
                return

            print(f"\n➕ New file detected: {file_path}")
            # Force update to add new node
            update_graph_for_file(str(file_path), dry_run=dry_run, force=True)

        def on_deleted(self, event):
            """Handle file deletion."""
            if event.is_directory:
                return

            # Get relative path
            file_path = Path(event.src_path).relative_to(get_project_root())

            # Skip unwanted files
            if ".project-graph/" in str(file_path):
                return
            if any(x in str(file_path) for x in ["__pycache__", ".pyc", ".egg-info"]):
                return

            print(f"\n🗑️  File deleted: {file_path}")

            # Get affected graphs and remove node
            affected_graphs = determine_all_affected_graphs(str(file_path))
            for graph_name, sub_graph in affected_graphs:
                graph_file = find_graph_file(graph_name, sub_graph)
                if graph_file and graph_file.exists():
                    remove_node_from_graph(graph_file, str(file_path))

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


def remove_node_from_graph(graph_path: Path, file_path: str) -> bool:
    """Remove a node from the graph when file is deleted.

    Args:
        graph_path: Path to graph JSON file
        file_path: File path (relative to project root)

    Returns:
        True if node was removed, False otherwise
    """
    try:
        with open(graph_path) as f:
            graph = json.load(f)

        # Find and remove node
        nodes = graph.get("nodes", [])
        original_count = len(nodes)
        graph["nodes"] = [n for n in nodes if n.get("path") != file_path]

        if len(graph["nodes"]) < original_count:
            # Node was removed, also remove related edges
            node_id = None
            for node in nodes:
                if node.get("path") == file_path:
                    node_id = node["id"]
                    break

            if node_id:
                edges = graph.get("edges", [])
                graph["edges"] = [
                    e for e in edges
                    if e.get("source") != node_id and e.get("target") != node_id
                ]

            # Update metadata
            graph["metadata"]["generated_at"] = datetime.now().strftime("%Y-%m-%d")
            graph["metadata"]["node_count"] = len(graph["nodes"])
            graph["metadata"]["edge_count"] = len(graph["edges"])

            # Save
            with open(graph_path, 'w') as f:
                json.dump(graph, f, indent=2)
                f.write("\n")

            print(f"   🗑️  Removed node for deleted file")
            return True
        else:
            print(f"   ℹ️  Node not found in graph")
            return False

    except Exception as e:
        print(f"   ❌ Error removing node: {e}", file=sys.stderr)
        return False


def init_hash_cache(force: bool = False, use_git: bool = True) -> None:
    """Initialize hash cache for all tracked files.

    Args:
        force: If True, recompute all hashes even if cache exists
        use_git: If True, use git ls-files to get list (respects .gitignore)
    """
    cache_path = get_hash_cache_path()

    if cache_path.exists() and not force:
        print(f"ℹ️  Hash cache already exists: {cache_path}")
        print("   Use --force to rebuild")
        return

    print("🔧 Initializing file hash cache...")
    project_root = get_project_root()
    cache = {}

    if use_git:
        # Use git to get all tracked files (respects .gitignore automatically)
        print("   📦 Using git ls-files (respects .gitignore)")
        import subprocess

        try:
            result = subprocess.run(
                ["git", "ls-files"],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=True,
            )

            tracked_files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
            print(f"   Found {len(tracked_files)} tracked files")

            file_count = 0
            for rel_path in tracked_files:
                file_path = project_root / rel_path

                # Skip the hash cache file itself
                if ".file_hashes.json" in rel_path:
                    continue

                if file_path.exists() and file_path.is_file():
                    try:
                        file_hash = compute_file_hash(file_path)
                        cache[rel_path] = file_hash
                        file_count += 1

                        if file_count % 50 == 0:
                            print(f"   Processed {file_count} files...")
                    except Exception as e:
                        print(f"   ⚠️  Could not hash {rel_path}: {e}")

        except subprocess.CalledProcessError as e:
            print(f"⚠️  Git command failed: {e}")
            print("   Falling back to directory scanning...")
            use_git = False

    if not use_git:
        # Fallback: scan directories manually
        print("   📁 Scanning directories manually")
        directories = [
            "telegram_bot_stack",
            "tests",
            "examples",
            "docs",
            ".github",
            "scripts",
            ".project-graph",
        ]

        file_count = 0
        for directory in directories:
            dir_path = project_root / directory
            if not dir_path.exists():
                continue

            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    # Skip unwanted files
                    if any(x in str(file_path) for x in ["__pycache__", ".pyc", ".egg-info", ".git", ".file_hashes.json"]):
                        continue

                    # Compute hash
                    rel_path = str(file_path.relative_to(project_root))
                    try:
                        file_hash = compute_file_hash(file_path)
                        cache[rel_path] = file_hash
                        file_count += 1
                        if file_count % 50 == 0:
                            print(f"   Processed {file_count} files...")
                    except Exception as e:
                        print(f"   ⚠️  Could not hash {rel_path}: {e}")

    # Save cache
    save_hash_cache(cache)
    print(f"✅ Hash cache initialized with {len(cache)} files")
    print(f"   Saved to: {cache_path}")


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
        "--init-cache",
        action="store_true",
        help="Initialize file hash cache",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without updating",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force update even if hash hasn't changed (or rebuild cache)",
    )
    parser.add_argument(
        "--no-git",
        action="store_true",
        help="Don't use git ls-files, scan directories manually instead",
    )

    args = parser.parse_args()

    if args.init_cache:
        init_hash_cache(force=args.force, use_git=not args.no_git)
    elif args.watch:
        watch_files(dry_run=args.dry_run)
    elif args.file:
        update_graph_for_file(args.file, dry_run=args.dry_run, force=args.force)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
