#!/usr/bin/env python3
"""Schema standardization and validation for project graphs.

This module ensures all graphs follow a consistent schema with:
- Mandatory fields that must be present
- Optional fields that can be auto-generated
- Type-specific fields for different node types

Usage:
    # Analyze current state
    python3 schema_standardizer.py --analyze

    # Standardize all graphs
    python3 schema_standardizer.py --standardize

    # Validate graphs against schema
    python3 schema_standardizer.py --validate
"""

import ast
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))


def get_graph_root() -> Path:
    """Get graph root directory."""
    return Path(__file__).parent.parent


def get_project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).parent.parent.parent


# ============================================================================
# SCHEMA DEFINITION
# ============================================================================

METADATA_SCHEMA = {
    # Mandatory fields (auto-generated)
    'mandatory': {
        'version': 'string',           # Schema version
        'generated_at': 'string',      # Date (YYYY-MM-DD)
        'graph_id': 'string',          # Unique graph identifier
        'graph_name': 'string',        # Human-readable name
        'graph_type': 'string',        # domain, domain_router, specialized
        'project_name': 'string',      # Project name
        'description': 'string',       # Graph description
        'scope': 'string',             # What this graph covers
        'node_count': 'integer',       # Number of nodes (auto-calculated)
        'edge_count': 'integer',       # Number of edges (auto-calculated)
    },

    # Optional fields (conditionally auto-generated)
    'optional': {
        'project_version': 'string',   # Project version (from pyproject.toml)
        'parent_graph': 'string',      # For sub-graphs
        'root_package': 'string',      # For code graphs
        'has_sub_graphs': 'boolean',   # For hierarchical graphs
        'sub_graphs': 'object',        # Sub-graph metadata
    },

    # Deprecated fields (should be removed)
    'deprecated': {
        'router_file',     # Only in project_meta
        'related_graphs',  # Should be in router, not metadata
    }
}


NODE_SCHEMA = {
    # Mandatory for ALL nodes (auto-generated)
    'mandatory': {
        'id': 'string',                # Unique node identifier
        'name': 'string',              # Node display name
        'type': 'string',              # Node type (see NODE_TYPES)
        'path': 'string',              # Relative file path
        'description': 'string',       # Node description (auto-gen from docstring or name)
    },

    # For Python modules/files
    'python_module': {
        'lines_of_code': 'integer',    # Auto: line count
        'classes': 'array',            # Auto: extracted from AST
        'functions': 'array',          # Auto: extracted from AST
        'exports': 'array',            # Auto: classes + functions
        'complexity_score': 'integer', # Auto: basic complexity calculation
    },

    # For all code files
    'code_file': {
        'dependencies': 'array',       # Auto: extracted from imports
        'dependents': 'array',         # Auto: calculated from edges
        'criticality': 'string',       # Auto: calculated from usage (low/medium/high/critical)
    },

    # Type-specific optional
    'optional': {
        'category': 'string',          # Auto: implementation/test/config/doc
        'tags': 'array',               # Manual: for special classification
        'language': 'string',          # Auto: file extension -> language
        'status': 'string',            # Manual: active/deprecated/experimental
        'format': 'string',            # For config files: yaml/json/toml
    },

    # Deprecated (archive graph only - don't use elsewhere)
    'deprecated_archive_only': {
        'phases',          # Only for archived plans
        'reason',          # Only for archived items
        'archived_date',   # Only for archived items
        'audience',        # Use tags instead
        'referenced_by',   # Use dependents
        'references',      # Use dependencies
        'affects',         # Too vague, use dependencies
        'configures',      # Too specific
        'services',        # Too specific
        'hooks',           # Should be in node description or exports
        'purposes',        # Use description
        'targets',         # Use dependencies
        'sections',        # For docs, use structure analysis
        'base_image',      # Too specific (Docker)
    }
}


NODE_TYPES = {
    # Code modules
    'module': 'Python module',
    'package': 'Python package (__init__.py)',
    'test_module': 'Test file',
    'example_bot': 'Example bot implementation',
    'example_module': 'Example bot helper module',

    # Scripts and automation
    'script': 'Executable script',
    'workflow': 'GitHub Actions workflow',

    # Documentation
    'doc': 'Documentation file',
    'documentation': 'Documentation file',

    # Configuration
    'config': 'Configuration file',
    'configuration': 'Configuration file',

    # Other
    'meta': 'Meta-information file',
    'historical': 'Historical/archived content',
}


CRITICALITY_RULES = {
    # Based on usage patterns
    'critical': [
        'bot_base', 'storage', 'base', '__init__', 'main'
    ],
    'high': [
        'manager', 'handler', 'command', 'api'
    ],
    'medium': [
        'util', 'helper', 'decorator'
    ],
    'low': [
        'test_', 'example', 'doc', 'readme'
    ]
}


# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def analyze_all_graphs() -> Dict[str, Any]:
    """Analyze all graphs and report inconsistencies.

    Returns:
        Dictionary with analysis results
    """
    graph_root = get_graph_root()

    # Find all graphs
    graph_files = []
    for pattern in ['*/graph.json', '*/*-graph.json']:
        graph_files.extend(graph_root.glob(pattern))

    # Exclude routers
    graph_files = [f for f in graph_files if 'router.json' not in f.name]

    results = {
        'total_graphs': len(graph_files),
        'graphs': {},
        'field_coverage': {},
        'issues': []
    }

    all_metadata_fields = set()
    all_node_fields = set()
    field_counts = {}

    print(f"\n📊 Analyzing {len(graph_files)} graphs")
    print("=" * 70)

    for graph_file in sorted(graph_files):
        rel_path = graph_file.relative_to(graph_root)

        try:
            with open(graph_file) as f:
                graph = json.load(f)

            graph_id = graph.get('metadata', {}).get('graph_id', rel_path.stem)

            # Analyze metadata
            metadata = graph.get('metadata', {})
            metadata_fields = set(metadata.keys())
            all_metadata_fields.update(metadata_fields)

            # Analyze nodes
            nodes = graph.get('nodes', [])
            node_fields_in_graph = set()

            for node in nodes:
                node_fields = set(node.keys())
                node_fields_in_graph.update(node_fields)
                all_node_fields.update(node_fields)

                for field in node_fields:
                    field_counts[field] = field_counts.get(field, 0) + 1

            # Check for issues
            graph_issues = []

            # Missing mandatory metadata
            for field in METADATA_SCHEMA['mandatory']:
                if field not in metadata_fields:
                    graph_issues.append(f"Missing mandatory metadata: {field}")

            # Deprecated metadata
            for field in METADATA_SCHEMA['deprecated']:
                if field in metadata_fields:
                    graph_issues.append(f"Using deprecated metadata: {field}")

            # Check nodes
            for i, node in enumerate(nodes[:10]):  # Check first 10
                for field in NODE_SCHEMA['mandatory']:
                    if field not in node:
                        graph_issues.append(f"Node {i} missing mandatory field: {field}")
                        break

                # Check for deprecated fields
                for field in NODE_SCHEMA['deprecated_archive_only']:
                    if field in node and graph_id != 'archive':
                        graph_issues.append(f"Node {i} using deprecated field: {field}")
                        break

            results['graphs'][graph_id] = {
                'file': str(rel_path),
                'metadata_fields': len(metadata_fields),
                'node_count': len(nodes),
                'node_fields': len(node_fields_in_graph),
                'issues': graph_issues
            }

            # Report
            status = "✅" if not graph_issues else "⚠️"
            print(f"{status} {graph_id:25} | nodes: {len(nodes):3} | fields: {len(node_fields_in_graph):2} | issues: {len(graph_issues)}")

            if graph_issues and len(graph_issues) <= 3:
                for issue in graph_issues[:3]:
                    print(f"      - {issue}")

        except Exception as e:
            results['issues'].append(f"Error reading {rel_path}: {e}")
            print(f"❌ {rel_path}: Error - {e}")

    results['all_metadata_fields'] = sorted(all_metadata_fields)
    results['all_node_fields'] = sorted(all_node_fields)
    results['field_counts'] = field_counts

    print("=" * 70)

    return results


def calculate_criticality(node: Dict[str, Any]) -> str:
    """Calculate node criticality based on content and usage.

    Args:
        node: Node dictionary

    Returns:
        Criticality level (low/medium/high/critical)
    """
    node_id = node.get('id', '').lower()
    node_name = node.get('name', '').lower()
    node_type = node.get('type', '')

    # Check rules
    for level, patterns in CRITICALITY_RULES.items():
        for pattern in patterns:
            if pattern in node_id or pattern in node_name:
                return level

    # Default based on type
    if node_type in ['test_module', 'doc', 'documentation']:
        return 'low'
    elif node_type in ['workflow', 'config']:
        return 'medium'
    elif node_type in ['module', 'package']:
        # Count dependents if available
        dependents = len(node.get('dependents', []))
        if dependents > 5:
            return 'critical'
        elif dependents > 2:
            return 'high'
        else:
            return 'medium'

    return 'medium'


def calculate_complexity(node: Dict[str, Any]) -> int:
    """Calculate basic complexity score.

    Args:
        node: Node dictionary

    Returns:
        Complexity score (1-5)
    """
    # Simple heuristic based on lines of code and exports
    lines = node.get('lines_of_code', 0)
    exports = len(node.get('exports', []))
    classes = len(node.get('classes', []))

    score = 1

    if lines > 500:
        score += 2
    elif lines > 200:
        score += 1

    if exports > 10:
        score += 1

    if classes > 3:
        score += 1

    return min(score, 5)


def determine_category(node: Dict[str, Any]) -> str:
    """Determine node category.

    Args:
        node: Node dictionary

    Returns:
        Category name
    """
    node_type = node.get('type', '')
    path = node.get('path', '')

    if 'test' in node_type or 'tests/' in path:
        return 'testing'
    elif node_type in ['doc', 'documentation']:
        return 'documentation'
    elif node_type in ['config', 'configuration', 'workflow']:
        return 'configuration'
    elif 'example' in node_type or 'examples/' in path:
        return 'examples'
    elif 'archive' in path:
        return 'historical'
    else:
        return 'implementation'


def standardize_node(node: Dict[str, Any], graph_id: str) -> Dict[str, Any]:
    """Standardize a node to match schema.

    Args:
        node: Original node dictionary
        graph_id: Graph identifier

    Returns:
        Standardized node dictionary
    """
    standardized = {}

    # === MANDATORY FIELDS ===
    for field in NODE_SCHEMA['mandatory']:
        if field in node:
            standardized[field] = node[field]
        elif field == 'description':
            # Auto-generate description
            standardized[field] = f"Module {node.get('name', 'unknown')}"
        else:
            standardized[field] = node.get(field, '')

    # === PYTHON MODULE FIELDS ===
    if node.get('type') in ['module', 'test_module', 'example_bot', 'example_module', 'package']:
        for field in NODE_SCHEMA['python_module']:
            if field == 'complexity_score' and field not in node:
                standardized[field] = calculate_complexity(node)
            elif field == 'exports' and field not in node:
                # Auto-generate from classes + functions
                classes = node.get('classes', [])
                functions = node.get('functions', [])
                standardized[field] = classes + functions
            else:
                standardized[field] = node.get(field, [] if field in ['classes', 'functions', 'exports'] else 0)

    # === CODE FILE FIELDS ===
    if node.get('type') not in ['doc', 'documentation', 'config']:
        for field in NODE_SCHEMA['code_file']:
            if field == 'criticality' and field not in node:
                standardized[field] = calculate_criticality(node)
            else:
                standardized[field] = node.get(field, [])

    # === OPTIONAL FIELDS ===
    if 'category' not in node:
        standardized['category'] = determine_category(node)
    elif 'category' in node:
        standardized['category'] = node['category']

    # Copy other optional fields if present
    for field in ['tags', 'language', 'status', 'format']:
        if field in node:
            standardized[field] = node[field]

    # === ARCHIVE GRAPH EXCEPTION ===
    if graph_id == 'archive':
        # Keep archive-specific fields
        for field in NODE_SCHEMA['deprecated_archive_only']:
            if field in node:
                standardized[field] = node[field]

    return standardized


def standardize_graph(graph_file: Path, dry_run: bool = False) -> Tuple[int, List[str]]:
    """Standardize a single graph file.

    Args:
        graph_file: Path to graph JSON file
        dry_run: If True, don't save changes

    Returns:
        Tuple of (nodes_updated, issues)
    """
    with open(graph_file) as f:
        graph = json.load(f)

    graph_id = graph.get('metadata', {}).get('graph_id', graph_file.stem)
    issues = []
    nodes_updated = 0

    # === STANDARDIZE METADATA ===
    metadata = graph.get('metadata', {})

    # Ensure all mandatory fields
    for field in METADATA_SCHEMA['mandatory']:
        if field not in metadata:
            if field == 'generated_at':
                metadata[field] = datetime.now().strftime('%Y-%m-%d')
            elif field == 'node_count':
                metadata[field] = len(graph.get('nodes', []))
            elif field == 'edge_count':
                metadata[field] = len(graph.get('edges', []))
            elif field == 'version':
                metadata[field] = '3.0.0'
            else:
                issues.append(f"Missing mandatory metadata: {field}")

    # Remove deprecated metadata fields
    for field in METADATA_SCHEMA['deprecated']:
        if field in metadata and graph_id != 'project_meta':
            del metadata[field]
            issues.append(f"Removed deprecated metadata: {field}")

    # === STANDARDIZE NODES ===
    if 'nodes' in graph:
        new_nodes = []
        for i, node in enumerate(graph['nodes']):
            standardized = standardize_node(node, graph_id)
            new_nodes.append(standardized)

            # Check if changed
            if set(node.keys()) != set(standardized.keys()):
                nodes_updated += 1

        graph['nodes'] = new_nodes

    # Save if not dry run
    if not dry_run:
        with open(graph_file, 'w') as f:
            json.dump(graph, f, indent=2)
            f.write('\n')

    return nodes_updated, issues


def standardize_all_graphs(dry_run: bool = False) -> None:
    """Standardize all graphs to follow consistent schema.

    Args:
        dry_run: If True, don't save changes
    """
    graph_root = get_graph_root()

    # Find all graphs
    graph_files = []
    for pattern in ['*/graph.json', '*/*-graph.json']:
        graph_files.extend(graph_root.glob(pattern))

    graph_files = [f for f in graph_files if 'router.json' not in f.name]

    print(f"\n🔧 Standardizing {len(graph_files)} graphs")
    if dry_run:
        print("   (DRY RUN - no changes will be saved)")
    print("=" * 70)

    total_updated = 0

    for graph_file in sorted(graph_files):
        rel_path = graph_file.relative_to(graph_root)

        try:
            nodes_updated, issues = standardize_graph(graph_file, dry_run)
            total_updated += nodes_updated

            status = "🔧" if nodes_updated > 0 else "✅"
            print(f"{status} {rel_path.parent.name}/{rel_path.name:30} | {nodes_updated} nodes updated")

            if issues:
                for issue in issues[:3]:
                    print(f"      - {issue}")

        except Exception as e:
            print(f"❌ {rel_path}: Error - {e}")

    print("=" * 70)
    if not dry_run:
        print(f"✅ Standardized {total_updated} nodes across {len(graph_files)} graphs")
    else:
        print(f"🔍 Would update {total_updated} nodes across {len(graph_files)} graphs")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Schema standardization for project graphs"
    )
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Analyze current schema inconsistencies'
    )
    parser.add_argument(
        '--standardize',
        action='store_true',
        help='Standardize all graphs to consistent schema'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    args = parser.parse_args()

    if not any([args.analyze, args.standardize]):
        parser.print_help()
        return

    print("🛠️  Graph Schema Standardizer")
    print("=" * 70)

    if args.analyze:
        results = analyze_all_graphs()

        print(f"\n📋 Summary:")
        print(f"   Total graphs: {results['total_graphs']}")
        print(f"   Metadata fields: {len(results['all_metadata_fields'])}")
        print(f"   Node fields: {len(results['all_node_fields'])}")

        graphs_with_issues = sum(1 for g in results['graphs'].values() if g['issues'])
        print(f"   Graphs with issues: {graphs_with_issues}/{results['total_graphs']}")

    if args.standardize:
        standardize_all_graphs(dry_run=args.dry_run)

    print("\n✅ Complete")


if __name__ == '__main__':
    main()
