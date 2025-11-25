# MCP Project Graph - Usage Guide

## 🚨 CRITICAL: Always Load Graph First!

**Before ANY work on this project, you MUST:**

```
1. fetch_mcp_resource: graph://recommend?task=<user_task>
2. fetch_mcp_resource: graph://<recommended_graph>
```

## Why This Matters

- **Token Efficiency:** Read 200-400 lines instead of 10,000+ lines
- **Focused Context:** Get only relevant code for your task
- **Faster Understanding:** Navigate codebase structure efficiently
- **Better Results:** Work with precise, task-specific information

## Available Graphs

| Graph              | URI                      | Use When                                                |
| ------------------ | ------------------------ | ------------------------------------------------------- |
| **Bot Framework**  | `graph://bot_framework`  | Adding features, storage backends, working with BotBase |
| **Infrastructure** | `graph://infrastructure` | CI/CD, GitHub automation, workflows                     |
| **Testing**        | `graph://testing`        | Writing tests, improving coverage, test structure       |
| **Documentation**  | `graph://docs`           | Updating docs, API reference                            |
| **Configuration**  | `graph://configuration`  | pyproject.toml, dependencies, build system              |
| **Examples**       | `graph://examples`       | Example bots, usage patterns                            |
| **Project Meta**   | `graph://project_meta`   | Architecture overview, cross-component understanding    |
| **Archive**        | `graph://archive`        | Historical context, deprecated features                 |

## Workflow

### Step 1: Get Recommendation

```
fetch_mcp_resource: graph://recommend?task=Continue work on issue #40 - CLI implementation
```

Response will suggest which graph to load.

### Step 2: Load Recommended Graph

```
fetch_mcp_resource: graph://bot_framework
```

### Step 3: Work with Focused Context

Now you have 200-400 lines of relevant, focused information instead of the entire codebase.

## Real Examples

### Example 1: Add Storage Backend

```
Task: "Add Redis storage backend"
→ graph://recommend?task=Add Redis storage backend
→ graph://bot_framework/storage
Result: Focused on storage module only (162 lines)
```

### Example 2: Fix CI/CD Issue

```
Task: "Fix merge_pr.py script"
→ graph://recommend?task=Fix merge_pr.py script
→ graph://infrastructure
Result: Focused on automation scripts (759 lines)
```

### Example 3: Write Tests

```
Task: "Add tests for new command"
→ graph://recommend?task=Add tests for new command
→ graph://testing
Result: Test structure and patterns (958 lines)
```

## Token Savings

| Approach          | Lines Read | Tokens  | Time |
| ----------------- | ---------- | ------- | ---- |
| **Without Graph** | 10,000+    | ~40,000 | Slow |
| **With Graph**    | 200-400    | ~1,600  | Fast |
| **Savings**       | 95%+       | 95%+    | 80%+ |

## Hierarchical Graphs

Some graphs have sub-graphs for even better focus:

### Bot Framework

- `graph://bot_framework/core` - BotBase, UserManager, AdminManager
- `graph://bot_framework/storage` - Storage backends
- `graph://bot_framework/utilities` - Decorators, helpers

## Integration with .cursorrules

The `.cursorrules` file now enforces this workflow:

**STEP 0 (MANDATORY):** Load MCP Project Graph FIRST
**Then:** Proceed with normal workflow

## If MCP Graph Fails

Fallback to traditional file reading, but you'll lose efficiency:

- Use `read_file` to read specific files
- Use `codebase_search` for semantic search
- Use `grep` for exact text search

## Maintenance

Update graphs when:

- Adding/removing modules in `telegram_bot_stack/`
- Changing automation scripts in `.github/workflows/scripts/`
- Restructuring tests
- Adding new documentation
- Changing build configuration

**Validation:**

```bash
cd .project-graph
python3 utils/graph_utils.py
```

## Support

- **Graph Router:** `.project-graph/graph-router.json`
- **Documentation:** `docs/mcp-project-graph-setup.md`
- **Issues:** Report via GitHub if graphs are out of date

---

**Remember:** MCP Project Graph is not optional - it's the most efficient way to work with this codebase.
