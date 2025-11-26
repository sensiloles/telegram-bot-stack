#!/usr/bin/env python3
"""Unified graph generator with reduced code duplication.

This module provides a generic graph generation framework that
eliminates code duplication across different graph generators.

Usage:
    from unified_generator import GraphGenerator

    generator = GraphGenerator(
        graph_id='testing',
        graph_name='Testing Infrastructure',
        description='Test suite, fixtures, and testing utilities'
    )

    generator.add_directory('tests', node_type='test_module')
    graph = generator.build()
"""

import ast
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set


class GraphGenerator:
    """Generic graph generator with configurable behavior."""

    def __init__(
        self,
        graph_id: str,
        graph_name: str,
        description: str,
        scope: str = "",
        project_name: str = "telegram-bot-stack",
        project_root: Optional[Path] = None
    ):
        """Initialize generator.

        Args:
            graph_id: Unique graph identifier
            graph_name: Human-readable graph name
            description: Graph description
            scope: Scope of coverage
            project_name: Project name
            project_root: Project root path (auto-detected if not provided)
        """
        self.graph_id = graph_id
        self.graph_name = graph_name
        self.description = description
        self.scope = scope
        self.project_name = project_name

        if project_root is None:
            self.project_root = Path(__file__).parent.parent.parent
        else:
            self.project_root = project_root

        self.nodes: List[Dict[str, Any]] = []
        self.edges: List[Dict[str, Any]] = []
        self._edge_counter = 1
        self._node_ids: Set[str] = set()

    def add_directory(
        self,
        directory: str,
        node_type: str = 'module',
        file_pattern: str = '*.py',
        recursive: bool = True,
        exclude_patterns: Optional[List[str]] = None,
        node_filter: Optional[Callable[[Path], bool]] = None
    ) -> int:
        """Add all files from a directory to the graph.

        Args:
            directory: Directory path relative to project root
            node_type: Type of nodes to create
            file_pattern: Glob pattern for files
            recursive: If True, search recursively
            exclude_patterns: Patterns to exclude (e.g., '__init__.py')
            node_filter: Optional function to filter files

        Returns:
            Number of nodes added
        """
        dir_path = self.project_root / directory

        if not dir_path.exists():
            return 0

        if exclude_patterns is None:
            exclude_patterns = ['__pycache__', '.pyc', '.egg-info']

        count = 0

        # Find files
        if recursive:
            files = dir_path.rglob(file_pattern)
        else:
            files = dir_path.glob(file_pattern)

        for file_path in files:
            # Skip excluded patterns
            if any(pattern in str(file_path) for pattern in exclude_patterns):
                continue

            # Skip if doesn't pass filter
            if node_filter and not node_filter(file_path):
                continue

            # Create node
            node = self._create_node_from_file(file_path, node_type)
            if node and node['id'] not in self._node_ids:
                self.nodes.append(node)
                self._node_ids.add(node['id'])
                count += 1

        return count

    def add_file(
        self,
        file_path: str,
        node_type: str = 'module'
    ) -> bool:
        """Add a specific file to the graph.

        Args:
            file_path: File path relative to project root
            node_type: Type of node to create

        Returns:
            True if node was added, False otherwise
        """
        full_path = self.project_root / file_path

        if not full_path.exists():
            return False

        node = self._create_node_from_file(full_path, node_type)
        if node and node['id'] not in self._node_ids:
            self.nodes.append(node)
            self._node_ids.add(node['id'])
            return True

        return False

    def add_custom_node(
        self,
        node_id: str,
        name: str,
        node_type: str,
        **kwargs
    ) -> bool:
        """Add a custom node with arbitrary attributes.

        Args:
            node_id: Unique node identifier
            name: Node name
            node_type: Node type
            **kwargs: Additional node attributes

        Returns:
            True if node was added, False if ID already exists
        """
        if node_id in self._node_ids:
            return False

        node = {
            'id': node_id,
            'name': name,
            'type': node_type,
            **kwargs
        }

        self.nodes.append(node)
        self._node_ids.add(node_id)
        return True

    def generate_edges(self, edge_type: str = 'imports') -> int:
        """Generate edges based on imports in Python files.

        Args:
            edge_type: Type of edges to create

        Returns:
            Number of edges created
        """
        count = 0
        # Track existing edges to avoid duplicates
        existing_edges = set()

        for node in self.nodes:
            if not node.get('path', '').endswith('.py'):
                continue

            file_path = self.project_root / node['path']

            if not file_path.exists():
                continue

            # Extract imports
            imports = self._extract_imports(file_path)

            # Create edges (deduplicated)
            for imported_module in imports:
                # Find target node
                target_id = self._find_node_id_by_module(imported_module)

                if target_id and target_id != node['id']:
                    # Create edge key for deduplication
                    edge_key = (node['id'], target_id, edge_type)

                    # Skip if edge already exists
                    if edge_key in existing_edges:
                        continue

                    existing_edges.add(edge_key)

                    edge = {
                        'id': f'edge_{self._edge_counter}',
                        'source': node['id'],
                        'target': target_id,
                        'type': edge_type,
                        'description': f'Imports from {target_id}'
                    }
                    self.edges.append(edge)
                    self._edge_counter += 1
                    count += 1

        return count

    def build(self) -> Dict[str, Any]:
        """Build final graph dictionary.

        Returns:
            Complete graph dictionary
        """
        return {
            'metadata': {
                'version': '3.0.0',
                'generated_at': datetime.now().strftime('%Y-%m-%d'),
                'graph_id': self.graph_id,
                'graph_name': self.graph_name,
                'graph_type': 'domain',
                'project_name': self.project_name,
                'description': self.description,
                'scope': self.scope or self.description,
                'node_count': len(self.nodes),
                'edge_count': len(self.edges),
            },
            'nodes': self.nodes,
            'edges': self.edges,
        }

    def save(self, output_path: Path) -> None:
        """Save graph to file.

        Args:
            output_path: Output file path
        """
        graph = self.build()

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(graph, f, indent=2)
            f.write('\n')

    def _create_node_from_file(
        self,
        file_path: Path,
        node_type: str
    ) -> Optional[Dict[str, Any]]:
        """Create a node from a file."""
        try:
            rel_path = file_path.relative_to(self.project_root)
        except ValueError:
            return None

        # Create node ID
        if file_path.suffix == '.py':
            parts = rel_path.with_suffix('').parts
            if parts[-1] == '__init__':
                parts = parts[:-1]
            node_id = '.'.join(parts)
        else:
            node_id = str(rel_path).replace('/', '.')

        # Analyze file
        if file_path.suffix == '.py':
            metadata = self._analyze_python_file(file_path)
        else:
            metadata = {
                'description': f'File {file_path.name}',
                'lines': len(file_path.read_text().splitlines()) if file_path.exists() else 0
            }

        # Create base node
        node = {
            'id': node_id,
            'name': file_path.stem,
            'type': node_type,
            'path': str(rel_path),
            'description': metadata.get('description', ''),
        }

        # Add Python-specific fields
        if file_path.suffix == '.py':
            node.update({
                'lines_of_code': metadata.get('lines', 0),
                'exports': metadata.get('classes', []) + metadata.get('functions', []),
                'classes': metadata.get('classes', []),
                'functions': metadata.get('functions', []),
            })

        return node

    def _analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze Python file and extract metadata."""
        try:
            with open(file_path) as f:
                source = f.read()
                tree = ast.parse(source)

            classes = []
            functions = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                    functions.append(node.name)

            # Get docstring
            docstring = ast.get_docstring(tree) or ''
            description = docstring.split('\n')[0] if docstring else f'Module {file_path.stem}'

            return {
                'classes': classes,
                'functions': functions,
                'lines': len(source.splitlines()),
                'description': description[:100]
            }

        except Exception:
            return {
                'classes': [],
                'functions': [],
                'lines': 0,
                'description': f'Module {file_path.stem}'
            }

    def _extract_imports(self, file_path: Path) -> Set[str]:
        """Extract imports from Python file (including relative imports)."""
        imports = set()

        try:
            with open(file_path) as f:
                source = f.read()
                tree = ast.parse(source)

            # Determine current module path for resolving relative imports
            try:
                rel_path = file_path.relative_to(self.project_root)
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

                    # Handle absolute imports
                    elif module:
                        module_parts = module.split('.')
                        if module_parts[0] in ['telegram_bot_stack', 'tests', 'examples']:
                            imports.add(module)

                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        module_parts = alias.name.split('.')
                        if module_parts[0] in ['telegram_bot_stack', 'tests', 'examples']:
                            imports.add(alias.name)

        except Exception:
            pass

        return imports

    def _find_node_id_by_module(self, module_name: str) -> Optional[str]:
        """Find node ID by module name."""
        # Try exact match
        if module_name in self._node_ids:
            return module_name

        # Try parent modules
        parts = module_name.split('.')
        while len(parts) > 1:
            parts.pop()
            parent = '.'.join(parts)
            if parent in self._node_ids:
                return parent

        return None


# Example usage functions for common patterns

def generate_testing_graph(project_root: Optional[Path] = None) -> Dict[str, Any]:
    """Generate testing graph using unified generator."""
    generator = GraphGenerator(
        graph_id='testing',
        graph_name='Testing Infrastructure',
        description='Test suite, fixtures, and testing utilities',
        scope='Unit tests, integration tests, fixtures',
        project_root=project_root
    )

    count = generator.add_directory('tests', node_type='test_module')
    print(f"   Added {count} test files")

    edges = generator.generate_edges()
    print(f"   Generated {edges} edges")

    return generator.build()


def generate_infrastructure_graph(project_root: Optional[Path] = None) -> Dict[str, Any]:
    """Generate infrastructure graph using unified generator."""
    generator = GraphGenerator(
        graph_id='infrastructure',
        graph_name='Infrastructure',
        description='CI/CD workflows, automation scripts, and tooling',
        scope='GitHub Actions, automation scripts, deployment',
        project_root=project_root
    )

    # Add .github files
    count_gh = generator.add_directory(
        '.github',
        node_type='workflow',
        file_pattern='*.*',
        exclude_patterns=['__pycache__', '.pyc', '.png', '.jpg']
    )
    print(f"   Added {count_gh} GitHub files")

    # Add scripts
    count_scripts = generator.add_directory(
        'scripts',
        node_type='script',
        recursive=False
    )
    print(f"   Added {count_scripts} scripts")

    edges = generator.generate_edges()
    print(f"   Generated {edges} edges")

    return generator.build()


def generate_examples_graph(project_root: Optional[Path] = None) -> Dict[str, Any]:
    """Generate examples graph using unified generator."""
    generator = GraphGenerator(
        graph_id='examples',
        graph_name='Example Bots',
        description='Example bot implementations and usage patterns',
        scope='Example bots demonstrating framework features',
        project_root=project_root
    )

    count = generator.add_directory(
        'examples',
        node_type='example_bot',
        node_filter=lambda p: p.name == 'bot.py' or not p.name.startswith('_')
    )
    print(f"   Added {count} example files")

    edges = generator.generate_edges()
    print(f"   Generated {edges} edges")

    return generator.build()


if __name__ == '__main__':
    # Example: Generate testing graph
    print("📦 Generating testing graph with unified generator...")
    graph = generate_testing_graph()
    print(f"✅ Generated graph with {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")
