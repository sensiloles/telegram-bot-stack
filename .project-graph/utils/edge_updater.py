#!/usr/bin/env python3
"""Update graph edges (dependencies) when imports change.

This module provides functionality to automatically update edges in graphs
when Python files are modified and their imports change.

Usage:
    from edge_updater import update_edges_for_file
    update_edges_for_file('telegram_bot_stack/storage/redis.py', graph)
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple


def extract_imports_from_file(file_path: Path, project_root: Path = None) -> Set[str]:
    """Extract all imports from a Python file.

    Args:
        file_path: Path to Python file (absolute or relative)
        project_root: Project root path (for resolving relative imports)

    Returns:
        Set of imported module names (e.g., {'telegram_bot_stack.storage.base'})
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent.parent

    try:
        with open(file_path) as f:
            tree = ast.parse(f.read())

        imports = set()

        # Determine current module path for resolving relative imports
        try:
            rel_path = file_path.relative_to(project_root)
            current_package_parts = rel_path.with_suffix('').parts
            if current_package_parts[-1] == '__init__':
                current_package_parts = current_package_parts[:-1]
            current_package = '.'.join(current_package_parts[:-1]) if len(current_package_parts) > 1 else ''
        except ValueError:
            current_package = ''

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ''

                # Handle relative imports (from .base import ...)
                if node.level > 0:
                    # Resolve relative import to absolute
                    if current_package:
                        package_parts = current_package.split('.')
                        # Go up 'level-1' directories
                        for _ in range(node.level - 1):
                            if package_parts:
                                package_parts.pop()

                        if package_parts:
                            base_package = '.'.join(package_parts)
                            if module:
                                resolved_module = f"{base_package}.{module}"
                            else:
                                resolved_module = base_package
                        else:
                            resolved_module = module if module else current_package
                    else:
                        resolved_module = module

                    # Check if it's internal
                    if resolved_module:
                        module_parts = resolved_module.split('.')
                        if module_parts[0] in ['telegram_bot_stack', 'tests', 'examples']:
                            imports.add(resolved_module)

                            # Also add specific imports
                            for alias in node.names:
                                if alias.name != '*' and alias.name != resolved_module.split('.')[-1]:
                                    full_import = f"{resolved_module}.{alias.name}"
                                    imports.add(full_import)

                # Handle absolute imports
                elif module:
                    # Check if it's internal import
                    module_parts = module.split('.')
                    if module_parts[0] in ['telegram_bot_stack', 'tests', 'examples']:
                        imports.add(module)

                        # Also add specific imports
                        for alias in node.names:
                            if alias.name != '*':
                                full_import = f"{module}.{alias.name}"
                                imports.add(full_import)

            elif isinstance(node, ast.Import):
                # import telegram_bot_stack.storage.base
                for alias in node.names:
                    module_parts = alias.name.split('.')
                    if module_parts[0] in ['telegram_bot_stack', 'tests', 'examples']:
                        imports.add(alias.name)

        return imports

    except Exception as e:
        print(f"⚠️  Warning: Could not extract imports from {file_path}: {e}")
        return set()


def file_path_to_node_id(file_path: str) -> str:
    """Convert file path to node ID.

    Args:
        file_path: Relative file path (e.g., 'telegram_bot_stack/storage/redis.py')

    Returns:
        Node ID (e.g., 'telegram_bot_stack.storage.redis')
    """
    path = Path(file_path)
    parts = path.with_suffix('').parts

    # Remove __init__ from path
    if parts[-1] == '__init__':
        parts = parts[:-1]

    return '.'.join(parts)


def module_to_node_id(module_name: str, graph: Dict) -> str:
    """Convert module name to actual node ID in graph.

    Args:
        module_name: Import module name (e.g., 'telegram_bot_stack.storage.base')
        graph: Graph dictionary

    Returns:
        Node ID if found, otherwise module name
    """
    # Try exact match first
    for node in graph.get('nodes', []):
        if node['id'] == module_name:
            return node['id']

    # Try parent module (for __init__ imports)
    # e.g., 'telegram_bot_stack.storage' might map to 'telegram_bot_stack.storage' node
    parts = module_name.split('.')
    while len(parts) > 1:
        parts.pop()
        parent_module = '.'.join(parts)
        for node in graph.get('nodes', []):
            if node['id'] == parent_module:
                return parent_module

    # Not found, return original
    return module_name


def update_edges_for_node(
    graph: Dict,
    node_id: str,
    new_imports: Set[str]
) -> Tuple[int, int]:
    """Update edges for a specific node based on new imports.

    Args:
        graph: Graph dictionary (will be modified)
        node_id: Node ID to update edges for
        new_imports: Set of imported modules

    Returns:
        Tuple of (added_count, removed_count)
    """
    # Get current edges from this node
    current_edges = [
        e for e in graph.get('edges', [])
        if e['source'] == node_id and e['type'] == 'imports'
    ]

    current_targets = {e['target'] for e in current_edges}

    # Map imports to actual node IDs
    new_targets = {
        module_to_node_id(imp, graph)
        for imp in new_imports
    }

    # Filter out targets that don't exist as nodes
    valid_targets = {
        t for t in new_targets
        if any(n['id'] == t for n in graph.get('nodes', []))
    }

    # Calculate changes
    to_add = valid_targets - current_targets
    to_remove = current_targets - valid_targets

    # Remove outdated edges
    graph['edges'] = [
        e for e in graph.get('edges', [])
        if not (e['source'] == node_id and e['type'] == 'imports' and e['target'] in to_remove)
    ]

    # Add new edges
    max_edge_id = max(
        [int(e['id'].split('_')[-1]) for e in graph.get('edges', []) if e['id'].startswith('edge_')],
        default=0
    )

    for i, target in enumerate(to_add, start=1):
        new_edge = {
            'id': f'edge_{max_edge_id + i}',
            'source': node_id,
            'target': target,
            'type': 'imports',
            'description': f'Imports from {target}'
        }
        graph.setdefault('edges', []).append(new_edge)

    return len(to_add), len(to_remove)


def update_edges_for_file(
    file_path: str,
    graph: Dict,
    project_root: Path
) -> Tuple[int, int]:
    """Update edges in graph when a file's imports change.

    Args:
        file_path: Relative path to changed file
        graph: Graph dictionary (will be modified)
        project_root: Project root path

    Returns:
        Tuple of (added_edges, removed_edges)
    """
    full_path = project_root / file_path

    if not full_path.exists() or not file_path.endswith('.py'):
        return 0, 0

    # Extract imports from file
    imports = extract_imports_from_file(full_path)

    if not imports:
        return 0, 0

    # Get node ID for this file
    node_id = file_path_to_node_id(file_path)

    # Check if node exists in graph
    if not any(n['id'] == node_id for n in graph.get('nodes', [])):
        return 0, 0

    # Update edges
    return update_edges_for_node(graph, node_id, imports)


def validate_graph_edges(graph: Dict) -> List[str]:
    """Validate that all edges reference existing nodes.

    Args:
        graph: Graph dictionary

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    node_ids = {n['id'] for n in graph.get('nodes', [])}

    for edge in graph.get('edges', []):
        source = edge.get('source')
        target = edge.get('target')

        if source not in node_ids:
            errors.append(f"Edge {edge['id']}: source '{source}' not found in nodes")

        if target not in node_ids:
            errors.append(f"Edge {edge['id']}: target '{target}' not found in nodes")

    return errors


def cleanup_orphan_edges(graph: Dict) -> int:
    """Remove edges that reference non-existent nodes.

    Args:
        graph: Graph dictionary (will be modified)

    Returns:
        Number of removed edges
    """
    node_ids = {n['id'] for n in graph.get('nodes', [])}

    original_count = len(graph.get('edges', []))

    graph['edges'] = [
        e for e in graph.get('edges', [])
        if e.get('source') in node_ids and e.get('target') in node_ids
    ]

    removed = original_count - len(graph['edges'])

    if removed > 0:
        print(f"   🧹 Cleaned up {removed} orphan edge(s)")

    return removed
