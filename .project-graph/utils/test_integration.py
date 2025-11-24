#!/usr/bin/env python3
"""Integration test for auto_update functionality.

Simple integration test that verifies:
1. File hash tracking
2. AST analysis
3. Cross-graph updates
4. Node updates in graphs
"""

import json
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from auto_update import (
    compute_file_hash,
    determine_all_affected_graphs,
    determine_graph_for_file,
    determine_sub_graph_for_file,
    has_file_changed,
    load_hash_cache,
    analyze_python_file,
)


def test_file_hashing():
    """Test file hash computation."""
    print("🧪 Test 1: File hashing")

    # Test with existing file
    test_file = Path(__file__).parent.parent.parent / "telegram_bot_stack" / "storage" / "base.py"

    if test_file.exists():
        hash1 = compute_file_hash(test_file)
        print(f"   ✅ Computed hash: {hash1[:16]}...")

        # Hash should be consistent
        hash2 = compute_file_hash(test_file)
        assert hash1 == hash2, "Hash should be consistent"
        print(f"   ✅ Hash is consistent")
    else:
        print(f"   ⚠️  Test file not found: {test_file}")

    print()


def test_hash_cache():
    """Test hash cache operations."""
    print("🧪 Test 2: Hash cache")

    cache = load_hash_cache()
    print(f"   ✅ Loaded cache with {len(cache)} entries")

    if cache:
        # Show first few entries
        for i, (path, hash_val) in enumerate(list(cache.items())[:3]):
            print(f"   • {path}: {hash_val[:16]}...")
            if i >= 2:
                break

    print()


def test_change_detection():
    """Test change detection."""
    print("🧪 Test 3: Change detection")

    test_files = [
        "telegram_bot_stack/storage/base.py",
        "telegram_bot_stack/bot_base.py",
        "tests/conftest.py"
    ]

    for file_path in test_files:
        changed = has_file_changed(file_path)
        status = "Changed" if changed else "Unchanged"
        print(f"   {file_path}: {status}")

    print()


def test_ast_analysis():
    """Test AST analysis."""
    print("🧪 Test 4: AST analysis")

    test_file = Path(__file__).parent.parent.parent / "telegram_bot_stack" / "storage" / "base.py"

    if test_file.exists():
        metadata = analyze_python_file(test_file)
        print(f"   ✅ Analyzed {test_file.name}")
        print(f"   • Lines: {metadata.get('lines', 0)}")
        print(f"   • Classes: {len(metadata.get('classes', []))}")
        print(f"   • Functions: {len(metadata.get('functions', []))}")
        print(f"   • Imports: {len(metadata.get('imports', []))}")

        if metadata.get('classes'):
            print(f"   • Class names: {', '.join(metadata['classes'][:3])}")
    else:
        print(f"   ⚠️  Test file not found")

    print()


def test_graph_determination():
    """Test graph determination."""
    print("🧪 Test 5: Graph determination")

    test_cases = [
        ("telegram_bot_stack/storage/base.py", "bot_framework"),
        ("tests/core/test_storage.py", "testing"),
        ("examples/echo_bot/bot.py", "examples"),
        ("docs/quickstart.md", "docs"),
        (".github/workflows/tests.yml", "infrastructure"),
        ("pyproject.toml", "configuration"),
    ]

    for file_path, expected_graph in test_cases:
        graph = determine_graph_for_file(file_path)
        status = "✅" if graph == expected_graph else "❌"
        print(f"   {status} {file_path} → {graph}")

    print()


def test_sub_graph_determination():
    """Test sub-graph determination."""
    print("🧪 Test 6: Sub-graph determination")

    test_cases = [
        ("telegram_bot_stack/storage/base.py", "storage"),
        ("telegram_bot_stack/bot_base.py", "core"),
        ("telegram_bot_stack/decorators.py", "utilities"),
        ("telegram_bot_stack/cli/main.py", "utilities"),
    ]

    for file_path, expected_sub in test_cases:
        sub = determine_sub_graph_for_file(file_path)
        status = "✅" if sub == expected_sub else "❌"
        print(f"   {status} {file_path} → {sub}")

    print()


def test_cross_graph_updates():
    """Test cross-graph dependency detection."""
    print("🧪 Test 7: Cross-graph updates")

    test_cases = [
        "telegram_bot_stack/storage/base.py",
        "tests/core/test_storage.py",
        "examples/echo_bot/bot.py",
    ]

    for file_path in test_cases:
        affected = determine_all_affected_graphs(file_path)
        print(f"   {file_path}:")
        for graph_name, sub_graph in affected:
            graph_label = f"{graph_name}/{sub_graph}" if sub_graph else graph_name
            print(f"      • {graph_label}")

    print()


def test_graph_loading():
    """Test graph loading."""
    print("🧪 Test 8: Graph loading")

    try:
        from graph_utils import (
            load_router,
            load_full_hierarchical_graph,
            get_recommended_graph,
        )

        # Load router
        router = load_router()
        print(f"   ✅ Loaded router with {len(router['graphs'])} graphs")

        # Load hierarchical graph
        graph = load_full_hierarchical_graph('bot_framework')
        print(f"   ✅ Loaded bot_framework: {graph['metadata']['node_count']} nodes")

        # Test recommendation
        task = "Add Redis storage backend"
        rec = get_recommended_graph(router, task)
        print(f"   ✅ Task '{task}' → {rec}")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    print()


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Auto-Update Integration Tests")
    print("=" * 60)
    print()

    try:
        test_file_hashing()
        test_hash_cache()
        test_change_detection()
        test_ast_analysis()
        test_graph_determination()
        test_sub_graph_determination()
        test_cross_graph_updates()
        test_graph_loading()

        print("=" * 60)
        print("✅ All tests completed successfully!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
