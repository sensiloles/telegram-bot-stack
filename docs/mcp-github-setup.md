# MCP GitHub Issues Setup

Quick setup guide for the custom MCP server that provides GitHub issue management in Cursor.

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
    "github-issues": {
      "command": "python3",
      "args": ["scripts/mcp_github_server.py"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}",
        "GITHUB_REPO": "owner/repo"
      }
    }
  }
}
```

**Note:** Paths are relative to the project root directory.

**Note:** The setup script automatically detects the repository from git and creates this configuration.

## Available Tools

- **`list_issues`** - List issues with filters (`state`, `labels`, `limit`, `repo`)
- **`get_issue`** - Get issue details (`issue_number`, `repo`)
- **`create_issue`** - Create new issue (`title`, `body`, `labels`, `assignees`, `repo`)
- **`update_issue`** - Update issue (`issue_number`, `set_priority`, `add_labels`, `remove_labels`, `set_labels`, `comment`, `close`, `reopen`, `repo`)

## Usage Examples

```
Show me all open issues
What's the status of issue #40?
Create a new issue titled "Bug: Fix tests" with label bug
Update issue #40 to high priority
Add a comment to issue #40 saying "Working on this"
Close issue #40
```

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

1. Verify token is in `.env` file: `GITHUB_TOKEN=your_token`
2. Check token has required scopes (`repo` or `public_repo`)
3. Restart Cursor after updating token

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
