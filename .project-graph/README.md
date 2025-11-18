# Multi-Graph System v3.1

**Hierarchical graph-based code navigation for AI agents and developers.**

**Coverage:** 100% of project files (~100 files) | **Domains:** 8 specialized graphs | **Savings:** 90-95% tokens

## 🎯 Core Concept

**Problem:** Reading 10,000+ lines of code is slow and inefficient.

**Solution:** Read 900-1000 lines of structured dependency graphs instead.

**Result:** 90% token savings, 100% coverage, better understanding.

## 🚀 Quick Start

```python
from utils.graph_utils import load_router, get_recommended_graph, load_graph_by_type

# Step 1: Load router (~783 lines)
router = load_router()

# Step 2: Get recommendation
graph_file = get_recommended_graph(router, "your task here")

# Step 3: Load specific domain
docs = load_graph_by_type('docs')
config = load_graph_by_type('configuration')
```

## 📁 Domain Graphs

| Domain                | Use When               | Files       | Load Function                          |
| --------------------- | ---------------------- | ----------- | -------------------------------------- |
| **bot-framework** 🤖  | Framework code         | 10 modules  | `load_graph_by_type('bot_framework')`  |
| **infrastructure** 🔧 | CI/CD, automation      | 16+ scripts | `load_graph_by_type('infrastructure')` |
| **testing** 🧪        | Tests, fixtures        | 7 files     | `load_graph_by_type('testing')`        |
| **examples** 📚       | Example bots           | 6 bots      | `load_graph_by_type('examples')`       |
| **docs** 📖           | Documentation          | 9 docs      | `load_graph_by_type('docs')`           |
| **configuration** ⚙️  | Build system, configs  | 7 files     | `load_graph_by_type('configuration')`  |
| **archive** 📦        | Historical, deprecated | 6 files     | `load_graph_by_type('archive')`        |
| **project-meta** 🌐   | Architecture overview  | Cross-graph | `load_graph_by_type('project_meta')`   |

## 📊 Structure

```
.project-graph/
├── graph-router.json           # START HERE (783 lines)
│
├── bot-framework/              # Hierarchical: 3 sub-graphs
│   ├── router.json
│   ├── core-graph.json         # BotBase, UserManager (321 lines)
│   ├── storage-graph.json      # JSON, Memory, SQL (435 lines)
│   └── utilities-graph.json    # Decorators (85 lines)
│
├── infrastructure/graph.json   # CI/CD (639 lines)
├── testing/graph.json          # Tests (539 lines)
├── examples/graph.json         # Examples (471 lines)
├── docs/graph.json             # Documentation (9 files)
├── configuration/graph.json    # Build configs (7 files)
├── archive/graph.json          # Deprecated (6 files)
├── project-meta/graph.json     # Architecture (493 lines)
│
└── utils/
    ├── graph_utils.py          # Navigation functions
    └── examples.py             # Usage examples
```

## 💡 Common Use Cases

### 1. Update Documentation

```python
docs = load_graph_by_type('docs')
api_ref = find_node(docs, 'docs.api_reference')
# → Edit: docs/api_reference.md (802 lines)
```

### 2. Add Dependency

```python
config = load_graph_by_type('configuration')
pyproject = find_node(config, 'config.pyproject')
# → Edit: pyproject.toml → dependencies
```

### 3. Add Storage Backend

```python
# Load hierarchical sub-graph
storage = load_sub_graph('bot_framework', 'storage')
base = find_node(storage, 'telegram_bot_stack.storage.base')
# → Implement: telegram_bot_stack/storage/redis.py
# → Update: bot-framework/storage-graph.json
```

### 4. Configure Tools

```python
config = load_graph_by_type('configuration')
# → Edit: pyproject.toml [tool.ruff]
# → Edit: .pre-commit-config.yaml
```

### 5. Historical Context

```python
archive = load_graph_by_type('archive')
# → Check: Why Docker was removed?
# → Read: archive/PACKAGE_CONVERSION_PLAN_RU.md
```

### 6. Cross-Domain Task (Add Feature)

```python
# Step 1: Implementation
storage = load_sub_graph('bot_framework', 'storage')

# Step 2: Tests
testing = load_graph_by_type('testing')

# Step 3: Documentation
docs = load_graph_by_type('docs')

# Step 4: Examples
examples = load_graph_by_type('examples')
```

## 🎓 Key Functions

```python
from utils.graph_utils import (
    # Basic
    load_router,                # Load main router
    load_graph_by_type,         # Load domain graph
    get_recommended_graph,      # Get recommendation
    find_node,                  # Find specific node

    # Hierarchical (bot-framework only)
    is_hierarchical_graph,      # Check if hierarchical
    load_sub_graph,             # Load sub-graph (core/storage/utilities)
    list_sub_graphs,            # List available sub-graphs
    load_full_hierarchical_graph, # Merge all sub-graphs
    get_recommended_sub_graph,  # Get sub-graph recommendation

    # Analysis
    find_dependencies,          # Get dependencies
    find_dependents,           # Get dependents
    get_impact_analysis,       # Impact analysis
)
```

## 📋 Decision Tree

```
Your Task                               → Load Graph
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Framework code (BotBase, storage)      → bot-framework
  └─ Core bot logic                    →   bot-framework/core
  └─ Storage backends                  →   bot-framework/storage
  └─ Decorators, helpers               →   bot-framework/utilities

CI/CD, workflows, automation            → infrastructure
Writing/running tests                   → testing
Example bot patterns                    → examples
Writing/updating docs                   → docs
Adding dependencies, build config       → configuration
Understanding history, deprecated       → archive
Project architecture overview           → project-meta
```

## 📈 Performance Comparison

| Approach                  | Lines Read | Savings |
| ------------------------- | ---------- | ------- |
| ❌ Read all project files | 10,000+    | 0%      |
| ✅ Router + 1 graph       | 900-1,000  | 90%     |
| ✅ Router + sub-graph     | 700-900    | 92%     |

## 🎯 Best Practices

1. **Always start with router** - It's your navigation hub (783 lines)
2. **Use recommendations** - `get_recommended_graph(router, task)`
3. **Load specific domains** - Don't read everything, be surgical
4. **Use sub-graphs** - For bot-framework, load only core/storage/utilities
5. **Cache router** - Load once, query many times
6. **Update graphs** - When adding files, update relevant graph

## 🔄 Hierarchical vs Flat

### Hierarchical Graph (1)

**bot-framework** - Split when exceeded 1200 lines:

- `core` - BotBase, UserManager, AdminManager (321 lines)
- `storage` - JSON, Memory, SQL backends (435 lines)
- `utilities` - Decorators, helpers (85 lines)

```python
# Load specific sub-graph
storage = load_sub_graph('bot_framework', 'storage')

# Or load all merged
full = load_full_hierarchical_graph('bot_framework')
```

### Flat Graphs (7)

All other domains are flat (< 1200 lines):

```python
# Direct load
docs = load_graph_by_type('docs')
config = load_graph_by_type('configuration')
archive = load_graph_by_type('archive')
```

## 🛠️ Utilities

### Validation

```bash
cd .project-graph && python3 utils/graph_utils.py
```

### Examples

```bash
# See utils/examples.py for complete examples
python3 utils/examples.py
```

### Maintenance

When adding new files:

1. Identify affected graph (use decision tree)
2. Update graph JSON (add nodes/edges)
3. Update router statistics if significant
4. Validate: `python3 utils/graph_utils.py`

**Example:** Adding `telegram_bot_stack/cache.py`

- Update: `bot-framework/utilities-graph.json`
- Add node for cache module
- Update metadata (node_count, edge_count)

## 📦 Version History

**v3.1.0 (2025-11-19)** - Complete Coverage

- ✅ Added docs graph (9 documentation files)
- ✅ Added configuration graph (7 config files)
- ✅ Added archive graph (6 historical files)
- ✅ 100% project coverage achieved
- ✅ 8 specialized domain graphs

**v3.0.0** - Hierarchical system

- Split bot-framework into 3 sub-graphs
- Introduced domain routers
- 80-90% token savings

## 🔮 Roadmap

**v3.2** - Enhanced Navigation

- Interactive CLI for exploration
- VS Code extension
- Auto-update graphs on file changes

**v3.3** - Visualization

- Mermaid diagram generation
- D3.js interactive viewer
- GraphViz export

**v3.4** - Smart Analysis

- Automated impact analysis
- Circular dependency detection
- Breaking change prediction

---

**Start here:** `graph-router.json` → Find your domain → Load specific graph → Work efficiently

**Token Budget:** Read 1000 lines instead of 10,000+ (90% savings)
