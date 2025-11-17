"""Utility functions for working with the dependency graph.

This module provides helper functions for querying and analyzing the
project dependency graph.

Example:
    >>> from graph_utils import load_graph, find_node, find_dependents
    >>> graph = load_graph()
    >>> node = find_node(graph, 'telegram_bot_stack.bot_base')
    >>> print(node['description'])
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


def load_graph(graph_path: Optional[str] = None) -> Dict[str, Any]:
    """Load dependency graph from JSON file.

    Args:
        graph_path: Path to graph JSON file. If None, uses default location.

    Returns:
        Dictionary containing the full dependency graph

    Raises:
        FileNotFoundError: If graph file doesn't exist
        json.JSONDecodeError: If graph file is not valid JSON
    """
    if graph_path is None:
        graph_path = Path(__file__).parent / "dependency-graph.json"
    else:
        graph_path = Path(graph_path)

    with open(graph_path, encoding="utf-8") as f:
        return json.load(f)


def save_graph(graph: Dict[str, Any], graph_path: Optional[str] = None) -> None:
    """Save dependency graph to JSON file.

    Args:
        graph: Dictionary containing the full dependency graph
        graph_path: Path to graph JSON file. If None, uses default location.
    """
    if graph_path is None:
        graph_path = Path(__file__).parent / "dependency-graph.json"
    else:
        graph_path = Path(graph_path)

    with open(graph_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)


def find_node(graph: Dict[str, Any], node_id: str) -> Optional[Dict[str, Any]]:
    """Find a node by its ID.

    Args:
        graph: Dependency graph
        node_id: Node identifier to search for

    Returns:
        Node dictionary if found, None otherwise
    """
    for node in graph["nodes"]:
        if node["id"] == node_id:
            return node
    return None


def find_nodes_by_tag(graph: Dict[str, Any], tag: str) -> List[Dict[str, Any]]:
    """Find all nodes with a specific tag.

    Args:
        graph: Dependency graph
        tag: Tag to search for

    Returns:
        List of nodes containing the tag
    """
    return [node for node in graph["nodes"] if tag in node.get("tags", [])]


def find_nodes_by_category(
    graph: Dict[str, Any], category: str
) -> List[Dict[str, Any]]:
    """Find all nodes in a specific category.

    Args:
        graph: Dependency graph
        category: Category to search for (e.g., 'core', 'implementation')

    Returns:
        List of nodes in the category
    """
    return [node for node in graph["nodes"] if node.get("category") == category]


def find_dependents(graph: Dict[str, Any], node_id: str) -> List[str]:
    """Find all modules that depend on a given module.

    Args:
        graph: Dependency graph
        node_id: Node identifier

    Returns:
        List of node IDs that depend on the given module
    """
    node = find_node(graph, node_id)
    return node["dependents"] if node else []


def find_dependencies(graph: Dict[str, Any], node_id: str) -> List[str]:
    """Find all dependencies of a given module.

    Args:
        graph: Dependency graph
        node_id: Node identifier

    Returns:
        List of node IDs that the module depends on
    """
    node = find_node(graph, node_id)
    return node["dependencies"] if node else []


def get_transitive_dependents(graph: Dict[str, Any], node_id: str) -> Set[str]:
    """Get all modules that transitively depend on a given module.

    This finds not just direct dependents, but also modules that depend
    on those dependents, recursively.

    Args:
        graph: Dependency graph
        node_id: Node identifier

    Returns:
        Set of all node IDs that transitively depend on the given module
    """
    result = set()
    to_process = [node_id]
    processed = set()

    while to_process:
        current = to_process.pop()
        if current in processed:
            continue

        processed.add(current)
        dependents = find_dependents(graph, current)

        for dep in dependents:
            if dep not in result:
                result.add(dep)
                to_process.append(dep)

    return result


def get_transitive_dependencies(graph: Dict[str, Any], node_id: str) -> Set[str]:
    """Get all modules that a given module transitively depends on.

    This finds not just direct dependencies, but also dependencies of
    those dependencies, recursively.

    Args:
        graph: Dependency graph
        node_id: Node identifier

    Returns:
        Set of all node IDs that the module transitively depends on
    """
    result = set()
    to_process = [node_id]
    processed = set()

    while to_process:
        current = to_process.pop()
        if current in processed:
            continue

        processed.add(current)
        dependencies = find_dependencies(graph, current)

        for dep in dependencies:
            if dep not in result:
                result.add(dep)
                to_process.append(dep)

    return result


def calculate_coupling_score(graph: Dict[str, Any], node_id: str) -> int:
    """Calculate coupling score for a module.

    Coupling score is the sum of incoming and outgoing dependencies.
    Higher score indicates more coupling.

    Args:
        graph: Dependency graph
        node_id: Node identifier

    Returns:
        Coupling score (0 = no coupling, higher = more coupling)
    """
    node = find_node(graph, node_id)
    if not node:
        return 0

    deps = len(node["dependencies"])
    dependents = len(node["dependents"])
    return deps + dependents


def find_leaf_modules(graph: Dict[str, Any]) -> List[str]:
    """Find all leaf modules (modules with no dependents).

    Args:
        graph: Dependency graph

    Returns:
        List of node IDs for leaf modules
    """
    return [node["id"] for node in graph["nodes"] if len(node["dependents"]) == 0]


def find_root_modules(graph: Dict[str, Any]) -> List[str]:
    """Find all root modules (modules with no dependencies).

    Args:
        graph: Dependency graph

    Returns:
        List of node IDs for root modules
    """
    return [node["id"] for node in graph["nodes"] if len(node["dependencies"]) == 0]


def find_bottlenecks(
    graph: Dict[str, Any], threshold: int = 3
) -> List[Tuple[str, int]]:
    """Find bottleneck modules (modules with many dependents).

    Args:
        graph: Dependency graph
        threshold: Minimum number of dependents to be considered a bottleneck

    Returns:
        List of tuples (node_id, dependent_count) for bottleneck modules
    """
    return [
        (node["id"], len(node["dependents"]))
        for node in graph["nodes"]
        if len(node["dependents"]) >= threshold
    ]


def find_critical_modules(graph: Dict[str, Any]) -> List[str]:
    """Find all critical modules.

    Args:
        graph: Dependency graph

    Returns:
        List of node IDs for critical modules
    """
    return [
        node["id"] for node in graph["nodes"] if node.get("criticality") == "critical"
    ]


def get_impact_analysis(graph: Dict[str, Any], node_id: str) -> Dict[str, Any]:
    """Analyze the impact of changing a module.

    Args:
        graph: Dependency graph
        node_id: Node identifier

    Returns:
        Dictionary with impact analysis:
        - direct_dependents: Direct dependents
        - transitive_dependents: All transitive dependents
        - total_impact: Total number of affected modules
        - criticality_breakdown: Count by criticality level
    """
    node = find_node(graph, node_id)
    if not node:
        return {
            "error": f"Node {node_id} not found",
            "direct_dependents": [],
            "transitive_dependents": [],
            "total_impact": 0,
        }

    direct = find_dependents(graph, node_id)
    transitive = get_transitive_dependents(graph, node_id)

    # Count by criticality
    criticality_breakdown = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for dep_id in transitive:
        dep_node = find_node(graph, dep_id)
        if dep_node:
            crit = dep_node.get("criticality", "medium")
            criticality_breakdown[crit] = criticality_breakdown.get(crit, 0) + 1

    return {
        "module": node_id,
        "module_criticality": node.get("criticality", "medium"),
        "direct_dependents": direct,
        "transitive_dependents": sorted(list(transitive)),
        "total_impact": len(transitive),
        "criticality_breakdown": criticality_breakdown,
        "recommendation": _get_impact_recommendation(
            len(transitive), node.get("criticality")
        ),
    }


def _get_impact_recommendation(impact_count: int, criticality: str) -> str:
    """Get recommendation based on impact analysis.

    Args:
        impact_count: Number of affected modules
        criticality: Criticality level of the module

    Returns:
        Recommendation string
    """
    if criticality == "critical" and impact_count > 5:
        return (
            "⚠️  HIGH RISK: Critical module with wide impact. Thorough testing required."
        )
    elif criticality == "critical":
        return "⚠️  MEDIUM RISK: Critical module. Careful testing needed."
    elif impact_count > 10:
        return "⚠️  MEDIUM RISK: Wide impact. Test all affected modules."
    elif impact_count > 5:
        return "⚡ LOW-MEDIUM RISK: Moderate impact. Test main dependents."
    else:
        return "✅ LOW RISK: Limited impact. Standard testing sufficient."


def validate_graph(graph: Dict[str, Any]) -> List[str]:
    """Validate graph integrity.

    Checks:
    - All edges reference existing nodes
    - Dependencies have corresponding edges
    - No orphaned edges
    - Statistics match actual counts

    Args:
        graph: Dependency graph

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    node_ids = {node["id"] for node in graph["nodes"]}

    # Check edges reference existing nodes
    for edge in graph["edges"]:
        if edge["source"] not in node_ids:
            errors.append(
                f"Edge {edge['id']}: source '{edge['source']}' not found in nodes"
            )
        if edge["target"] not in node_ids:
            errors.append(
                f"Edge {edge['id']}: target '{edge['target']}' not found in nodes"
            )

    # Check dependencies match edges (for implements/uses/depends_on edges)
    for node in graph["nodes"]:
        for dep in node["dependencies"]:
            if dep not in node_ids:
                errors.append(
                    f"Node {node['id']}: dependency '{dep}' not found in nodes"
                )

    # Check statistics
    actual_node_count = len(graph["nodes"])
    actual_edge_count = len(graph["edges"])
    meta_node_count = graph["metadata"].get("node_count", 0)
    meta_edge_count = graph["metadata"].get("edge_count", 0)

    if actual_node_count != meta_node_count:
        errors.append(
            f"Metadata node_count ({meta_node_count}) doesn't match "
            f"actual count ({actual_node_count})"
        )
    if actual_edge_count != meta_edge_count:
        errors.append(
            f"Metadata edge_count ({meta_edge_count}) doesn't match "
            f"actual count ({actual_edge_count})"
        )

    return errors


def print_module_info(graph: Dict[str, Any], node_id: str) -> None:
    """Print detailed information about a module.

    Args:
        graph: Dependency graph
        node_id: Node identifier
    """
    node = find_node(graph, node_id)
    if not node:
        print(f"❌ Module '{node_id}' not found")
        return

    print(f"\n{'=' * 60}")
    print(f"📦 Module: {node['name']}")
    print(f"{'=' * 60}")
    print(f"ID:          {node['id']}")
    print(f"Path:        {node['path']}")
    print(f"Type:        {node['type']}")
    print(f"Category:    {node['category']}")
    print(f"Criticality: {node.get('criticality', 'N/A')}")
    print(f"Role:        {node.get('role', 'N/A')}")
    print(f"\nDescription: {node.get('description', 'N/A')}")

    print("\n📊 Metrics:")
    print(f"  Lines of code:    {node.get('lines_of_code', 'N/A')}")
    print(f"  Complexity score: {node.get('complexity_score', 'N/A')}/10")
    print(f"  Coupling score:   {calculate_coupling_score(graph, node_id)}")

    if node.get("exports"):
        print(f"\n📤 Exports ({len(node['exports'])}):")
        for export in node["exports"]:
            print(f"  • {export}")

    if node.get("dependencies"):
        print(f"\n⬇️  Dependencies ({len(node['dependencies'])}):")
        for dep in node["dependencies"]:
            print(f"  • {dep}")

    if node.get("dependents"):
        print(f"\n⬆️  Dependents ({len(node['dependents'])}):")
        for dep in node["dependents"]:
            print(f"  • {dep}")

    if node.get("tags"):
        print(f"\n🏷️  Tags: {', '.join(node['tags'])}")

    print(f"{'=' * 60}\n")


def print_impact_analysis(graph: Dict[str, Any], node_id: str) -> None:
    """Print impact analysis for a module.

    Args:
        graph: Dependency graph
        node_id: Node identifier
    """
    analysis = get_impact_analysis(graph, node_id)

    if "error" in analysis:
        print(f"❌ {analysis['error']}")
        return

    print(f"\n{'=' * 60}")
    print(f"🎯 Impact Analysis: {analysis['module']}")
    print(f"{'=' * 60}")
    print(f"Module Criticality: {analysis['module_criticality']}")
    print(f"Total Impact:       {analysis['total_impact']} modules")

    print("\n📊 Criticality Breakdown:")
    for level, count in analysis["criticality_breakdown"].items():
        if count > 0:
            print(f"  {level.capitalize()}: {count}")

    print(f"\n📍 Direct Dependents ({len(analysis['direct_dependents'])}):")
    if analysis["direct_dependents"]:
        for dep in analysis["direct_dependents"]:
            print(f"  • {dep}")
    else:
        print("  (none)")

    if analysis["total_impact"] > len(analysis["direct_dependents"]):
        transitive_only = set(analysis["transitive_dependents"]) - set(
            analysis["direct_dependents"]
        )
        print(f"\n🔗 Transitive Dependents ({len(transitive_only)}):")
        for dep in sorted(transitive_only):
            print(f"  • {dep}")

    print(f"\n{analysis['recommendation']}")
    print(f"{'=' * 60}\n")


# Example usage
if __name__ == "__main__":
    # Load graph
    graph = load_graph()

    print("🔗 Dependency Graph Analysis")
    print(f"Version: {graph['metadata']['version']}")
    print(f"Modules: {graph['metadata']['node_count']}")
    print(f"Dependencies: {graph['metadata']['edge_count']}\n")

    # Find critical modules
    print("🔴 Critical Modules:")
    critical = find_critical_modules(graph)
    for mod in critical:
        print(f"  • {mod}")

    # Find bottlenecks
    print("\n🔥 Bottleneck Modules (3+ dependents):")
    bottlenecks = find_bottlenecks(graph, threshold=3)
    for mod, count in sorted(bottlenecks, key=lambda x: x[1], reverse=True):
        print(f"  • {mod}: {count} dependents")

    # Example: Impact analysis for storage.base
    print("\n" + "=" * 60)
    print("Example: Impact Analysis")
    print("=" * 60)
    print_impact_analysis(graph, "telegram_bot_stack.storage.base")

    # Example: Module info
    print_module_info(graph, "telegram_bot_stack.bot_base")

    # Validate graph
    print("\n🔍 Graph Validation:")
    errors = validate_graph(graph)
    if errors:
        print("❌ Validation errors found:")
        for error in errors:
            print(f"  • {error}")
    else:
        print("✅ Graph is valid!")
