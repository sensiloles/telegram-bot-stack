#!/usr/bin/env python3
"""Auto-generate graph-router.json from existing graphs.

This module automatically generates the router file by:
- Scanning all graph files in .project-graph
- Extracting metadata from each graph
- Calculating statistics (lines, nodes, edges)
- Preserving semantic fields (when_to_use, typical_queries)

Usage:
    # Generate new router
    python3 router_generator.py --generate

    # Preview what would be generated
    python3 router_generator.py --dry-run

    # Update existing router (preserve semantic fields)
    python3 router_generator.py --update
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))


def get_graph_root() -> Path:
    """Get graph root directory."""
    return Path(__file__).parent.parent


def get_project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).parent.parent.parent


# ============================================================================
# ROUTER SCHEMA
# ============================================================================

ROUTER_SCHEMA = {
    # Top-level metadata
    'metadata': {
        'version': '3.0.0',                    # Router schema version
        'generated_at': 'auto',                # Auto: current date
        'description': 'Router for selecting appropriate dependency graph based on task type',
        'architecture': 'Multi-graph system for efficient AI agent navigation',
    },

    # Per-graph fields
    'graph_fields': {
        # Auto-generated from graph files
        'auto': [
            'id',                   # From graph metadata
            'name',                 # From graph metadata + emoji
            'file',                 # Graph file path
            'description',          # From graph metadata
            'node_count',           # Calculated
            'edge_count',           # Calculated
            'lines',                # JSON file size
            'coverage',             # Directories + stats
        ],

        # Semantic (manual or AI-generated, preserved during updates)
        'semantic': [
            'when_to_use',          # List of scenarios
            'typical_queries',      # List of questions
            'criticality',          # low/medium/high/critical
            'update_frequency',     # low/medium/high
            'complexity',           # low/medium/high
        ],

        # Special fields
        'special': [
            'has_sub_graphs',       # Auto: bool for hierarchical graphs
            'sub_graphs',           # Auto: dict of sub-graph info
            'router_file',          # Auto: path to sub-router
        ],
    }
}


GRAPH_EMOJIS = {
    'bot_framework': '🤖',
    'infrastructure': '🔧',
    'testing': '🧪',
    'examples': '📚',
    'docs': '📖',
    'configuration': '⚙️',
    'archive': '📦',
    'project_meta': '🎯',
}


DECISION_TREE = {
    "understanding_project": {
        "description": "I want to understand the project structure",
        "recommended_graphs": ["project_meta", "bot_framework"],
        "reason": "project_meta provides overview, bot_framework shows core implementation"
    },
    "adding_features": {
        "description": "I want to add new features to the bot",
        "questions": {
            "storage_related": {
                "question": "Is it storage-related (database, persistence)?",
                "yes": ["bot_framework/storage"],
                "no": "next"
            },
            "user_management": {
                "question": "Is it user/admin management related?",
                "yes": ["bot_framework/core"],
                "no": "next"
            },
            "cli_tools": {
                "question": "Is it CLI/developer tools related?",
                "yes": ["bot_framework/cli"],
                "no": ["bot_framework"]
            }
        }
    },
    "fixing_bugs": {
        "description": "I want to fix bugs or issues",
        "questions": {
            "where": {
                "question": "Where is the bug?",
                "ci_cd": ["infrastructure"],
                "tests": ["testing"],
                "framework": ["bot_framework"],
                "examples": ["examples"]
            }
        }
    },
    "writing_tests": {
        "description": "I want to write or fix tests",
        "recommended_graphs": ["testing", "bot_framework"],
        "reason": "testing shows test structure, bot_framework shows what to test"
    },
    "documentation": {
        "description": "I want to update documentation",
        "recommended_graphs": ["docs", "examples"],
        "reason": "docs for guides, examples for code samples"
    },
    "learning_usage": {
        "description": "I want to learn how to use the framework",
        "recommended_graphs": ["examples", "docs"],
        "reason": "examples show practical usage, docs explain concepts"
    }
}


# ============================================================================
# GRAPH SCANNING & ANALYSIS
# ============================================================================

def scan_all_graphs() -> Dict[str, Dict[str, Any]]:
    """Scan all graph files and extract metadata.

    Returns:
        Dictionary mapping graph_id to graph info
    """
    graph_root = get_graph_root()
    graphs = {}

    # Find all graph files
    graph_files = []
    for pattern in ['*/graph.json', '*/*-graph.json']:
        graph_files.extend(graph_root.glob(pattern))

    # Exclude routers
    graph_files = [f for f in graph_files if 'router.json' not in f.name]

    for graph_file in sorted(graph_files):
        try:
            with open(graph_file) as f:
                graph = json.load(f)

            rel_path = graph_file.relative_to(graph_root)
            metadata = graph.get('metadata', {})
            graph_id = metadata.get('graph_id', rel_path.stem)

            # Extract info
            info = {
                'id': graph_id,
                'name': f"{GRAPH_EMOJIS.get(graph_id, '')} {metadata.get('graph_name', graph_id)}".strip(),
                'file': str(rel_path),
                'description': metadata.get('description', ''),
                'node_count': len(graph.get('nodes', [])),
                'edge_count': len(graph.get('edges', [])),
                'lines': sum(1 for _ in open(graph_file)),
                'scope': metadata.get('scope', ''),
            }

            # Check for sub-graphs (hierarchical structure)
            if 'bot-framework' in str(rel_path.parent):
                parent_graph = 'bot_framework'
                sub_graph_name = rel_path.stem.replace('-graph', '').replace('bot-framework-', '')

                if sub_graph_name in ['core', 'storage', 'utilities', 'cli']:
                    info['parent_graph'] = parent_graph
                    info['sub_graph_name'] = sub_graph_name

            graphs[graph_id] = info

        except Exception as e:
            print(f"⚠️  Error scanning {graph_file}: {e}")

    return graphs


def calculate_coverage(graph_id: str) -> Dict[str, Any]:
    """Calculate coverage information for a graph.

    Args:
        graph_id: Graph identifier

    Returns:
        Coverage dictionary
    """
    project_root = get_project_root()

    # Map graph to directories
    directory_map = {
        'bot_framework': ['telegram_bot_stack'],
        'testing': ['tests'],
        'examples': ['examples'],
        'infrastructure': ['.github', 'scripts'],
        'docs': ['docs'],
        'configuration': ['.'],  # Root level config files
        'archive': ['archive'],
        'project_meta': ['.'],
    }

    directories = directory_map.get(graph_id, [])

    coverage = {
        'directories': directories,
        'file_patterns': [f"{d}/**/*.py" for d in directories if d != '.'],
    }

    # Count files and lines
    total_files = 0
    total_lines = 0

    for directory in directories:
        dir_path = project_root / directory
        if not dir_path.exists():
            continue

        if directory == '.':
            # Root level config files
            for ext in ['.toml', '.yaml', '.yml', '.md', '.txt']:
                total_files += len(list(dir_path.glob(f'*{ext}')))
        else:
            # Python files in directory
            py_files = list(dir_path.rglob('*.py'))
            total_files += len(py_files)

            for py_file in py_files:
                try:
                    total_lines += sum(1 for _ in open(py_file))
                except:
                    pass

    if total_files > 0:
        coverage['modules'] = total_files
    if total_lines > 0:
        coverage['lines_of_code'] = total_lines

    return coverage


def group_hierarchical_graphs(graphs: Dict[str, Dict]) -> Dict[str, Dict]:
    """Group sub-graphs under their parent graphs.

    Args:
        graphs: Dictionary of all graphs

    Returns:
        Dictionary with hierarchical structure
    """
    result = {}
    sub_graphs_map = {}

    # First pass: collect sub-graphs
    for graph_id, info in graphs.items():
        if 'parent_graph' in info:
            parent = info['parent_graph']
            sub_name = info['sub_graph_name']

            if parent not in sub_graphs_map:
                sub_graphs_map[parent] = {}

            sub_graphs_map[parent][sub_name] = {
                'name': info['name'].split(maxsplit=1)[-1],  # Remove emoji
                'description': info['description'],
                'file': info['file'],
                'lines': info['lines'],
                'node_count': info['node_count'],
                'edge_count': info['edge_count'],
            }
        else:
            result[graph_id] = info

    # Second pass: add sub-graphs to parents
    for parent, sub_graphs in sub_graphs_map.items():
        if parent in result:
            result[parent]['has_sub_graphs'] = True
            result[parent]['sub_graphs'] = sub_graphs
            result[parent]['router_file'] = f"{parent.replace('_', '-')}/router.json"

    return result


def load_existing_router() -> Optional[Dict]:
    """Load existing router to preserve semantic fields.

    Returns:
        Existing router dictionary or None
    """
    router_path = get_graph_root() / 'graph-router.json'

    if not router_path.exists():
        return None

    try:
        with open(router_path) as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Could not load existing router: {e}")
        return None


def merge_with_existing(new_graphs: Dict, existing_router: Optional[Dict]) -> Dict:
    """Merge new graph data with existing semantic fields.

    Args:
        new_graphs: Newly generated graph data
        existing_router: Existing router (if any)

    Returns:
        Merged graph data
    """
    if not existing_router or 'graphs' not in existing_router:
        return new_graphs

    semantic_fields = ROUTER_SCHEMA['graph_fields']['semantic']

    for graph_id, new_info in new_graphs.items():
        # Find in existing router (key might be different)
        existing_info = None
        for key, info in existing_router['graphs'].items():
            if info.get('id') == graph_id or key == graph_id:
                existing_info = info
                break

        if existing_info:
            # Preserve semantic fields
            for field in semantic_fields:
                if field in existing_info:
                    new_info[field] = existing_info[field]

            # Preserve usage_note if present
            if 'usage_note' in existing_info:
                new_info['usage_note'] = existing_info['usage_note']

    return new_graphs


def generate_router(
    preserve_semantic: bool = True,
    dry_run: bool = False
) -> Dict[str, Any]:
    """Generate router.json from scratch or update existing.

    Args:
        preserve_semantic: If True, preserve semantic fields from existing router
        dry_run: If True, don't save

    Returns:
        Generated router dictionary
    """
    print("\n🔄 Generating Router")
    print("=" * 70)

    # Scan all graphs
    print("📊 Scanning graphs...")
    graphs = scan_all_graphs()
    print(f"   Found {len(graphs)} graphs")

    # Group hierarchical graphs
    print("🔗 Grouping hierarchical graphs...")
    graphs = group_hierarchical_graphs(graphs)
    print(f"   Organized into {len(graphs)} top-level graphs")

    # Add coverage information
    print("📈 Calculating coverage...")
    for graph_id, info in graphs.items():
        info['coverage'] = calculate_coverage(graph_id)

    # Load existing router if preserving semantic fields
    existing_router = None
    if preserve_semantic:
        print("💾 Loading existing router...")
        existing_router = load_existing_router()
        if existing_router:
            print("   Preserving semantic fields from existing router")
            graphs = merge_with_existing(graphs, existing_router)

    # Build router
    router = {
        'version': '3.0.0',
        'generated_at': datetime.now().strftime('%Y-%m-%d'),
        'description': 'Router for selecting appropriate dependency graph based on task type',
        'architecture': 'Multi-graph system for efficient AI agent navigation',
        'metadata': {
            'total_graphs': len(graphs),
            'total_nodes': sum(g.get('node_count', 0) for g in graphs.values()),
            'total_edges': sum(g.get('edge_count', 0) for g in graphs.values()),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        },
        'quick_start': {
            'step_1': 'Read this file (graph-router.json) - ~150 lines',
            'step_2': "Identify your task type using 'decision_tree'",
            'step_3': "Load ONLY the relevant graph(s) from 'graphs' section",
            'step_4': 'Work with focused graph instead of reading everything',
            'benefit': 'Read 200-400 lines instead of 2000+ lines (80-90% token savings)'
        },
        'decision_tree': DECISION_TREE,
        'graphs': {}
    }

    # Add graphs (use original key format for backwards compatibility)
    for graph_id, info in sorted(graphs.items()):
        key = graph_id.replace('_', '-')  # bot_framework -> bot-framework
        router['graphs'][key] = info

    # Report
    print("\n📋 Generated Router Statistics:")
    print(f"   Total graphs: {router['metadata']['total_graphs']}")
    print(f"   Total nodes: {router['metadata']['total_nodes']}")
    print(f"   Total edges: {router['metadata']['total_edges']}")

    # Save if not dry run
    if not dry_run:
        router_path = get_graph_root() / 'graph-router.json'
        with open(router_path, 'w') as f:
            json.dump(router, f, indent=2, ensure_ascii=False)
            f.write('\n')
        print(f"\n✅ Saved to: {router_path}")
    else:
        print("\n🔍 DRY RUN - Router not saved")

    print("=" * 70)

    return router


def validate_router(router: Dict) -> List[str]:
    """Validate router structure.

    Args:
        router: Router dictionary

    Returns:
        List of validation errors
    """
    errors = []

    # Check required top-level fields
    required = ['version', 'generated_at', 'description', 'graphs']
    for field in required:
        if field not in router:
            errors.append(f"Missing required field: {field}")

    # Check each graph
    if 'graphs' in router:
        for key, graph in router['graphs'].items():
            # Required fields per graph
            graph_required = ['id', 'name', 'file', 'description']
            for field in graph_required:
                if field not in graph:
                    errors.append(f"Graph '{key}' missing field: {field}")

            # Check file exists
            if 'file' in graph:
                graph_file = get_graph_root() / graph['file']
                if not graph_file.exists():
                    errors.append(f"Graph file not found: {graph['file']}")

    return errors


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Auto-generate graph-router.json"
    )
    parser.add_argument(
        '--generate',
        action='store_true',
        help='Generate new router from scratch'
    )
    parser.add_argument(
        '--update',
        action='store_true',
        help='Update router (preserve semantic fields)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be generated without saving'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate existing router'
    )

    args = parser.parse_args()

    if not any([args.generate, args.update, args.validate]):
        parser.print_help()
        return

    print("🛠️  Router Generator")
    print("=" * 70)

    if args.validate:
        router_path = get_graph_root() / 'graph-router.json'
        if not router_path.exists():
            print("❌ Router not found")
            return

        with open(router_path) as f:
            router = json.load(f)

        errors = validate_router(router)

        if errors:
            print("❌ Validation errors:")
            for error in errors:
                print(f"   - {error}")
        else:
            print("✅ Router is valid")

    if args.generate or args.update:
        preserve = args.update or args.generate
        router = generate_router(
            preserve_semantic=preserve,
            dry_run=args.dry_run
        )

        # Validate generated router
        if not args.dry_run:
            errors = validate_router(router)
            if errors:
                print("\n⚠️  Generated router has validation errors:")
                for error in errors:
                    print(f"   - {error}")

    print("\n✅ Complete")


if __name__ == '__main__':
    main()
