#!/bin/bash
# Check MCP servers status and provide instructions
# Usage: bash scripts/check_mcp_status.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_NAME="telegram-bot-stack"

echo "🔍 Checking MCP servers status for $PROJECT_NAME..."
echo ""

# Check if MCP config exists
if [ ! -f "$PROJECT_ROOT/.cursor/mcp.json" ]; then
    echo "❌ MCP configuration not found!"
    echo "   Run: bash scripts/setup_mcp.sh"
    exit 1
fi

echo "✅ MCP configuration found: .cursor/mcp.json"

# Check if MCP servers exist
MCP_GITHUB="$PROJECT_ROOT/scripts/mcp_github_server.py"
MCP_GRAPH="$PROJECT_ROOT/scripts/mcp_project_graph.py"

if [ -f "$MCP_GITHUB" ]; then
    echo "✅ GitHub Workflow server: $MCP_GITHUB"
else
    echo "❌ GitHub Workflow server not found!"
fi

if [ -f "$MCP_GRAPH" ]; then
    echo "✅ Project Graph server: $MCP_GRAPH"
else
    echo "❌ Project Graph server not found!"
fi

echo ""
echo "📊 Testing MCP servers..."

# Test GitHub server
echo -n "   github-workflow: "
if python3 "$MCP_GITHUB" --version 2>&1 | grep -q "MCP" || python3 "$MCP_GITHUB" 2>&1 | grep -q "GITHUB_TOKEN"; then
    echo "✅ Ready"
else
    echo "⚠️  Check configuration"
fi

# Test Project Graph server
echo -n "   project-graph: "
if python3 "$MCP_GRAPH" --version 2>&1 | grep -q "MCP" || python3 "$MCP_GRAPH" 2>&1 | head -1 > /dev/null; then
    echo "✅ Ready"
else
    echo "⚠️  Check configuration"
fi

echo ""
echo "📝 Next steps:"
echo ""
echo "1. Open Cursor IDE"
echo "2. Go to: Settings → Tools & MCP → Installed MCP Servers"
echo "3. Enable both servers by clicking toggles:"
echo "   • github-workflow (9 tools)"
echo "   • project-graph (13 resources)"
echo ""
echo "4. Test in Cursor chat:"
echo "   'List all open GitHub issues'"
echo ""
echo "💡 Tip: Once enabled, Cursor remembers the state"
echo "   Servers will auto-start on next project open!"
echo ""

# Check if .env exists
if [ -f "$PROJECT_ROOT/.env" ]; then
    if grep -q "GITHUB_TOKEN" "$PROJECT_ROOT/.env" && grep -q "GITHUB_REPO" "$PROJECT_ROOT/.env"; then
        echo "✅ GitHub credentials configured in .env"
    else
        echo "⚠️  Add GitHub credentials to .env:"
        echo "   GITHUB_TOKEN=your_token"
        echo "   GITHUB_REPO=owner/repo"
    fi
else
    echo "⚠️  Create .env file with:"
    echo "   GITHUB_TOKEN=your_token"
    echo "   GITHUB_REPO=sensiloles/telegram-bot-stack"
fi

echo ""
echo "📚 Documentation:"
echo "   • MCP Setup: docs/mcp-github-setup.md"
echo "   • Project Graph: docs/mcp-project-graph-setup.md"
