#!/bin/bash
# Quick GitHub Issue Creator using GitHub CLI

set -e

echo "🤖 Quick GitHub Issue Creator"
echo "=============================="
echo ""

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed"
    echo "Install it with: brew install gh"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "🔐 GitHub CLI authentication required"
    echo ""
    echo "Starting authentication process..."
    echo "Please follow the prompts to authenticate with GitHub"
    echo ""
    gh auth login
fi

echo "✅ Authenticated with GitHub"
echo ""

# Read the issue draft
DRAFT_FILE=".github/FIRST_ISSUE_DRAFT.md"

if [ ! -f "$DRAFT_FILE" ]; then
    echo "❌ Draft file not found: $DRAFT_FILE"
    exit 1
fi

echo "📝 Creating issue from draft..."
echo ""

# Create issue using gh CLI
gh issue create \
    --title "[Refactor] Phase 0.1: Extract Reusable Components into src/core/" \
    --body-file "$DRAFT_FILE" \
    --label "refactor,component:bot,priority:high"

echo ""
echo "✅ Issue created successfully!"
echo ""
echo "🎯 Next steps:"
echo "1. Visit the issue URL above"
echo "2. Try Cloud Agent commands in comments:"
echo "   /breakdown - Break into subtasks"
echo "   /accept - Generate acceptance criteria"
echo "   /estimate - Get time estimate"
echo ""
echo "🎉 Done!"
