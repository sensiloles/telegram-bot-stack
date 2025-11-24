# MCP GitHub Workflow Setup

Quick setup guide for the enhanced MCP server that provides comprehensive GitHub workflow management in Cursor.

**Version:** 2.0.0 (Enhanced with PR Management & Batch Operations)

## Quick Setup

1. **Run setup script:**

   ```bash
   bash scripts/setup_mcp.sh
   ```

2. **Ensure GitHub token is set:**

   ```bash
   # Add to .env file
   echo "GITHUB_TOKEN=your_token_here" >> .env
   ```

3. **Restart Cursor**

4. **Test:**
   In Cursor chat, ask: "List all open GitHub issues"

## Manual Configuration

If you prefer manual setup, create `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "github-workflow": {
      "command": "python3",
      "args": ["/absolute/path/to/scripts/mcp_github_server.py"],
      "env": {
        "GITHUB_REPO": "owner/repo"
      },
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

**Note:** Use absolute paths for reliability.

**Note:** `GITHUB_TOKEN` is read from `.env` file automatically, not from MCP config (more secure).

**Note:** The setup script automatically detects the repository from git and creates this configuration.

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

## How Token Authentication Works

**Security-First Approach:**

The MCP server automatically reads `GITHUB_TOKEN` from your `.env` file (not from MCP config). This means:

✅ **More Secure** - Token never stored in MCP config (which might be committed)
✅ **Simpler Setup** - Just add token to `.env` once
✅ **Automatic Loading** - Server reads `.env` on startup

**Token Priority:**

1. Check environment variable `GITHUB_TOKEN`
2. If not found or placeholder → Read from `.env` file
3. If still not found → Error message

This happens automatically in `load_token_from_env()` function.

## GitHub Token Requirements

Create a **Classic Personal Access Token** with:

- `repo` scope (for private repos) or `public_repo` (for public repos only)

Get token: https://github.com/settings/tokens/new

## Troubleshooting

### Configuration becomes empty

If `.cursor/mcp.json` becomes empty, restore it:

```bash
bash scripts/setup_mcp.sh --restore
```

### Token not working

1. **Verify token is in `.env` file** (project root):

   ```bash
   grep GITHUB_TOKEN .env
   # Should show: GITHUB_TOKEN=ghp_...
   ```

2. **MCP server reads token from `.env` automatically** - no need to set environment variables

3. **Check token has required scopes** (`repo` or `public_repo`):

   - Visit: https://github.com/settings/tokens
   - Verify token exists and has correct permissions

4. **Restart Cursor** after updating `.env` or MCP config

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
