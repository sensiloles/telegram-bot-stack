"""Project dependency graph utilities.

This package contains tools for working with the project dependency graph.

Example:
    >>> from project_graph import load_graph, find_node
    >>> graph = load_graph()
    >>> bot_base = find_node(graph, 'telegram_bot_stack.bot_base')
"""

from .graph_utils import (
    calculate_coupling_score,
    find_bottlenecks,
    find_critical_modules,
    find_dependencies,
    find_dependents,
    find_leaf_modules,
    find_node,
    find_nodes_by_category,
    find_nodes_by_tag,
    find_root_modules,
    get_impact_analysis,
    get_transitive_dependencies,
    get_transitive_dependents,
    load_graph,
    print_impact_analysis,
    print_module_info,
    save_graph,
    validate_graph,
)

__all__ = [
    "load_graph",
    "save_graph",
    "find_node",
    "find_nodes_by_tag",
    "find_nodes_by_category",
    "find_dependents",
    "find_dependencies",
    "get_transitive_dependents",
    "get_transitive_dependencies",
    "calculate_coupling_score",
    "find_leaf_modules",
    "find_root_modules",
    "find_bottlenecks",
    "find_critical_modules",
    "get_impact_analysis",
    "print_module_info",
    "print_impact_analysis",
    "validate_graph",
]
