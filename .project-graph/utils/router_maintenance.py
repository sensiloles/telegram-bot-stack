#!/usr/bin/env python3
"""Router maintenance utilities.

This module provides tools for maintaining graph-router.json,
including validation of when_to_use and typical_queries fields.

Usage:
    python3 router_maintenance.py --check-completeness
    python3 router_maintenance.py --suggest-queries
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))


def get_graph_root() -> Path:
    """Get graph root directory."""
    return Path(__file__).parent.parent


def load_router() -> Dict[str, Any]:
    """Load router file."""
    router_path = get_graph_root() / "graph-router.json"
    with open(router_path) as f:
        return json.load(f)


def save_router(router: Dict[str, Any]) -> None:
    """Save router file."""
    router_path = get_graph_root() / "graph-router.json"
    with open(router_path, 'w') as f:
        json.dump(router, f, indent=2)
        f.write('\n')


def check_completeness() -> Dict[str, List[str]]:
    """Check if all graphs have when_to_use and typical_queries.

    Returns:
        Dictionary mapping graph ID to list of missing fields
    """
    router = load_router()
    issues = {}

    print("\n🔍 Checking Router Completeness")
    print("=" * 60)

    for graph_key, graph_info in router['graphs'].items():
        graph_id = graph_info['id']
        missing = []

        # Check when_to_use
        when_to_use = graph_info.get('when_to_use', [])
        if not when_to_use:
            missing.append('when_to_use is empty')
        elif len(when_to_use) < 3:
            missing.append(f'when_to_use has only {len(when_to_use)} items (recommend 5-8)')

        # Check typical_queries
        typical_queries = graph_info.get('typical_queries', [])
        if not typical_queries:
            missing.append('typical_queries is empty')
        elif len(typical_queries) < 3:
            missing.append(f'typical_queries has only {len(typical_queries)} items (recommend 5-10)')

        # Report
        if missing:
            print(f"\n⚠️  {graph_id}")
            for issue in missing:
                print(f"   - {issue}")
            issues[graph_id] = missing
        else:
            print(f"✅ {graph_id}: Complete")

    print("\n" + "=" * 60)
    if issues:
        print(f"⚠️  Found issues in {len(issues)} graph(s)")
    else:
        print("✅ All graphs have complete metadata!")
    print("=" * 60)

    return issues


def suggest_queries_for_graph(graph_id: str, graph_info: Dict) -> Dict[str, List[str]]:
    """Suggest when_to_use and typical_queries based on graph content.

    Args:
        graph_id: Graph identifier
        graph_info: Graph metadata from router

    Returns:
        Dictionary with suggested 'when_to_use' and 'typical_queries'
    """
    suggestions = {
        'when_to_use': [],
        'typical_queries': []
    }

    description = graph_info.get('description', '').lower()
    name = graph_info.get('name', '').lower()

    # Generate suggestions based on graph type
    if 'testing' in graph_id or 'test' in description:
        suggestions['when_to_use'] = [
            "Writing new tests",
            "Understanding test structure",
            "Fixing failing tests",
            "Adding test fixtures",
            "Improving test coverage",
            "Debugging test failures"
        ]
        suggestions['typical_queries'] = [
            "How to write a test for X?",
            "Where are test fixtures defined?",
            "How to run specific tests?",
            "What is the test structure?",
            "How to mock dependencies?",
            "How to add integration tests?"
        ]

    elif 'infrastructure' in graph_id or 'ci' in description or 'workflow' in description:
        suggestions['when_to_use'] = [
            "Fixing CI/CD workflows",
            "Understanding automation scripts",
            "Modifying GitHub Actions",
            "Adding new automation",
            "Debugging workflow failures",
            "Understanding release process"
        ]
        suggestions['typical_queries'] = [
            "How does the release workflow work?",
            "Where are automation scripts?",
            "How to add a new workflow?",
            "What scripts handle PR creation?",
            "How to modify CI checks?",
            "How does semantic release work?"
        ]

    elif 'example' in graph_id or 'example' in description:
        suggestions['when_to_use'] = [
            "Learning framework usage",
            "Understanding bot patterns",
            "Finding code examples",
            "Starting new bot project",
            "Seeing feature demonstrations"
        ]
        suggestions['typical_queries'] = [
            "How to build a simple bot?",
            "What are example bots available?",
            "How to use storage in a bot?",
            "How to implement X feature?",
            "What bot patterns are recommended?"
        ]

    elif 'doc' in graph_id or 'documentation' in description:
        suggestions['when_to_use'] = [
            "Updating documentation",
            "Finding documentation gaps",
            "Understanding API reference",
            "Writing user guides",
            "Improving documentation"
        ]
        suggestions['typical_queries'] = [
            "Where is X documented?",
            "How to update documentation?",
            "What documentation exists?",
            "Where is the API reference?",
            "How to add new documentation?"
        ]

    elif 'config' in graph_id or 'configuration' in description:
        suggestions['when_to_use'] = [
            "Modifying build configuration",
            "Changing dependencies",
            "Updating project settings",
            "Understanding build system",
            "Configuring development tools"
        ]
        suggestions['typical_queries'] = [
            "Where are dependencies defined?",
            "How to add a new dependency?",
            "What is the build configuration?",
            "How to modify pyproject.toml?",
            "What tools are configured?"
        ]

    elif 'archive' in graph_id:
        suggestions['when_to_use'] = [
            "Understanding project history",
            "Finding deprecated features",
            "Learning about past decisions",
            "Accessing historical documentation"
        ]
        suggestions['typical_queries'] = [
            "What was the original architecture?",
            "Why was X deprecated?",
            "What was the old implementation?",
            "What features were removed?"
        ]

    else:
        # Generic suggestions based on description
        suggestions['when_to_use'] = [
            f"Working with {name}",
            f"Understanding {name} structure",
            f"Modifying {name} components"
        ]
        suggestions['typical_queries'] = [
            f"How does {name} work?",
            f"Where is X in {name}?",
            f"How to modify {name}?"
        ]

    return suggestions


def generate_suggestions() -> None:
    """Generate suggestions for all graphs with incomplete metadata."""
    router = load_router()

    print("\n💡 Generating Suggestions")
    print("=" * 60)

    for graph_key, graph_info in router['graphs'].items():
        graph_id = graph_info['id']

        when_to_use = graph_info.get('when_to_use', [])
        typical_queries = graph_info.get('typical_queries', [])

        # Only suggest if incomplete
        if len(when_to_use) < 3 or len(typical_queries) < 3:
            print(f"\n📊 {graph_id}")

            suggestions = suggest_queries_for_graph(graph_id, graph_info)

            if len(when_to_use) < 3:
                print("\n   💡 Suggested when_to_use:")
                for item in suggestions['when_to_use']:
                    print(f"      - {item}")

            if len(typical_queries) < 3:
                print("\n   💡 Suggested typical_queries:")
                for item in suggestions['typical_queries']:
                    print(f"      - {item}")

    print("\n" + "=" * 60)
    print("Copy these suggestions to graph-router.json")
    print("=" * 60)


def validate_router_structure() -> List[str]:
    """Validate overall router structure.

    Returns:
        List of validation errors
    """
    router = load_router()
    errors = []

    print("\n🔍 Validating Router Structure")
    print("=" * 60)

    # Check required top-level fields
    required_fields = ['metadata', 'graphs']
    for field in required_fields:
        if field not in router:
            errors.append(f"Missing required field: {field}")

    # Check metadata
    if 'metadata' in router:
        meta_required = ['version', 'description', 'last_updated']
        for field in meta_required:
            if field not in router['metadata']:
                errors.append(f"Missing metadata field: {field}")

    # Check each graph
    if 'graphs' in router:
        for graph_key, graph_info in router['graphs'].items():
            # Required fields per graph
            graph_required = ['id', 'name', 'description', 'file']
            for field in graph_required:
                if field not in graph_info:
                    errors.append(f"Graph '{graph_key}' missing field: {field}")

            # Check file exists
            if 'file' in graph_info:
                graph_file = get_graph_root() / graph_info['file']
                if not graph_file.exists():
                    errors.append(f"Graph file not found: {graph_info['file']}")

    # Report
    if errors:
        print("❌ Found validation errors:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("✅ Router structure is valid!")

    print("=" * 60)

    return errors


def extract_keywords_from_graphs() -> Dict[str, Set[str]]:
    """Extract keywords from actual graph content to suggest queries.

    Returns:
        Dictionary mapping graph_id to set of keywords
    """
    router = load_router()
    keywords = {}

    print("\n📊 Extracting Keywords from Graphs")
    print("=" * 60)

    for graph_key, graph_info in router['graphs'].items():
        graph_id = graph_info['id']
        graph_file = get_graph_root() / graph_info['file']

        if not graph_file.exists():
            continue

        try:
            with open(graph_file) as f:
                graph = json.load(f)

            graph_keywords = set()

            # Extract from nodes
            for node in graph.get('nodes', []):
                # Class names
                for cls in node.get('classes', []):
                    graph_keywords.add(cls)

                # Function names (filter out common ones)
                for func in node.get('functions', []):
                    if func not in ['main', 'run', 'init', 'setup']:
                        graph_keywords.add(func)

            keywords[graph_id] = graph_keywords
            print(f"   {graph_id}: {len(graph_keywords)} keywords")

        except Exception as e:
            print(f"   ⚠️  {graph_id}: Error - {e}")

    print("=" * 60)

    return keywords


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Router maintenance utilities"
    )
    parser.add_argument(
        '--check-completeness',
        action='store_true',
        help='Check if all graphs have complete metadata'
    )
    parser.add_argument(
        '--suggest',
        action='store_true',
        help='Generate suggestions for incomplete graphs'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate router structure'
    )
    parser.add_argument(
        '--extract-keywords',
        action='store_true',
        help='Extract keywords from graphs'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all checks'
    )

    args = parser.parse_args()

    if not any([
        args.check_completeness,
        args.suggest,
        args.validate,
        args.extract_keywords,
        args.all
    ]):
        parser.print_help()
        return

    print("🛠️  Router Maintenance")
    print("=" * 60)

    if args.all or args.validate:
        validate_router_structure()

    if args.all or args.check_completeness:
        check_completeness()

    if args.all or args.suggest:
        generate_suggestions()

    if args.all or args.extract_keywords:
        extract_keywords_from_graphs()

    print("\n✅ Router maintenance complete")


if __name__ == '__main__':
    main()
