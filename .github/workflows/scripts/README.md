# GitHub Automation Scripts

Modern PyGithub-based automation scripts for GitHub workflow management.

## Quick Start

All scripts automatically load `GITHUB_TOKEN` from `.env` or environment.

```bash
# Token in .env (recommended)
echo "GITHUB_TOKEN=your_token_here" > .env

# Or export to environment
export GITHUB_TOKEN=your_token
```

## Core Scripts

### Issue Management

**read_issues.py** - Read and list issues

```bash
# List open issues
python3 .github/workflows/scripts/read_issues.py --list

# Get specific issue
python3 .github/workflows/scripts/read_issues.py 4

# Filter by state/labels
python3 .github/workflows/scripts/read_issues.py --list --state closed
python3 .github/workflows/scripts/read_issues.py --list --labels bug,priority:high

# JSON export
python3 .github/workflows/scripts/read_issues.py 4 --json > issue.json
```

**create_issue.py** - Create GitHub issues

```bash
# From markdown file
python3 .github/workflows/scripts/create_issue.py \
    --title "Bug: Fix tests" \
    --file /tmp/issue.md \
    --labels bug,priority:high

# From stdin
echo "Issue description" | python3 .github/workflows/scripts/create_issue.py \
    --title "Feature request"

# Dry run
python3 .github/workflows/scripts/create_issue.py \
    --title "Test" \
    --file issue.md \
    --dry-run
```

**update_issue.py** - Update issue labels, priority, state

```bash
# Change priority
python3 .github/workflows/scripts/update_issue.py 31 --set-priority low

# Add labels
python3 .github/workflows/scripts/update_issue.py 31 --add-labels blocked,needs-review

# Remove labels
python3 .github/workflows/scripts/update_issue.py 31 --remove-labels priority:high

# Replace all labels
python3 .github/workflows/scripts/update_issue.py 31 --set-labels bug,priority:critical

# Close issue with comment
python3 .github/workflows/scripts/update_issue.py 31 --close --comment "Fixed in #42"

# Multiple operations
python3 .github/workflows/scripts/update_issue.py 31 \
    --remove-labels priority:high \
    --add-labels priority:low,blocked \
    --comment "Blocked by core features"

# Dry run
python3 .github/workflows/scripts/update_issue.py 31 --set-priority low --dry-run
```

**link_issues.py** - Link issues with dependencies

```bash
# Mark issue as blocked by others
python3 .github/workflows/scripts/link_issues.py 31 --blocked-by 27,28,29

# Mark issue as blocking another
python3 .github/workflows/scripts/link_issues.py 27 --blocks 31

# Create bidirectional link
python3 .github/workflows/scripts/link_issues.py 31 --blocked-by 27 --bidirectional

# Add related issues (no dependency)
python3 .github/workflows/scripts/link_issues.py 31 --related-to 19,20

# With custom message
python3 .github/workflows/scripts/link_issues.py 31 \
    --blocked-by 27,28,29 \
    --comment "Waiting for core VPS deployment features"

# Dry run
python3 .github/workflows/scripts/link_issues.py 31 --blocked-by 27,28 --dry-run
```

### Pull Request Management

**create_pr.py** - Create pull requests

```bash
# Auto-detect branch, auto-generate description
python3 .github/workflows/scripts/create_pr.py \
    --title "feat(storage): add Redis backend"

# Link to issue (adds "Closes #42" automatically)
python3 .github/workflows/scripts/create_pr.py \
    --title "fix(auth): token validation" \
    --closes 42

# Draft PR
python3 .github/workflows/scripts/create_pr.py \
    --title "feat(api): WIP new endpoint" \
    --draft

# Dry run
python3 .github/workflows/scripts/create_pr.py \
    --title "feat: test" \
    --dry-run
```

**merge_pr.py** - Merge PRs (one command)

```bash
# Merge current branch's PR (auto-detect)
python3 .github/workflows/scripts/merge_pr.py

# Merge and delete both local and remote branches
python3 .github/workflows/scripts/merge_pr.py --cleanup

# Merge specific PR
python3 .github/workflows/scripts/merge_pr.py --pr 42

# Dry run
python3 .github/workflows/scripts/merge_pr.py --dry-run
```

**check_ci.py** - Check CI status

```bash
# Check PR CI status
python3 .github/workflows/scripts/check_ci.py --pr 5

# Check specific commit
python3 .github/workflows/scripts/check_ci.py --commit abc123

# Check branch
python3 .github/workflows/scripts/check_ci.py --branch main

# List recent PRs with CI status
python3 .github/workflows/scripts/check_ci.py --list-prs

# JSON output
python3 .github/workflows/scripts/check_ci.py --pr 5 --json
```

**pr_ready.py** - Check if PR is ready to merge

```bash
# Check all requirements
python3 .github/workflows/scripts/pr_ready.py --pr 5

# Quiet mode (exit code only)
python3 .github/workflows/scripts/pr_ready.py --pr 5 --quiet

# Returns:
# - 0 if ready to merge
# - 1 if not ready
```

### Project Status

**project_overview.py** - Quick project snapshot

```bash
# Quick overview
python3 .github/workflows/scripts/project_overview.py

# Detailed overview
python3 .github/workflows/scripts/project_overview.py --detailed

# Shows:
# - Git status and branch
# - Test coverage
# - Open PRs with CI status
# - Open issues
# - Quick command reference
```

## Helper Modules

### github_helper.py

Core module with reusable functions:

```python
from github_helper import get_repo, get_github_client

# Get repository (auto-detected from git)
repo = get_repo()

# Or specify explicitly
repo = get_repo("sensiloles/telegram-bot-stack")

# Get authenticated client
gh = get_github_client()

# List issues
for issue in repo.get_issues(state='open'):
    print(f"#{issue.number}: {issue.title}")

# Create issue
issue = repo.create_issue(
    title="Bug: Something broke",
    body="Detailed description...",
    labels=["bug", "priority:high"]
)
```

**Functions:**

- `load_token()` - Load token from .env or environment
- `get_github_client()` - Get authenticated Github client
- `get_repo()` - Get Repository object
- `get_repo_from_git()` - Auto-detect repo from git remote
- `format_issue_list()` - Format issues for display
- `format_issue_detail()` - Format single issue with details

## Script Details

### Auto-Label Scripts

**auto_label.py** - Auto-label issues (used in cloud-agent workflow)

Analyzes issue content and automatically applies appropriate labels based on keywords.

**add_acceptance_criteria.py** - Generate acceptance criteria

Adds comprehensive acceptance criteria checklists to feature/refactor issues.

**generate_subtasks.py** - Break down complex issues

Creates subtask issues for epics and complex features.

### Analysis Scripts

**analyze_context.py** - Analyze repository context

Finds related files and similar issues for better context.

**analyze_pr.py** - Analyze pull request changes

Reviews PR changes and provides automated analysis.

### Command Processing

**parse_command.py** - Parse slash commands in comments

Parses commands like `/breakdown`, `/accept`, `/estimate` from issue comments.

**execute_command.py** - Execute parsed commands

Executes the parsed commands and performs appropriate actions.

## Common Patterns

### For Cursor Agent

```bash
# 1. Check current phase
python3 .github/workflows/scripts/read_issues.py --list --state open

# 2. Read active issue
python3 .github/workflows/scripts/read_issues.py 4

# 3. Create new phase issue
cat > /tmp/issue_content.md << 'EOF'
## Phase Description
...
EOF

python3 .github/workflows/scripts/create_issue.py \
    --title "[Phase] Phase X: Name" \
    --file /tmp/issue_content.md \
    --labels "phase:X,enhancement"

# 4. Create PR after work
python3 .github/workflows/scripts/create_pr.py \
    --title "feat(storage): add Redis backend" \
    --closes 42

# 5. Check CI status
python3 .github/workflows/scripts/check_ci.py --pr 5

# 6. Merge when ready
python3 .github/workflows/scripts/merge_pr.py
```

### For Automation

```bash
# Export all open issues to JSON
python3 .github/workflows/scripts/read_issues.py --list --json > issues.json

# Create issue from pipeline
python3 generate_report.py | \
    python3 .github/workflows/scripts/create_issue.py \
        --title "Weekly Report" \
        --labels report

# Wait for CI before merge
if python3 .github/workflows/scripts/pr_ready.py --pr 5 --quiet; then
    python3 .github/workflows/scripts/merge_pr.py --pr 5
else
    echo "PR not ready"
    exit 1
fi

# Get CI status in scripts
CI_STATUS=$(python3 .github/workflows/scripts/check_ci.py --pr 5 --json | jq -r '.status')
```

## Setup

### 1. Install Dependencies

```bash
pip install PyGithub
```

Or let scripts auto-install.

### 2. Configure Token

Create `.env` in workspace root:

```bash
GITHUB_TOKEN=your_github_token_here
```

### 3. Token Permissions

Required scopes:

- `repo` - Full repository access
- For public repos: `public_repo` is enough

## Features

- ✅ Automatic token loading from `.env`
- ✅ Auto-detect repository from git remote
- ✅ Proper error handling with helpful messages
- ✅ Type hints for better IDE support
- ✅ Auto-installs PyGithub if missing
- ✅ JSON output for automation
- ✅ Dry-run mode for testing
- ✅ Exit codes for scripting

## Exit Codes

- `0` - Success
- `1` - Error (operation failed, validation failed)
- `2` - Usage error (missing arguments, invalid options)

## Troubleshooting

### "GITHUB_TOKEN not found"

Create `.env` file:

```bash
echo "GITHUB_TOKEN=your_token_here" > .env
```

Or export:

```bash
export GITHUB_TOKEN=your_token
```

### "401 Unauthorized"

Token is invalid or expired. Generate new token with correct scopes.

### "404 Not Found"

Repository doesn't exist or you don't have access. Check repository name format: `owner/repo`

### "Could not detect repository"

Not in git repository. Use `--repo owner/repo` explicitly or run from workspace root.

### Import errors

Install dependencies:

```bash
pip install -e ".[dev,github-actions]"
```

## Documentation

- **Full Guide:** `.github/docs/scripts.md`
- **PR Automation:** `.github/PR_AUTOMATION.md`
- **Git Workflow:** `.github/docs/workflow/git-flow.md`
- **Agent Rules:** `.cursorrules`

## Migration from gh CLI

**Old (gh CLI):**

```bash
gh issue list
gh issue view 4
gh pr create --title "feat: add feature"
```

**New (PyGithub):**

```bash
python3 .github/workflows/scripts/read_issues.py --list
python3 .github/workflows/scripts/read_issues.py 4
python3 .github/workflows/scripts/create_pr.py --title "feat: add feature"
```

**Why PyGithub?**

- ✅ Works reliably with personal access tokens
- ✅ No GraphQL permission issues
- ✅ Better error messages
- ✅ Programmatic API for complex operations

---

**Need help?** Run any script with `--help` flag:

```bash
python3 .github/workflows/scripts/create_pr.py --help
```
