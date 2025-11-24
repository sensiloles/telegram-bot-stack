# MCP Project Graph Integration

Integration of `.project-graph/` system with Model Context Protocol (MCP) for efficient AI agent navigation.

## Overview

The project graph MCP server exposes the hierarchical graph system through a standardized MCP interface, allowing AI agents to:

- 🚀 Navigate large codebase efficiently (90-95% token savings)
- 🎯 Get graph recommendations for specific tasks
- 📊 Analyze code dependencies and impact
- 🔍 Query project structure without reading all files

## Setup

### 1. Install MCP SDK

```bash
pip install mcp
```

### 2. Configure Cursor

Add to your Cursor settings (`.cursor/mcp_config.json` or Cursor settings):

```json
{
  "mcpServers": {
    "project-graph": {
      "command": "python3",
      "args": [
        "/absolute/path/to/telegram-bot-stack/scripts/mcp_project_graph.py"
      ],
      "description": "Project graph navigation for telegram-bot-stack"
    }
  }
}
```

**Important:** Use absolute path to ensure MCP server starts correctly.

**For this project:**
```json
{
  "mcpServers": {
    "project-graph": {
      "command": "python3",
      "args": [
        "/Users/sensiloles/Documents/work/telegram-bot-stack/scripts/mcp_project_graph.py"
      ],
      "description": "Project graph navigation"
    }
  }
}
```

**Or** add to workspace-specific settings:

```json
// .vscode/settings.json or workspace settings
{
  "cursor.mcp.servers": {
    "project-graph": {
      "command": "python3",
      "args": ["${workspaceFolder}/scripts/mcp_project_graph.py"]
    }
  }
}
```

### 3. Verify Setup

```python
# In Cursor chat, try:
# "Load the project graph router"
# Agent should use: fetch_mcp_resource(server="project-graph", uri="graph://router")
```

## Available Resources

### Main Graphs

| URI | Description | Lines | Use When |
|-----|-------------|-------|----------|
| `graph://router` | Navigation router | 783 | Start here - understand structure |
| `graph://bot_framework` | Framework core | ~800 | Working with core bot code |
| `graph://infrastructure` | CI/CD automation | 639 | Fixing workflows, scripts |
| `graph://testing` | Test infrastructure | 539 | Writing/debugging tests |
| `graph://examples` | Example bots | 471 | Understanding bot patterns |
| `graph://docs` | Documentation | ~300 | Updating docs |
| `graph://configuration` | Build configs | ~200 | Changing dependencies, config |
| `graph://archive` | Historical | ~250 | Understanding project history |
| `graph://project_meta` | Architecture | 493 | High-level understanding |

### Hierarchical Sub-Graphs (bot-framework)

| URI | Description | Lines |
|-----|-------------|-------|
| `graph://bot_framework/core` | BotBase, managers | 321 |
| `graph://bot_framework/storage` | Storage backends | 435 |
| `graph://bot_framework/utilities` | Decorators, helpers | 85 |

### Special URIs

```
graph://recommend?task=<description>  # Get graph recommendation
```

## Available Tools

### 1. `recommend_graph`

Get recommendation for which graph to load:

```python
# Agent call:
mcp_project_graph_recommend_graph(task="Add new storage backend")

# Returns:
{
  "recommended_graph": "bot_framework",
  "sub_graph": "storage"
}
```

### 2. `analyze_impact`

Analyze impact of changing a file:

```python
# Agent call:
mcp_project_graph_analyze_impact(
    file_path="telegram_bot_stack/storage/base.py",
    graph_type="bot_framework"
)

# Returns:
{
  "direct_dependents": ["sql.py", "json.py", "memory.py"],
  "transitive_dependents": ["bot_base.py"],
  "impact_level": "high"
}
```

### 3. `find_dependencies`

Find what a node depends on:

```python
# Agent call:
mcp_project_graph_find_dependencies(
    node_id="telegram_bot_stack.bot_base",
    graph_type="bot_framework"
)

# Returns:
{
  "dependencies": [
    "telegram_bot_stack.storage.base",
    "telegram_bot_stack.user_manager",
    "telegram_bot_stack.admin_manager"
  ]
}
```

### 4. `find_dependents`

Find who uses this node:

```python
# Agent call:
mcp_project_graph_find_dependents(
    node_id="telegram_bot_stack.storage.base",
    graph_type="bot_framework"
)

# Returns:
{
  "dependents": [
    "telegram_bot_stack.storage.json",
    "telegram_bot_stack.storage.sql",
    "telegram_bot_stack.storage.memory"
  ]
}
```

### 5. `list_sub_graphs`

List available sub-graphs for hierarchical graphs:

```python
# Agent call:
mcp_project_graph_list_sub_graphs(graph_type="bot_framework")

# Returns:
{
  "sub_graphs": [
    {"name": "core", "lines": 321},
    {"name": "storage", "lines": 435},
    {"name": "utilities", "lines": 85}
  ]
}
```

## Usage Examples

### Example 1: Add Storage Backend

**Agent workflow:**

```python
# 1. Get recommendation
fetch_mcp_resource("project-graph", "graph://recommend?task=add Redis storage backend")
# → Recommends: bot_framework/storage

# 2. Load storage sub-graph
storage = fetch_mcp_resource("project-graph", "graph://bot_framework/storage")
# → Returns 435 lines of storage graph instead of reading all files

# 3. Analyze dependencies
mcp_project_graph_find_dependencies(
    node_id="telegram_bot_stack.storage.base",
    graph_type="bot_framework"
)
# → Understand what base.py provides

# 4. Implement Redis backend
# ... (agent writes code)

# 5. Analyze impact
mcp_project_graph_analyze_impact(
    file_path="telegram_bot_stack/storage/redis.py",
    graph_type="bot_framework"
)
# → Verify no breaking changes
```

**Token savings:** 435 lines (graph) vs ~2000+ lines (reading all storage files)

### Example 2: Fix CI Workflow

**Agent workflow:**

```python
# 1. Get recommendation
fetch_mcp_resource("project-graph", "graph://recommend?task=fix GitHub Actions workflow")
# → Recommends: infrastructure

# 2. Load infrastructure graph
infra = fetch_mcp_resource("project-graph", "graph://infrastructure")
# → Returns 639 lines covering all CI/CD

# 3. Find relevant workflow
# (Graph shows: .github/workflows/tests.yml)

# 4. Fix issue and update
```

**Token savings:** 639 lines (graph) vs ~5000+ lines (reading all .github files)

### Example 3: Update Documentation

```python
# 1. Load docs graph
docs = fetch_mcp_resource("project-graph", "graph://docs")

# 2. Find target doc
# (Graph shows all 9 doc files with descriptions)

# 3. Update specific doc
```

## Integration with .cursorrules

Add to `.cursorrules`:

```markdown
## Project Navigation (MCP-Enhanced)

### Before Implementation:
1. Get graph recommendation:
   Use MCP: `recommend_graph` tool with task description

2. Load relevant graph:
   Use MCP: `fetch_mcp_resource("project-graph", "graph://recommended")`

3. Analyze dependencies:
   Use MCP: `find_dependencies` / `find_dependents` tools

### Common Tasks → MCP Resources:

| Task | MCP Resource |
|------|--------------|
| Add storage backend | `graph://bot_framework/storage` |
| Fix CI workflow | `graph://infrastructure` |
| Update docs | `graph://docs` |
| Add CLI command | `graph://bot_framework/utilities` |
| Write tests | `graph://testing` |

### Token Efficiency:
- ✅ Load graphs via MCP (200-800 lines)
- ❌ Don't read entire codebase (10,000+ lines)
- 💰 90-95% token savings
```

## Benefits

### For AI Agents

1. **Standardized Interface**
   - No need to know project-specific graph API
   - Works across different projects with MCP

2. **Automatic Caching**
   - MCP handles resource caching
   - Faster repeated queries

3. **Context Independence**
   - Works from any directory
   - No Python import issues

4. **Built-in Tools**
   - Dependency analysis
   - Impact assessment
   - Recommendations

### For Developers

1. **90-95% Token Savings**
   - Load 900 lines instead of 10,000+
   - Faster AI responses
   - Lower API costs

2. **Better Understanding**
   - Graph shows dependencies explicitly
   - Clear project structure
   - Easy navigation

3. **Maintainable**
   - Single MCP server for all graph operations
   - Graphs update independently
   - Versioned system

## Performance Comparison

| Approach | Tokens | Time | Accuracy |
|----------|--------|------|----------|
| Read all files | 10,000+ | Slow | Low (too much context) |
| Manual selection | ~2,000 | Medium | Medium (might miss files) |
| **Graph + MCP** | **900** | **Fast** | **High (comprehensive)** |

## Maintenance

### When to Update Graphs

Update graphs when:
- Adding new files to project
- Changing dependencies
- Refactoring module structure
- Adding new examples

### How to Update

```bash
# 1. Edit relevant graph JSON
vim .project-graph/bot-framework/storage-graph.json

# 2. Update metadata
# - node_count
# - edge_count
# - generated_at

# 3. Validate
cd .project-graph && python3 utils/graph_utils.py
```

### Auto-Update (Future)

```python
# Planned: Auto-update on file save
# .cursorrules will include:
# "After editing files, update relevant graph if structure changed"
```

## Troubleshooting

### MCP Server Not Found

```bash
# Verify MCP SDK installed
pip list | grep mcp

# Test server manually
python3 scripts/mcp_project_graph.py
```

### Resource Not Loading

```bash
# Check graph file exists
ls -la .project-graph/bot-framework/

# Validate JSON
cd .project-graph && python3 utils/graph_utils.py
```

### Import Errors

```bash
# Ensure graph_utils can be imported
cd /Users/sensiloles/Documents/work/telegram-bot-stack
python3 -c "from .project-graph.utils.graph_utils import load_router"
```

## Roadmap

### v1.1 (Current)
- ✅ MCP server implementation
- ✅ Basic resource exposure
- ✅ Analysis tools

### v1.2 (Planned)
- 🔄 Auto-update graphs on file changes
- 🔄 Graph visualization via MCP
- 🔄 Diff analysis between commits

### v1.3 (Future)
- ⏳ Multi-repository support
- ⏳ Real-time dependency tracking
- ⏳ Breaking change detection

## References

- **Graph System:** `.project-graph/README.md`
- **Graph Utils:** `.project-graph/utils/graph_utils.py`
- **MCP Spec:** https://modelcontextprotocol.io/
- **Cursor MCP:** https://docs.cursor.com/context/model-context-protocol

---

**💡 Start using:** Load `graph://router` to see all available graphs!
