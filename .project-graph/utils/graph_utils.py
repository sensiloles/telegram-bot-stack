"""Utility functions for working with the dependency graphs.

This module provides helper functions for querying and analyzing the
project dependency graphs. The project uses a multi-graph system with
a router to help AI agents quickly find relevant information.

Examples:
    # Load specific graph by type
    >>> from graph_utils import load_graph_by_type
    >>> graph = load_graph_by_type('bot_framework')

    # Load router to understand all graphs
    >>> from graph_utils import load_router, get_recommended_graph
    >>> router = load_router()
    >>> graph_name = get_recommended_graph(router, "Add new storage backend")
    >>> graph = load_graph(graph_name)

    # Traditional usage (works with any graph)
    >>> graph = load_graph('bot-framework-graph.json')
    >>> node = find_node(graph, 'telegram_bot_stack.bot_base')
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


def load_router() -> Dict[str, Any]:
    """Load the graph router.

    Returns:
        Dictionary containing graph router metadata and recommendations

    Raises:
        FileNotFoundError: If router file doesn't exist
        json.JSONDecodeError: If router file is not valid JSON
    """
    router_path = Path(__file__).parent.parent / "graph-router.json"
    with open(router_path, encoding="utf-8") as f:
        return json.load(f)


def load_graph_by_type(graph_type: str) -> Dict[str, Any]:
    """Load a specific graph by its type.

    Args:
        graph_type: Type of graph to load. Options:
            - 'bot_framework': Core framework code
            - 'infrastructure': CI/CD and automation
            - 'testing': Test infrastructure
            - 'examples': Example bots
            - 'docs': Documentation files
            - 'configuration': Build system and configs
            - 'archive': Deprecated and historical
            - 'project_meta': Project overview

    Returns:
        Dictionary containing the requested graph

    Raises:
        ValueError: If graph_type is unknown
        FileNotFoundError: If graph file doesn't exist
    """
    router = load_router()

    # Try to find by ID first
    for graph_file, graph_info in router["graphs"].items():
        if graph_info["id"] == graph_type or graph_file == graph_type:
            return load_graph(graph_info["file"])

    # Not found
    available_ids = [info["id"] for info in router["graphs"].values()]
    raise ValueError(
        f"Unknown graph type '{graph_type}'. Available IDs: {available_ids}"
    )


def get_recommended_graph(router: Dict[str, Any], task_description: str) -> str:
    """Get recommended graph file based on task description.

    This uses keyword matching against when_to_use and typical_queries.

    Args:
        router: Graph router dictionary
        task_description: Description of the task (case-insensitive)

    Returns:
        Recommended graph filename
    """
    task_lower = task_description.lower()
    task_words = set(task_lower.split())

    best_match = None
    best_score = 0

    # Check each graph's when_to_use and typical_queries
    for _graph_file, graph_info in router["graphs"].items():
        score = 0

        # Check when_to_use
        for use_case in graph_info.get("when_to_use", []):
            use_case_lower = use_case.lower()
            use_case_words = set(use_case_lower.split())

            # Count matching words
            common_words = task_words & use_case_words
            if common_words:
                score += len(common_words) * 2  # Higher weight for when_to_use

        # Check typical_queries
        for query in graph_info.get("typical_queries", []):
            query_lower = query.lower()
            query_words = set(query_lower.split())

            # Count matching words
            common_words = task_words & query_words
            if common_words:
                score += len(common_words)

        if score > best_score:
            best_score = score
            best_match = graph_info["id"]

    # If we found a match, return it
    if best_match and best_score >= 2:  # At least 2 matching words
        return best_match

    # Default to project meta for overview
    return "project_meta"


def list_available_graphs() -> None:
    """Print all available graphs with descriptions."""
    router = load_router()

    print("\n📊 Available Dependency Graphs:")
    print("=" * 60)

    for _graph_file, graph_info in router["graphs"].items():
        print(f"\n🔹 {graph_info['name']}")
        print(f"   ID: {graph_info['id']}")
        print(f"   File: {graph_info['file']}")
        print(f"   Description: {graph_info['description']}")
        print(
            f"   Modules/Components: {graph_info['coverage'].get('modules', graph_info['coverage'].get('scripts', 'N/A'))}"
        )

    print("\n" + "=" * 60)
    print("Use load_graph_by_type('<id>') to load a specific graph")
    print("Example: load_graph_by_type('bot_framework')")
    print("=" * 60 + "\n")


def load_graph(graph_path: Optional[str] = None) -> Dict[str, Any]:
    """Load dependency graph from JSON file.

    Args:
        graph_path: Path to graph JSON file. If None, loads bot-framework-graph.json.
                   Can be just filename (e.g., 'testing-graph.json') or full path.

    Returns:
        Dictionary containing the full dependency graph

    Raises:
        FileNotFoundError: If graph file doesn't exist
        json.JSONDecodeError: If graph file is not valid JSON
    """
    if graph_path is None:
        # Default to bot framework graph
        graph_path = Path(__file__).parent.parent / "bot-framework" / "router.json"
    else:
        graph_path = Path(graph_path)
        # If just filename provided, look in .project-graph directory
        if not graph_path.is_absolute() and not graph_path.exists():
            graph_path = Path(__file__).parent.parent / graph_path

    with open(graph_path, encoding="utf-8") as f:
        return json.load(f)


def save_graph(graph: Dict[str, Any], graph_path: Optional[str] = None) -> None:
    """Save dependency graph to JSON file.

    Args:
        graph: Dictionary containing the full dependency graph
        graph_path: Path to graph JSON file. If None, tries to infer from graph metadata.
    """
    if graph_path is None:
        # Try to infer from graph metadata
        graph_id = graph.get("metadata", {}).get("graph_id", "bot_framework")
        graph_path = Path(__file__).parent / f"{graph_id}-graph.json"
    else:
        graph_path = Path(graph_path)
        if not graph_path.is_absolute():
            graph_path = Path(__file__).parent / graph_path

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


def find_node_by_path(
    graph: Dict[str, Any], file_path: str
) -> Optional[Dict[str, Any]]:
    """Find a node by its file path.

    Args:
        graph: Dependency graph
        file_path: File path to search for (e.g., 'telegram_bot_stack/storage/base.py')

    Returns:
        Node dictionary if found, None otherwise
    """
    for node in graph["nodes"]:
        if node.get("path") == file_path:
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


# ========== Hierarchical Graph Support (v3.0) ==========


def is_hierarchical_graph(graph_type: str) -> bool:
    """Check if a graph type uses hierarchical sub-graphs.

    Args:
        graph_type: Graph type identifier (e.g., 'bot_framework')

    Returns:
        True if graph has sub-graphs, False otherwise
    """
    try:
        router = load_router()
        for graph_file, graph_info in router["graphs"].items():
            if graph_info["id"] == graph_type or graph_file == graph_type:
                return graph_info.get("has_sub_graphs", False)
        return False
    except Exception:
        return False


def load_domain_router(graph_type: str) -> Dict[str, Any]:
    """Load domain router for hierarchical graphs.

    Args:
        graph_type: Graph type identifier (e.g., 'bot_framework')

    Returns:
        Domain router dictionary with sub-graph information

    Raises:
        ValueError: If graph is not hierarchical
        FileNotFoundError: If router file doesn't exist
    """
    if not is_hierarchical_graph(graph_type):
        raise ValueError(f"Graph '{graph_type}' is not hierarchical")

    router = load_router()
    for graph_file, graph_info in router["graphs"].items():
        if graph_info["id"] == graph_type or graph_file == graph_type:
            router_file = graph_info.get("router_file")
            if router_file:
                router_path = Path(__file__).parent.parent / router_file
                with open(router_path, encoding="utf-8") as f:
                    return json.load(f)

    raise FileNotFoundError(f"Domain router not found for '{graph_type}'")


def list_sub_graphs(graph_type: str) -> Dict[str, Dict[str, Any]]:
    """List all sub-graphs for a hierarchical graph.

    Args:
        graph_type: Graph type identifier (e.g., 'bot_framework')

    Returns:
        Dictionary mapping sub-graph IDs to their metadata

    Example:
        >>> sub_graphs = list_sub_graphs('bot_framework')
        >>> print(sub_graphs.keys())  # ['core', 'storage', 'utilities']
    """
    domain_router = load_domain_router(graph_type)
    return domain_router.get("sub_graphs", {})


def load_sub_graph(graph_type: str, sub_graph_id: str) -> Dict[str, Any]:
    """Load a specific sub-graph from a hierarchical graph.

    Args:
        graph_type: Parent graph type (e.g., 'bot_framework')
        sub_graph_id: Sub-graph identifier (e.g., 'core', 'storage')

    Returns:
        Sub-graph dictionary

    Raises:
        ValueError: If sub-graph doesn't exist
        FileNotFoundError: If sub-graph file doesn't exist

    Example:
        >>> core = load_sub_graph('bot_framework', 'core')
        >>> print(core['metadata']['graph_name'])  # 'Bot Framework - Core'
    """
    sub_graphs = list_sub_graphs(graph_type)

    if sub_graph_id not in sub_graphs:
        available = list(sub_graphs.keys())
        raise ValueError(
            f"Sub-graph '{sub_graph_id}' not found in '{graph_type}'. "
            f"Available: {available}"
        )

    sub_graph_info = sub_graphs[sub_graph_id]
    file_path = Path(__file__).parent.parent / sub_graph_info["file"]

    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


def load_full_hierarchical_graph(graph_type: str) -> Dict[str, Any]:
    """Load and merge all sub-graphs into a single graph view.

    This is useful when you need the complete graph, but the source
    is split into sub-graphs for manageability.

    Args:
        graph_type: Parent graph type (e.g., 'bot_framework')

    Returns:
        Merged graph dictionary with all nodes and edges

    Example:
        >>> full_graph = load_full_hierarchical_graph('bot_framework')
        >>> print(full_graph['metadata']['node_count'])  # Total from all sub-graphs
    """
    domain_router = load_domain_router(graph_type)
    sub_graphs_info = domain_router.get("sub_graphs", {})

    all_nodes = []
    all_edges = []
    total_loc = 0

    for sub_graph_id, sub_info in sub_graphs_info.items():
        sub_graph = load_sub_graph(graph_type, sub_graph_id)
        all_nodes.extend(sub_graph.get("nodes", []))
        all_edges.extend(sub_graph.get("edges", []))
        total_loc += sub_info.get("lines_of_code", 0)

    # Add cross-graph edges
    cross_edges = domain_router.get("cross_graph_edges", [])
    for cross_edge in cross_edges:
        edge = {
            "id": cross_edge["id"],
            "source": cross_edge["source_node"],
            "target": cross_edge["target_node"],
            "type": cross_edge["type"],
            "description": cross_edge.get("description", ""),
            "cross_graph": True,
            "source_graph": cross_edge["source_graph"],
            "target_graph": cross_edge["target_graph"],
        }
        all_edges.append(edge)

    # Create merged graph
    merged_graph = {
        "metadata": {
            "version": "3.0.0",
            "graph_id": domain_router["metadata"]["graph_id"],
            "graph_name": domain_router["metadata"]["graph_name"],
            "graph_type": "merged_hierarchical",
            "source": "merged from sub-graphs",
            "project_name": domain_router["metadata"]["project_name"],
            "project_version": domain_router["metadata"]["project_version"],
            "node_count": len(all_nodes),
            "edge_count": len(all_edges),
            "sub_graphs_count": len(sub_graphs_info),
        },
        "nodes": all_nodes,
        "edges": all_edges,
        "sub_graphs": sub_graphs_info,
        "statistics": domain_router.get("statistics", {}),
    }

    return merged_graph


def get_recommended_sub_graph(graph_type: str, task_description: str) -> str:
    """Get recommended sub-graph based on task description.

    Args:
        graph_type: Parent graph type (e.g., 'bot_framework')
        task_description: Description of what you want to do

    Returns:
        Sub-graph ID (e.g., 'core', 'storage', 'utilities')

    Example:
        >>> sub_id = get_recommended_sub_graph('bot_framework', 'add storage backend')
        >>> print(sub_id)  # 'storage'
    """
    sub_graphs = list_sub_graphs(graph_type)
    task_lower = task_description.lower()

    # Score each sub-graph based on keywords in recommended_for
    scores = {}
    for sub_id, sub_info in sub_graphs.items():
        score = 0
        recommended_for = sub_info.get("recommended_for", [])
        for recommendation in recommended_for:
            rec_lower = recommendation.lower()
            # Count keyword matches
            keywords = rec_lower.split()
            matches = sum(1 for kw in keywords if kw in task_lower)
            score += matches
        scores[sub_id] = score

    # Return sub-graph with highest score, or first one if no matches
    if max(scores.values()) > 0:
        return max(scores, key=scores.get)
    else:
        return list(sub_graphs.keys())[0]


# Example usage
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔗 Multi-Graph Dependency System")
    print("=" * 60)

    # Show available graphs
    list_available_graphs()

    # Example: Load bot framework graph
    print("\n📦 Loading Bot Framework Graph...")
    graph = load_graph_by_type("bot_framework")

    print(f"Version: {graph['metadata']['version']}")
    print(f"Graph: {graph['metadata']['graph_name']}")
    print(f"Modules: {graph['metadata'].get('node_count', 'N/A')}")
    print(f"Dependencies: {graph['metadata'].get('edge_count', 'N/A')}\n")

    # Find critical modules (only for bot_framework graph)
    if "nodes" in graph:
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

    # Validate graph (works for bot_framework graph)
    print("\n🔍 Bot Framework Graph Validation:")
    errors = validate_graph(graph)
    if errors:
        print("❌ Validation errors found:")
        for error in errors:
            print(f"  • {error}")
    else:
        print("✅ Graph is valid!")

    # Example: Recommend graph based on task
    print("\n" + "=" * 60)
    print("🎯 Graph Recommendation Examples")
    print("=" * 60)

    router = load_router()
    tasks = [
        "Add new storage backend",
        "Fix CI pipeline",
        "Add test for user manager",
        "Create new example bot",
    ]

    for task in tasks:
        recommended = get_recommended_graph(router, task)
        print(f"\nTask: {task}")
        print(f"  → Recommended graph: {recommended}")
