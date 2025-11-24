#!/bin/bash
# Setup script for MCP GitHub server configuration
# Usage: bash scripts/setup_mcp.sh [--restore]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# Use relative path from .cursor/mcp.json to scripts/mcp_github_server.py
MCP_SERVER_RELATIVE_PATH="scripts/mcp_github_server.py"
CURSOR_CONFIG_DIR="$PROJECT_ROOT/.cursor"
CURSOR_CONFIG="$CURSOR_CONFIG_DIR/mcp.json"

# Check for restore flag
RESTORE_MODE=false
if [[ "$1" == "--restore" ]]; then
    RESTORE_MODE=true
fi

if [ "$RESTORE_MODE" = true ]; then
    echo "🔄 Restoring MCP GitHub server configuration..."
else
    echo "🔧 Setting up MCP GitHub server configuration..."
fi

# Check if MCP server exists (using absolute path for check)
MCP_SERVER_ABSOLUTE_PATH="$PROJECT_ROOT/$MCP_SERVER_RELATIVE_PATH"
if [ ! -f "$MCP_SERVER_ABSOLUTE_PATH" ]; then
    echo "❌ Error: MCP server not found at $MCP_SERVER_ABSOLUTE_PATH"
    exit 1
fi

# Create Cursor config directory if it doesn't exist
mkdir -p "$CURSOR_CONFIG_DIR"

# Check if config already exists and is valid
if [ -f "$CURSOR_CONFIG" ]; then
    # Check if file is empty or contains only empty JSON object
    if [ ! -s "$CURSOR_CONFIG" ] || [ "$(cat "$CURSOR_CONFIG" | python3 -m json.tool 2>/dev/null | grep -c 'github-issues')" -eq 0 ]; then
        echo "⚠️  Configuration file exists but is empty or invalid"
        if [ "$RESTORE_MODE" = false ]; then
            echo "   Backing up to ${CURSOR_CONFIG}.backup"
            cp "$CURSOR_CONFIG" "${CURSOR_CONFIG}.backup" 2>/dev/null || true
        fi
    elif [ "$RESTORE_MODE" = false ]; then
        echo "✅ Valid configuration already exists at $CURSOR_CONFIG"
        echo "   Skipping recreation. Use --restore to force restore."
        exit 0
    fi
fi

# Try to detect repository from git
GITHUB_REPO=""
if command -v git >/dev/null 2>&1; then
    if [ -d "$PROJECT_ROOT/.git" ]; then
        REMOTE_URL=$(git -C "$PROJECT_ROOT" remote get-url origin 2>/dev/null || echo "")
        if [ -n "$REMOTE_URL" ] && echo "$REMOTE_URL" | grep -q "github.com"; then
            # Parse repository name from different URL formats
            REMOTE_URL="${REMOTE_URL%.git}"  # Remove .git suffix
            if echo "$REMOTE_URL" | grep -q "git@github.com:"; then
                # SSH format: git@github.com:owner/repo
                GITHUB_REPO=$(echo "$REMOTE_URL" | sed 's|git@github.com:||')
            elif echo "$REMOTE_URL" | grep -q "github.com/"; then
                # HTTPS format: https://github.com/owner/repo
                GITHUB_REPO=$(echo "$REMOTE_URL" | sed 's|.*github.com/||')
            fi
        fi
    fi
fi

# Detect absolute path to MCP servers
MCP_GITHUB_ABSOLUTE="$PROJECT_ROOT/$MCP_SERVER_RELATIVE_PATH"
MCP_GRAPH_RELATIVE="scripts/mcp_project_graph.py"
MCP_GRAPH_ABSOLUTE="$PROJECT_ROOT/$MCP_GRAPH_RELATIVE"

# Detect repository (for .env file suggestion)
if [ -n "$GITHUB_REPO" ]; then
    echo "📦 Detected repository: $GITHUB_REPO"
fi

# Create unified configuration (both servers, no env variables)
cat > "$CURSOR_CONFIG" << EOF
{
  "mcpServers": {
    "github-workflow": {
      "command": "python3",
      "args": [
        "$MCP_GITHUB_ABSOLUTE"
      ],
      "description": "GitHub workflow management (issues, PRs, CI)"
    },
    "project-graph": {
      "command": "python3",
      "args": [
        "$MCP_GRAPH_ABSOLUTE"
      ],
      "description": "Project graph navigation"
    }
  }
}
EOF

echo "✅ Configuration created at $CURSOR_CONFIG"
echo ""
echo "📝 Next steps:"
echo "   1. Add to .env file:"
if [ -n "$GITHUB_REPO" ]; then
    echo "      echo 'GITHUB_TOKEN=your_token_here' >> .env"
    echo "      echo 'GITHUB_REPO=$GITHUB_REPO' >> .env"
else
    echo "      echo 'GITHUB_TOKEN=your_token_here' >> .env"
    echo "      echo 'GITHUB_REPO=owner/repo' >> .env"
fi
echo "   2. Restart Cursor"
echo "   3. Test by asking: 'List all open GitHub issues'"
echo ""
echo "💡 MCP servers configured:"
echo "   • github-workflow: GitHub issues, PRs, CI"
echo "   • project-graph: Project navigation"
echo ""
echo "🔒 Security: GITHUB_TOKEN and GITHUB_REPO read from .env file"
