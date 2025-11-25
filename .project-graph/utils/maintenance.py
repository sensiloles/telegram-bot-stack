#!/usr/bin/env python3
"""Maintenance utilities for project graphs.

This module provides tools for:
- Cleaning up orphaned hash cache entries
- Validating graph integrity
- Finding and fixing inconsistencies

Usage:
    python3 maintenance.py --clean-cache
    python3 maintenance.py --validate-all
    python3 maintenance.py --fix-orphans
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from auto_update import (
    get_hash_cache_path,
    get_project_root,
    load_hash_cache,
    save_hash_cache,
)
from edge_updater import cleanup_orphan_edges, validate_graph_edges


def get_graph_root() -> Path:
    """Get graph root directory."""
    return Path(__file__).parent.parent


def clean_hash_cache(dry_run: bool = False) -> int:
    """Remove hash cache entries for non-existent files.

    Args:
        dry_run: If True, only report what would be removed

    Returns:
        Number of removed entries
    """
    project_root = get_project_root()
    cache = load_hash_cache()

    original_count = len(cache)
    removed_files = []

    # Check each cached file
    for file_path in list(cache.keys()):
        full_path = project_root / file_path
        if not full_path.exists():
            removed_files.append(file_path)
            if not dry_run:
                del cache[file_path]

    removed_count = len(removed_files)

    if removed_count > 0:
        print(f"\n🧹 Hash Cache Cleanup")
        print(f"   Total entries: {original_count}")
        print(f"   Orphaned: {removed_count}")

        if dry_run:
            print(f"\n   Would remove:")
            for fp in removed_files[:10]:
                print(f"      - {fp}")
            if len(removed_files) > 10:
                print(f"      ... and {len(removed_files) - 10} more")
        else:
            save_hash_cache(cache)
            print(f"   ✅ Removed {removed_count} orphaned entries")
    else:
        print("✅ Hash cache is clean (no orphaned entries)")

    return removed_count


def validate_all_graphs(fix: bool = False) -> Dict[str, List[str]]:
    """Validate all graphs for integrity issues.

    Args:
        fix: If True, attempt to fix found issues

    Returns:
        Dictionary mapping graph name to list of errors
    """
    graph_root = get_graph_root()
    results = {}

    print("\n🔍 Validating Project Graphs")
    print("=" * 60)

    # Find all graph files
    graph_files = list(graph_root.rglob("*graph*.json"))
    graph_files = [
        f for f in graph_files
        if f.name not in ['.file_hashes.json', 'graph-router.json']
        and 'router.json' not in f.name
    ]

    for graph_file in sorted(graph_files):
        rel_path = graph_file.relative_to(graph_root)
        print(f"\n📊 {rel_path}")

        try:
            with open(graph_file) as f:
                graph = json.load(f)

            errors = []

            # Validate structure
            if 'metadata' not in graph:
                errors.append("Missing 'metadata' section")

            if 'nodes' not in graph:
                errors.append("Missing 'nodes' array")

            if 'edges' not in graph:
                errors.append("Missing 'edges' array")

            # Validate metadata counts
            if 'nodes' in graph and 'metadata' in graph:
                actual_nodes = len(graph['nodes'])
                declared_nodes = graph['metadata'].get('node_count', 0)
                if actual_nodes != declared_nodes:
                    errors.append(
                        f"Node count mismatch: declared {declared_nodes}, actual {actual_nodes}"
                    )
                    if fix:
                        graph['metadata']['node_count'] = actual_nodes
                        print(f"   🔧 Fixed node_count: {declared_nodes} → {actual_nodes}")

            if 'edges' in graph and 'metadata' in graph:
                actual_edges = len(graph['edges'])
                declared_edges = graph['metadata'].get('edge_count', 0)
                if actual_edges != declared_edges:
                    errors.append(
                        f"Edge count mismatch: declared {declared_edges}, actual {actual_edges}"
                    )
                    if fix:
                        graph['metadata']['edge_count'] = actual_edges
                        print(f"   🔧 Fixed edge_count: {declared_edges} → {actual_edges}")

            # Validate edges reference existing nodes
            edge_errors = validate_graph_edges(graph)
            if edge_errors:
                errors.extend(edge_errors)
                if fix:
                    removed = cleanup_orphan_edges(graph)
                    if removed > 0:
                        graph['metadata']['edge_count'] = len(graph['edges'])
                        print(f"   🔧 Removed {removed} orphan edges")

            # Check for duplicate node IDs
            node_ids = [n['id'] for n in graph.get('nodes', [])]
            duplicates = {nid for nid in node_ids if node_ids.count(nid) > 1}
            if duplicates:
                errors.append(f"Duplicate node IDs: {duplicates}")

            # Check for duplicate edge IDs
            edge_ids = [e['id'] for e in graph.get('edges', [])]
            dup_edges = {eid for eid in edge_ids if edge_ids.count(eid) > 1}
            if dup_edges:
                errors.append(f"Duplicate edge IDs: {dup_edges}")

            # Save if fixed
            if fix and (edge_errors or errors):
                with open(graph_file, 'w') as f:
                    json.dump(graph, f, indent=2)
                    f.write("\n")

            # Report
            if errors:
                print(f"   ❌ Found {len(errors)} issue(s)")
                for err in errors[:5]:
                    print(f"      - {err}")
                if len(errors) > 5:
                    print(f"      ... and {len(errors) - 5} more")
                results[str(rel_path)] = errors
            else:
                print(f"   ✅ Valid")

        except json.JSONDecodeError as e:
            error = f"Invalid JSON: {e}"
            print(f"   ❌ {error}")
            results[str(rel_path)] = [error]
        except Exception as e:
            error = f"Error: {e}"
            print(f"   ❌ {error}")
            results[str(rel_path)] = [error]

    # Summary
    print("\n" + "=" * 60)
    if results:
        print(f"⚠️  Found issues in {len(results)} graph(s)")
        if fix:
            print("✅ Attempted to fix issues")
    else:
        print("✅ All graphs are valid!")
    print("=" * 60)

    return results


def find_missing_nodes(verbose: bool = False) -> Dict[str, List[str]]:
    """Find files that should be in graphs but aren't.

    Args:
        verbose: If True, print detailed information

    Returns:
        Dictionary mapping graph name to list of missing file paths
    """
    project_root = get_project_root()
    graph_root = get_graph_root()
    missing = {}

    print("\n🔍 Finding Missing Nodes")
    print("=" * 60)

    # Check each domain
    domains = {
        'bot_framework': 'telegram_bot_stack',
        'testing': 'tests',
        'examples': 'examples',
        'infrastructure': ['.github', 'scripts'],
        'docs': 'docs',
    }

    for graph_name, directories in domains.items():
        if isinstance(directories, str):
            directories = [directories]

        print(f"\n📊 Checking {graph_name}")

        # Load all graphs for this domain
        if graph_name == 'bot_framework':
            graph_files = list((graph_root / 'bot-framework').glob('*-graph.json'))
        else:
            graph_file = graph_root / graph_name / 'graph.json'
            graph_files = [graph_file] if graph_file.exists() else []

        if not graph_files:
            print(f"   ⚠️  No graph files found")
            continue

        # Collect all node paths from graphs
        node_paths = set()
        for gf in graph_files:
            with open(gf) as f:
                graph = json.load(f)
            for node in graph.get('nodes', []):
                if 'path' in node:
                    node_paths.add(node['path'])

        # Find all Python files in directories
        actual_files = set()
        for directory in directories:
            dir_path = project_root / directory
            if dir_path.exists():
                for py_file in dir_path.rglob('*.py'):
                    # Skip __pycache__, etc
                    if '__pycache__' in str(py_file) or '.egg-info' in str(py_file):
                        continue
                    rel_path = str(py_file.relative_to(project_root))
                    actual_files.add(rel_path)

        # Find missing
        missing_files = actual_files - node_paths

        if missing_files:
            print(f"   ⚠️  Found {len(missing_files)} missing file(s)")
            if verbose:
                for mf in sorted(missing_files)[:10]:
                    print(f"      - {mf}")
                if len(missing_files) > 10:
                    print(f"      ... and {len(missing_files) - 10} more")
            missing[graph_name] = sorted(missing_files)
        else:
            print(f"   ✅ All files present")

    print("\n" + "=" * 60)
    if missing:
        total_missing = sum(len(files) for files in missing.values())
        print(f"⚠️  Total missing: {total_missing} file(s) across {len(missing)} graph(s)")
        print("   Run with --verbose to see details")
        print("   Consider running full regeneration: python3 utils/regenerate_all.py")
    else:
        print("✅ All files are present in graphs!")
    print("=" * 60)

    return missing


def check_graph_freshness() -> Dict[str, Tuple[str, int]]:
    """Check if graphs are outdated compared to source files.

    Returns:
        Dictionary mapping graph path to (status, days_old)
    """
    from datetime import datetime

    graph_root = get_graph_root()
    results = {}

    print("\n📅 Checking Graph Freshness")
    print("=" * 60)

    graph_files = list(graph_root.rglob("*graph*.json"))
    graph_files = [
        f for f in graph_files
        if f.name not in ['.file_hashes.json']
        and 'router.json' not in f.name
    ]

    for graph_file in sorted(graph_files):
        rel_path = graph_file.relative_to(graph_root)

        try:
            with open(graph_file) as f:
                graph = json.load(f)

            generated_at = graph.get('metadata', {}).get('generated_at')

            if not generated_at:
                print(f"   ⚠️  {rel_path}: No generation date")
                results[str(rel_path)] = ('unknown', 0)
                continue

            # Parse date
            gen_date = datetime.strptime(generated_at, '%Y-%m-%d')
            today = datetime.now()
            days_old = (today - gen_date).days

            status = 'fresh' if days_old < 7 else 'stale' if days_old < 30 else 'outdated'

            symbol = '✅' if status == 'fresh' else '⚠️' if status == 'stale' else '❌'
            print(f"   {symbol} {rel_path}: {days_old} days old ({status})")

            results[str(rel_path)] = (status, days_old)

        except Exception as e:
            print(f"   ❌ {rel_path}: Error - {e}")
            results[str(rel_path)] = ('error', 0)

    print("=" * 60)
    return results


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Maintenance utilities for project graphs"
    )
    parser.add_argument(
        '--clean-cache',
        action='store_true',
        help='Remove orphaned hash cache entries'
    )
    parser.add_argument(
        '--validate-all',
        action='store_true',
        help='Validate all graphs for integrity'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Attempt to fix found issues (use with --validate-all)'
    )
    parser.add_argument(
        '--find-missing',
        action='store_true',
        help='Find files that should be in graphs but aren\'t'
    )
    parser.add_argument(
        '--check-freshness',
        action='store_true',
        help='Check if graphs are outdated'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all checks'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed information'
    )

    args = parser.parse_args()

    # If no specific action, show help
    if not any([
        args.clean_cache,
        args.validate_all,
        args.find_missing,
        args.check_freshness,
        args.all
    ]):
        parser.print_help()
        return

    print("🛠️  Project Graph Maintenance")
    print("=" * 60)

    if args.all or args.clean_cache:
        clean_hash_cache(dry_run=args.dry_run)

    if args.all or args.validate_all:
        validate_all_graphs(fix=args.fix and not args.dry_run)

    if args.all or args.find_missing:
        find_missing_nodes(verbose=args.verbose)

    if args.all or args.check_freshness:
        check_graph_freshness()

    print("\n✅ Maintenance complete")


if __name__ == '__main__':
    main()
