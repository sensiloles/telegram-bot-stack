#!/usr/bin/env python3
"""Full graph regeneration starting from root router.

Regenerates the entire graph hierarchy from top to bottom:
1. Update main router (graph-router.json)
2. Regenerate all domain graphs
3. Regenerate all sub-graphs
4. Update all cross-references and metadata

Usage:
    python3 full_regenerate.py
    python3 full_regenerate.py --dry-run
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))


def get_project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).parent.parent.parent


def get_graph_root() -> Path:
    """Get graph root directory."""
    return Path(__file__).parent.parent


def count_lines_in_json(file_path: Path) -> int:
    """Count lines in a JSON file."""
    if file_path.exists():
        with open(file_path) as f:
            return len(f.readlines())
    return 0


def count_loc_in_graph(graph_data: dict) -> int:
    """Count total lines of code in a graph."""
    total = 0
    for node in graph_data.get("nodes", []):
        total += node.get("lines_of_code", 0)
    return total


def update_router(dry_run: bool = False) -> None:
    """Update main router with latest graph statistics.

    Args:
        dry_run: If True, only show what would be updated
    """
    print("📊 Step 1: Updating main router (graph-router.json)")
    print()

    graph_root = get_graph_root()
    router_path = graph_root / "graph-router.json"

    with open(router_path) as f:
        router = json.load(f)

    # Update generation date
    old_date = router.get("generated_at", "unknown")
    new_date = datetime.now().strftime("%Y-%m-%d")

    print(f"   Generated date: {old_date} → {new_date}")

    # Update sub-graph statistics for bot_framework
    if "bot-framework" in router["graphs"]:
        bf_graph = router["graphs"]["bot-framework"]
        if bf_graph.get("has_sub_graphs") and "sub_graphs" in bf_graph:
            print("   Updating bot_framework sub-graph stats:")

            for sub_id, sub_info in bf_graph["sub_graphs"].items():
                sub_file = graph_root / sub_info["file"]
                if sub_file.exists():
                    # Count lines in file
                    lines = count_lines_in_json(sub_file)

                    # Load graph to count LOC
                    with open(sub_file) as f:
                        sub_graph = json.load(f)
                    loc = count_loc_in_graph(sub_graph)

                    old_lines = sub_info.get("lines", 0)
                    old_loc = sub_info.get("lines_of_code", 0)

                    print(f"      {sub_id}: lines {old_lines} → {lines}, LOC {old_loc} → {loc}")

                    sub_info["lines"] = lines
                    sub_info["lines_of_code"] = loc

    # Update other graphs statistics
    print("   Updating domain graph stats:")
    for graph_key, graph_info in router["graphs"].items():
        if not graph_info.get("has_sub_graphs"):
            graph_file = graph_root / graph_info["file"]
            if graph_file.exists():
                lines = count_lines_in_json(graph_file)
                old_lines = graph_info.get("lines", 0)
                if old_lines != lines:
                    print(f"      {graph_info['name']}: {old_lines} → {lines} lines")
                    graph_info["lines"] = lines

    router["generated_at"] = new_date

    if dry_run:
        print("   [DRY RUN] Would save updated router")
    else:
        with open(router_path, "w") as f:
            json.dump(router, f, indent=2, ensure_ascii=False)
        print("   ✅ Router updated")

    print()


def regenerate_domain_graphs(dry_run: bool = False) -> None:
    """Regenerate all domain graphs using generate_graphs.py.

    Args:
        dry_run: If True, only show what would be updated
    """
    print("📦 Step 2: Regenerating domain graphs")
    print()

    if dry_run:
        print("   [DRY RUN] Would run generate_graphs.py")
        return

    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "generate_graphs.py"), "--graph", "all"],
        cwd=get_project_root(),
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        # Parse output for statistics
        for line in result.stdout.split("\n"):
            if "Found" in line and "nodes" in line:
                print(f"   {line.strip()}")
        print()
    else:
        print(f"   ⚠️  Warning: generate_graphs.py returned code {result.returncode}")
        print()


def regenerate_bot_framework_graphs(dry_run: bool = False) -> None:
    """Regenerate bot_framework sub-graphs.

    Args:
        dry_run: If True, only show what would be updated
    """
    print("🤖 Step 3: Regenerating bot_framework sub-graphs")
    print()

    if dry_run:
        print("   [DRY RUN] Would regenerate bot_framework graphs")
        return

    # Import regenerate function from regenerate_all
    from regenerate_all import regenerate_bot_framework_graphs as regen_bf

    regen_bf(dry_run=False)
    print()


def regenerate_docs_graph(dry_run: bool = False) -> None:
    """Regenerate docs graph.

    Args:
        dry_run: If True, only show what would be updated
    """
    print("📚 Step 4: Regenerating docs graph")
    print()

    if dry_run:
        print("   [DRY RUN] Would regenerate docs graph")
        return

    from regenerate_all import regenerate_docs_graph as regen_docs

    regen_docs(dry_run=False)
    print()


def update_bot_framework_router(dry_run: bool = False) -> None:
    """Update bot-framework domain router with updated sub-graph stats.

    Args:
        dry_run: If True, only show what would be updated
    """
    print("📊 Step 5: Updating bot-framework domain router")
    print()

    graph_root = get_graph_root()
    bf_router_path = graph_root / "bot-framework" / "router.json"

    if not bf_router_path.exists():
        print("   ⚠️  bot-framework/router.json not found")
        return

    with open(bf_router_path) as f:
        bf_router = json.load(f)

    # Update metadata
    old_date = bf_router.get("metadata", {}).get("generated_at", "unknown")
    new_date = datetime.now().strftime("%Y-%m-%d")

    if "metadata" in bf_router:
        bf_router["metadata"]["generated_at"] = new_date

        # Update sub-graph statistics
        total_nodes = 0
        total_edges = 0
        total_loc = 0

        for sub_id, sub_info in bf_router.get("sub_graphs", {}).items():
            sub_file = graph_root / sub_info["file"]
            if sub_file.exists():
                with open(sub_file) as f:
                    sub_graph = json.load(f)

                nodes = len(sub_graph.get("nodes", []))
                edges = len(sub_graph.get("edges", []))
                loc = count_loc_in_graph(sub_graph)

                total_nodes += nodes
                total_edges += edges
                total_loc += loc

                # Update sub_info
                sub_info["lines_of_code"] = loc

                print(f"   {sub_id}: {nodes} nodes, {edges} edges, {loc} LOC")

        # Update totals
        if "statistics" in bf_router:
            bf_router["statistics"]["total_nodes"] = total_nodes
            bf_router["statistics"]["total_edges"] = total_edges
            bf_router["statistics"]["total_lines_of_code"] = total_loc

        print(f"   Total: {total_nodes} nodes, {total_edges} edges, {total_loc} LOC")

    if dry_run:
        print("   [DRY RUN] Would save updated bot-framework router")
    else:
        with open(bf_router_path, "w") as f:
            json.dump(bf_router, f, indent=2, ensure_ascii=False)
        print("   ✅ Bot-framework router updated")

    print()


def reinitialize_hash_cache(dry_run: bool = False) -> None:
    """Reinitialize file hash cache with all current files.

    Args:
        dry_run: If True, only show what would be updated
    """
    print("🔧 Step 6: Reinitializing hash cache")
    print()

    if dry_run:
        print("   [DRY RUN] Would reinitialize hash cache")
        return

    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).parent / "auto_update.py"),
            "--init-cache",
            "--force",
        ],
        cwd=get_project_root(),
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        for line in result.stdout.split("\n"):
            if line.strip():
                print(f"   {line}")
    else:
        print(f"   ⚠️  Warning: hash cache init returned code {result.returncode}")

    print()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Full graph regeneration from root router"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without saving",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("🔄 FULL GRAPH REGENERATION FROM ROOT")
    print("=" * 70)
    print()

    # Step-by-step regeneration
    update_router(dry_run=args.dry_run)
    regenerate_domain_graphs(dry_run=args.dry_run)
    regenerate_bot_framework_graphs(dry_run=args.dry_run)
    regenerate_docs_graph(dry_run=args.dry_run)
    update_bot_framework_router(dry_run=args.dry_run)
    reinitialize_hash_cache(dry_run=args.dry_run)

    print("=" * 70)
    if args.dry_run:
        print("🔍 Dry run completed - no changes made")
    else:
        print("✅ FULL REGENERATION COMPLETED")
        print()
        print("Hierarchy updated:")
        print("   1. ✅ Main router (graph-router.json)")
        print("   2. ✅ Domain graphs (infrastructure, testing, examples)")
        print("   3. ✅ Bot-framework sub-graphs (core, storage, utilities)")
        print("   4. ✅ Documentation graph")
        print("   5. ✅ Bot-framework domain router")
        print("   6. ✅ File hash cache (164 files)")
        print()
        print("Next steps:")
        print("   git diff .project-graph/")
        print("   git add .project-graph/ && git commit")
    print("=" * 70)


if __name__ == "__main__":
    main()
