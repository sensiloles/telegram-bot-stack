"""Examples of using the dependency graph utilities.

This file demonstrates common use cases for querying and analyzing
the project dependency graph.
"""

from graph_utils import (
    calculate_coupling_score,
    find_bottlenecks,
    find_node,
    find_nodes_by_category,
    find_nodes_by_tag,
    get_impact_analysis,
    load_graph,
    print_impact_analysis,
    validate_graph,
)


def example_1_basic_queries():
    """Example 1: Basic graph queries."""
    print("=" * 60)
    print("Example 1: Basic Graph Queries")
    print("=" * 60)

    graph = load_graph()

    # Find a specific module
    bot_base = find_node(graph, "telegram_bot_stack.bot_base")
    print(f"\n📦 Found module: {bot_base['name']}")
    print(f"   Description: {bot_base['description']}")
    print(f"   Complexity: {bot_base['complexity_score']}/10")

    # Find all core modules
    print("\n🔵 Core modules:")
    core_modules = find_nodes_by_category(graph, "core")
    for mod in core_modules:
        print(f"   • {mod['name']}: {mod['description']}")

    # Find all testing-related modules
    print("\n🧪 Testing modules:")
    test_modules = find_nodes_by_tag(graph, "testing")
    for mod in test_modules:
        print(f"   • {mod['name']}")


def example_2_impact_analysis():
    """Example 2: Impact analysis for changes."""
    print("\n" + "=" * 60)
    print("Example 2: Impact Analysis")
    print("=" * 60)

    graph = load_graph()

    # Scenario: You want to change StorageBackend interface
    print("\n📝 Scenario: Changing StorageBackend interface")
    print_impact_analysis(graph, "telegram_bot_stack.storage.base")

    # Scenario: You want to refactor BotBase
    print("\n📝 Scenario: Refactoring BotBase")
    analysis = get_impact_analysis(graph, "telegram_bot_stack.bot_base")
    print(f"Total modules affected: {analysis['total_impact']}")
    print(f"Recommendation: {analysis['recommendation']}")


def example_3_find_bottlenecks():
    """Example 3: Find architectural bottlenecks."""
    print("\n" + "=" * 60)
    print("Example 3: Find Bottlenecks")
    print("=" * 60)

    graph = load_graph()

    # Find modules with many dependents
    bottlenecks = find_bottlenecks(graph, threshold=2)
    print("\n🔥 Modules with 2+ dependents (potential bottlenecks):")
    for mod_id, count in sorted(bottlenecks, key=lambda x: x[1], reverse=True):
        node = find_node(graph, mod_id)
        print(f"   • {node['name']}: {count} dependents")
        print(f"     Criticality: {node.get('criticality', 'N/A')}")
        print(f"     Role: {node.get('role', 'N/A')}")


def example_4_find_extension_points():
    """Example 4: Find where to add new features."""
    print("\n" + "=" * 60)
    print("Example 4: Find Extension Points")
    print("=" * 60)

    graph = load_graph()

    # Find abstract/interface modules (good extension points)
    abstract_modules = find_nodes_by_tag(graph, "abstract")
    print("\n🎯 Abstract modules (implement these to extend):")
    for mod in abstract_modules:
        print(f"   • {mod['name']}: {mod['description']}")

    # Find extensible modules
    extensible = find_nodes_by_tag(graph, "extensible")
    print("\n🔌 Extensible modules (override hooks):")
    for mod in extensible:
        print(f"   • {mod['name']}")
        if mod.get("classes"):
            for cls in mod["classes"]:
                if cls.get("hooks"):
                    print(f"     Hooks: {', '.join(cls['hooks'])}")


def example_5_coupling_analysis():
    """Example 5: Analyze module coupling."""
    print("\n" + "=" * 60)
    print("Example 5: Coupling Analysis")
    print("=" * 60)

    graph = load_graph()

    # Calculate coupling for all modules
    print("\n📊 Coupling scores (higher = more coupled):")
    coupling_scores = []
    for node in graph["nodes"]:
        score = calculate_coupling_score(graph, node["id"])
        coupling_scores.append((node["name"], score))

    # Sort by coupling score
    for name, score in sorted(coupling_scores, key=lambda x: x[1], reverse=True):
        print(f"   • {name}: {score}")


def example_6_design_patterns():
    """Example 6: Explore design patterns used."""
    print("\n" + "=" * 60)
    print("Example 6: Design Patterns")
    print("=" * 60)

    graph = load_graph()

    patterns = graph.get("design_patterns", {}).get("patterns_used", [])
    print(f"\n🎨 Design patterns used ({len(patterns)}):")
    for pattern in patterns:
        print(f"\n   • {pattern['name']}")
        print(f"     Description: {pattern['description']}")
        print(
            f"     Participants: {', '.join([p.split('.')[-1] for p in pattern['participants']])}"
        )
        print(f"     Benefit: {pattern['benefit']}")


def example_7_ai_agent_workflow():
    """Example 7: AI Agent workflow for understanding codebase."""
    print("\n" + "=" * 60)
    print("Example 7: AI Agent Workflow")
    print("=" * 60)

    graph = load_graph()

    # Step 1: Get reading order
    hints = graph.get("ai_agent_hints", {})
    reading_order = hints.get("code_reading_order", [])
    print("\n📚 Recommended reading order for new AI agents:")
    for i, step in enumerate(reading_order, 1):
        print(f"   {i}. {step}")

    # Step 2: Navigation tips
    print("\n💡 Navigation tips:")
    for tip in hints.get("navigation_tips", [])[:5]:
        print(f"   • {tip}")

    # Step 3: Common tasks
    print("\n🎯 Common tasks:")
    tasks = hints.get("common_tasks", [])
    for task in tasks[:3]:
        if isinstance(task, dict):
            print(f"   • {task['task']}")
            print(f"     Location: {task['location']}")


def example_8_validate_graph():
    """Example 8: Validate graph integrity."""
    print("\n" + "=" * 60)
    print("Example 8: Graph Validation")
    print("=" * 60)

    graph = load_graph()

    errors = validate_graph(graph)
    if errors:
        print("\n❌ Validation errors found:")
        for error in errors:
            print(f"   • {error}")
    else:
        print("\n✅ Graph is valid!")

    # Show statistics
    stats = graph.get("statistics", {})
    print("\n📊 Graph statistics:")
    print(f"   Total modules: {stats.get('total_modules', 'N/A')}")
    print(f"   Total classes: {stats.get('total_classes', 'N/A')}")
    print(f"   Lines of code: {stats.get('total_lines_of_code', 'N/A')}")
    print(
        f"   Avg dependencies: {stats.get('average_dependencies_per_module', 'N/A'):.2f}"
    )
    print(f"   Circular dependencies: {stats.get('circular_dependencies', 'N/A')}")


def example_9_layer_analysis():
    """Example 9: Analyze architectural layers."""
    print("\n" + "=" * 60)
    print("Example 9: Layer Analysis")
    print("=" * 60)

    graph = load_graph()

    layers_info = graph.get("layers", {})
    layers = layers_info.get("layers", [])

    print(f"\n🏗️  Architectural layers ({len(layers)}):")
    for layer in sorted(layers, key=lambda x: x["level"]):
        print(f"\n   Level {layer['level']}: {layer['name']}")
        print(f"   Purpose: {layer['purpose']}")
        print(f"   Visibility: {layer['visibility']}")
        print(f"   Modules ({len(layer['modules'])}):")
        for mod_id in layer["modules"]:
            mod_name = mod_id.split(".")[-1]
            print(f"     • {mod_name}")


def example_10_usage_scenarios():
    """Example 10: Find usage scenarios."""
    print("\n" + "=" * 60)
    print("Example 10: Usage Scenarios")
    print("=" * 60)

    graph = load_graph()

    scenarios = graph.get("usage_scenarios", {}).get("scenarios", [])
    print(f"\n📖 Common usage scenarios ({len(scenarios)}):")

    for scenario in scenarios:
        print(f"\n   {scenario['name']}")
        print("   Flow:")
        for i, step in enumerate(scenario["flow"], 1):
            print(f"     {i}. {step}")


# Run all examples
if __name__ == "__main__":
    print("\n🔗 DEPENDENCY GRAPH EXAMPLES")
    print("=" * 60)
    print("This script demonstrates various ways to use the dependency graph.\n")

    try:
        example_1_basic_queries()
        example_2_impact_analysis()
        example_3_find_bottlenecks()
        example_4_find_extension_points()
        example_5_coupling_analysis()
        example_6_design_patterns()
        example_7_ai_agent_workflow()
        example_8_validate_graph()
        example_9_layer_analysis()
        example_10_usage_scenarios()

        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback

        traceback.print_exc()
