# 🔗 Multi-Graph Dependency System v3.0

Hierarchical graph-based code navigation for AI agents and developers.

## 🎯 What & Why

**Problem:** Large monolithic dependency graphs (2000+ lines) are slow to read and process.

**Solution:** Domain-specific graphs with hierarchical sub-graphs for focused navigation.

**Result:**

- **80-90% token savings** (router → graph)
- **50-60% additional savings** with sub-graphs
- Read 300-450 lines instead of 1145+ lines

## 📊 Structure

```
.project-graph/
├── graph-router.json           # Start here - navigation hub (530 lines)
│
├── bot-framework/              # 🤖 Hierarchical domain (3 sub-graphs)
│   ├── router.json            # Domain router (89 lines)
│   ├── core-graph.json        # Core bot logic (321 lines)
│   ├── storage-graph.json     # Storage backends (435 lines)
│   └── utilities-graph.json   # Decorators, helpers (85 lines)
│
├── infrastructure/             # 🔧 Flat domain
│   ├── router.json            # Domain metadata
│   └── graph.json             # CI/CD, automation (639 lines)
│
├── testing/                    # 🧪 Flat domain
│   ├── router.json            # Domain metadata
│   └── graph.json             # Test infrastructure (539 lines)
│
├── examples/                   # 📚 Flat domain
│   ├── router.json            # Domain metadata
│   └── graph.json             # Example bots (471 lines)
│
├── project-meta/               # 🌐 Flat domain
│   ├── router.json            # Domain metadata
│   └── graph.json             # Project overview (493 lines)
│
└── utils/                      # 🛠️ Python utilities
    ├── graph_utils.py          # Graph navigation functions
    ├── split_bot_framework.py  # Graph splitting tool
    └── examples.py             # Usage examples
```

## 🚀 Quick Start

### For AI Agents

**Step 1:** Read router (~530 lines)

```python
from graph_utils import load_router
router = load_router()
```

**Step 2:** Get recommendation

```python
from graph_utils import get_recommended_graph
graph_file = get_recommended_graph(router, "add storage backend")
# Returns: "bot-framework-graph.json"
```

**Step 3:** Check if hierarchical

```python
from graph_utils import is_hierarchical_graph, get_recommended_sub_graph

if is_hierarchical_graph('bot_framework'):
    # Get specific sub-graph
    sub_id = get_recommended_sub_graph('bot_framework', 'add storage backend')
    # Returns: "storage"
```

**Step 4:** Load only what you need

```python
from graph_utils import load_sub_graph
storage_graph = load_sub_graph('bot_framework', 'storage')
# Read 435 lines instead of 1145 lines (62% savings!)
```

### For Humans

```python
from graph_utils import load_graph_by_type, find_node

# Load graph
graph = load_graph_by_type('bot_framework')

# Find module
node = find_node(graph, 'telegram_bot_stack.bot_base')
print(node['description'])
```

## 🔄 Hierarchical Graphs

### When to Use

**Flat graph** (< 1200 lines): Use as-is

```python
graph = load_graph_by_type('testing')  # 539 lines - OK
```

**Hierarchical** (> 1200 lines): Use sub-graphs

```python
# Instead of loading entire 1145-line graph:
graph = load_graph_by_type('bot_framework')  # DON'T

# Load specific sub-graph:
core = load_sub_graph('bot_framework', 'core')  # DO (321 lines)
```

### Available Sub-Graphs

**bot-framework** (only hierarchical domain currently):

- `core` - BotBase, UserManager, AdminManager (321 lines)
- `storage` - JSON, Memory, SQL backends (435 lines)
- `utilities` - Decorators, helpers (85 lines)

## 📖 Usage Patterns

### Pattern 1: Task-Based Navigation

```python
from graph_utils import get_recommended_graph, load_graph

# Get recommendation
task = "add new decorator"
graph_file = get_recommended_graph(router, task)

# For hierarchical graphs
if 'bot-framework' in graph_file:
    sub_id = get_recommended_sub_graph('bot_framework', task)
    graph = load_sub_graph('bot_framework', sub_id)
else:
    graph = load_graph(graph_file)
```

### Pattern 2: Explore Sub-Graphs

```python
from graph_utils import list_sub_graphs, load_sub_graph

# List available sub-graphs
sub_graphs = list_sub_graphs('bot_framework')
for sub_id, info in sub_graphs.items():
    print(f"{sub_id}: {info['description']}")

# Load specific one
storage = load_sub_graph('bot_framework', 'storage')
```

### Pattern 3: Full Merged View

```python
from graph_utils import load_full_hierarchical_graph

# Load all sub-graphs merged (when you need complete view)
full_graph = load_full_hierarchical_graph('bot_framework')
# Returns merged graph with all 10 modules
```

## 🏗️ Architecture Decisions

### Why Hierarchical?

**Trigger:** Graph exceeds 1200 lines

**Benefits:**

1. **Focused Context:** Read only relevant sub-system
2. **Better Reasoning:** Smaller graphs easier to understand
3. **Scalability:** Project can grow to 100+ modules
4. **Visualization:** Hierarchical views for humans

### Size Guidelines

| Type       | Lines    | Action                    |
| ---------- | -------- | ------------------------- |
| Router     | 200-500  | Keep compact              |
| Flat Graph | < 800    | No split needed           |
| Flat Graph | 800-1200 | Monitor growth            |
| Flat Graph | > 1200   | **Split into sub-graphs** |
| Sub-Graph  | 300-800  | Ideal size                |

### Future Domains

When other graphs exceed 1200 lines, create hierarchical structure:

```
infrastructure/
├── router.json
├── ci-cd-graph.json
├── automation-graph.json
└── deployment-graph.json
```

## 🛠️ Utilities

### graph_utils.py

Core navigation functions:

**Loading:**

- `load_router()` - Load main router
- `load_graph(filename)` - Load any graph
- `load_graph_by_type(type)` - Load by domain type

**Hierarchical:**

- `is_hierarchical_graph(type)` - Check if has sub-graphs
- `list_sub_graphs(type)` - List available sub-graphs
- `load_sub_graph(type, sub_id)` - Load specific sub-graph
- `load_full_hierarchical_graph(type)` - Merge all sub-graphs
- `get_recommended_sub_graph(type, task)` - Get recommendation

**Analysis:**

- `find_node(graph, id)` - Find module by ID
- `get_dependencies(graph, id)` - Get dependencies
- `get_dependents(graph, id)` - Get dependents
- `analyze_impact(graph, id)` - Impact analysis

### split_bot_framework.py

Tool for splitting large graphs into sub-graphs. Used to create bot-framework/ structure.

## 📋 Decision Tree

```
1. What are you working on?
   ├─ Bot framework (BotBase, storage, etc)
   │  ├─ Core bot logic? → bot-framework/core
   │  ├─ Storage backend? → bot-framework/storage
   │  └─ Decorators/utils? → bot-framework/utilities
   │
   ├─ CI/CD, automation → infrastructure-graph
   ├─ Tests, fixtures → testing-graph
   ├─ Example bots → examples-graph
   └─ Project overview → project-meta-graph

2. Load recommended graph/sub-graph
3. Work with focused context
```

## 🎓 Examples

See `utils/examples.py` for complete usage examples.

## 🔮 Roadmap

### v3.1 - Enhanced Navigation

- Interactive CLI for graph exploration
- VS Code extension with tree view
- Graph validation in CI/CD

### v3.2 - Visualization

- Mermaid diagram generation
- D3.js interactive web viewer
- Export to GraphViz/DOT format

### v3.3 - Smart Analysis

- Automated impact analysis
- Circular dependency detection
- Performance bottleneck identification
- Breaking change prediction

### Future Hierarchical Splits

When graphs exceed 1200 lines:

- `infrastructure/` → ci-cd, automation, deployment
- `testing/` → unit, integration, fixtures
- `examples/` → simple, advanced, production

---

**Version:** 3.0.0 (Hierarchical Multi-Graph System)
**Last Updated:** 2025-11-19
**Domains:** 5 (1 hierarchical with 3 sub-graphs)
**Total Graphs:** 8 files (router + 5 domains + 2 hierarchical layers)
