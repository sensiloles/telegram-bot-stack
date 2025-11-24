# MCP GitHub Workflow Setup

Quick setup guide for the enhanced MCP server that provides comprehensive GitHub workflow management in Cursor.

**Version:** 2.0.0 (Enhanced with PR Management & Batch Operations)

## Quick Setup

1. **Run setup script:**

   ```bash
   bash scripts/setup_mcp.sh
   ```

2. **Add credentials to .env file:**

   ```bash
   # Add to .env file
   echo "GITHUB_TOKEN=your_token_here" >> .env
   echo "GITHUB_REPO=owner/repo" >> .env
   ```

3. **Restart Cursor**

4. **Test:**
   In Cursor chat, ask: "List all open GitHub issues"

## Configuration Priority

Cursor reads MCP configuration in this order (according to [official docs](https://docs.cursor.com/context/mcp)):

1. **Workspace config** (`.cursor/mcp.json`) - **Highest priority** ✅
2. **Global config** (`~/.cursor/mcp.json`) - Lower priority

**Additionally supported:**

- **VS Code settings** (`.vscode/settings.json`) with `cursor.mcp.servers` key - Alternative approach

**Why workspace config?**

- ✅ **Project isolation** - Each project has its own MCP servers
- ✅ **Team sharing** - Can be committed to repository (add to `.gitignore` if sensitive)
- ✅ **Auto-priority** - Overrides global config automatically
- ✅ **No global pollution** - Doesn't affect other Cursor projects

## Manual Configuration

### Option 1: Workspace config (Recommended)

Create `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "github-workflow": {
      "command": "python3",
      "args": ["/absolute/path/to/scripts/mcp_github_server.py"],
      "description": "GitHub workflow management (issues, PRs, CI)"
    },
    "project-graph": {
      "command": "python3",
      "args": ["/absolute/path/to/scripts/mcp_project_graph.py"],
      "description": "Project graph navigation"
    }
  }
}
```

**Note:** Use absolute paths for reliability (setup script auto-detects them).

**For this project:**

```json
{
  "mcpServers": {
    "github-workflow": {
      "command": "python3",
      "args": [
        "/Users/sensiloles/Documents/work/telegram-bot-stack/scripts/mcp_github_server.py"
      ],
      "description": "GitHub workflow management (issues, PRs, CI)"
    },
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

### Option 2: VS Code settings (Alternative)

Add to `.vscode/settings.json`:

```json
{
  "cursor.mcp.servers": {
    "github-workflow": {
      "command": "python3",
      "args": ["${workspaceFolder}/scripts/mcp_github_server.py"],
      "description": "GitHub workflow management (issues, PRs, CI)"
    },
    "project-graph": {
      "command": "python3",
      "args": ["${workspaceFolder}/scripts/mcp_project_graph.py"],
      "description": "Project graph navigation"
    }
  }
}
```

**Note:** Uses `${workspaceFolder}` variable - works on any machine! Can be version controlled.

### Option 3: Global config (Not recommended)

Add to `~/.cursor/mcp.json` - applies to all Cursor projects.

**Security Note:** `GITHUB_TOKEN` and `GITHUB_REPO` are read from `.env` file automatically, not from MCP config (more secure).

## Available Tools

### Issue Management

- **`list_issues`** - List issues with advanced filters
  - Filters: `state`, `labels`, `milestone`, `assignee`, `sort`, `direction`, `since`, `limit`, `repo`
- **`get_issue`** - Get issue details (`issue_number`, `repo`)
- **`create_issue`** - Create new issue (`title`, `body`, `labels`, `assignees`, `repo`)
- **`update_issue`** - Update single issue (`issue_number`, `set_priority`, `add_labels`, `remove_labels`, `set_labels`, `comment`, `close`, `reopen`, `repo`)
- **`batch_update_issues`** - Update multiple issues at once (`issue_numbers`, `add_labels`, `remove_labels`, `comment`, `close`, `repo`)

### Pull Request Management

- **`create_pr`** - Create new Pull Request (`title`, `body`, `head`, `base`, `draft`, `closes_issue`, `repo`)
- **`merge_pr`** - Merge Pull Request (`pr_number`, `merge_method`, `delete_branch`, `repo`)
- **`list_prs`** - List Pull Requests (`state`, `sort`, `direction`, `limit`, `repo`)
- **`check_ci`** - Check CI/CD status (`pr_number` or `commit_sha`, `repo`)

## Usage Examples

### Issues

```
Show me all open issues
List issues with label "priority:high"
List issues assigned to me
What's the status of issue #40?
Create a new issue titled "Bug: Fix tests" with label bug
Update issue #40 to high priority
Add a comment to issue #40 saying "Working on this"
Close issue #40
Close issues #40, #41, #42 with comment "Completed in Sprint 1"
```

### Pull Requests

```
Create PR for current branch with title "feat(cli): add init command"
Create PR that closes issue #40
List all open PRs
Check CI status for PR #5
Merge PR #5 with squash method
Merge current branch's PR and delete the branch
```

### Advanced Filters

```
List issues updated in the last week
List issues in milestone "v2.0.0"
List PRs sorted by most recently updated
Check CI status for commit abc123
```

## How Authentication Works

**Security-First Approach:**

The MCP server automatically reads `GITHUB_TOKEN` and `GITHUB_REPO` from your `.env` file (not from MCP config). This means:

✅ **More Secure** - Credentials never stored in MCP config (which might be committed)
✅ **Simpler Setup** - Just add to `.env` once
✅ **Automatic Loading** - Server reads `.env` on startup
✅ **Unified Configuration** - All sensitive data in one place

**Loading Priority:**

1. Check environment variables (`GITHUB_TOKEN`, `GITHUB_REPO`)
2. If not found or placeholder → Read from `.env` file
3. If still not found → Error message

This happens automatically in `load_env_variables()` function.

## GitHub Token Requirements

Create a **Classic Personal Access Token** with:

- `repo` scope (for private repos) or `public_repo` (for public repos only)

Get token: https://github.com/settings/tokens/new

## Migration from Global to Workspace Config

If you previously used global config (`~/.cursor/mcp.json`), migrate to workspace-specific:

**Step 1:** Run setup script to create workspace config:

```bash
bash scripts/setup_mcp.sh
```

**Step 2:** Clear global config:

```bash
echo '{"mcpServers": {}}' > ~/.cursor/mcp.json
```

**Step 3:** Restart Cursor

**Step 4:** Verify MCP servers are **Enabled** in Settings → Tools & MCP → Installed MCP Servers

**Why clear global config?**

- Cursor prioritizes workspace config over global
- But if global has same server names, it can cause conflicts
- Empty global config ensures workspace config is always used

## Troubleshooting

### MCP Servers show as "Disabled"

**Cause:** Cursor is reading empty global config instead of workspace config.

**Solution:**

```bash
# Option 1: Clear global config (recommended)
echo '{"mcpServers": {}}' > ~/.cursor/mcp.json

# Option 2: Re-run setup script
bash scripts/setup_mcp.sh --restore

# Then restart Cursor
```

### Configuration becomes empty

If `.cursor/mcp.json` becomes empty, restore it:

```bash
bash scripts/setup_mcp.sh --restore
```

### Token not working

1. **Verify credentials in `.env` file** (project root):

   ```bash
   cat .env
   # Should contain:
   # GITHUB_TOKEN=ghp_...
   # GITHUB_REPO=owner/repo
   ```

2. **MCP server reads both from `.env` automatically** - no need to set environment variables

3. **Check token has required scopes** (`repo` or `public_repo`):

   - Visit: https://github.com/settings/tokens
   - Verify token exists and has correct permissions

4. **Restart Cursor** after updating `.env`

### Server not loading

1. Check Cursor logs: `Help` → `Toggle Developer Tools` → `Console`
2. Verify Python path: `which python3`
3. Test server manually: `python3 scripts/mcp_github_server.py`

## Files

- **Server:** `scripts/mcp_github_server.py`
- **Setup:** `scripts/setup_mcp.sh`
- **Config:** `.cursor/mcp.json` (auto-generated)

## Resources

- **MCP Protocol:** https://modelcontextprotocol.io/
- **GitHub Scripts:** `.github/workflows/scripts/README.md`
