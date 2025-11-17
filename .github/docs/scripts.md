# GitHub Automation Scripts

Modern PyGithub-based scripts for GitHub automation.

## 🚀 Quick Start

All scripts automatically load `GITHUB_TOKEN` from `.env` or environment.

### Read Issues

```bash
# List open issues
python3 .github/workflows/scripts/read_issues.py --list

# Get specific issue details
python3 .github/workflows/scripts/read_issues.py 4

# List with filters
python3 .github/workflows/scripts/read_issues.py --list --state closed
python3 .github/workflows/scripts/read_issues.py --list --labels bug,priority:high

# JSON export
python3 .github/workflows/scripts/read_issues.py 4 --json > issue.json
```

### Create Issue

```bash
# From markdown file
python3 .github/workflows/scripts/create_issue.py \
    --title "Bug: Fix tests" \
    --file /tmp/issue.md \
    --labels bug,priority:high

# From stdin
echo "Issue description" | python3 .github/workflows/scripts/create_issue.py \
    --title "Feature request"

# Interactive (type description, Ctrl+D when done)
python3 .github/workflows/scripts/create_issue.py --title "New feature"

# Dry run (preview without creating)
python3 .github/workflows/scripts/create_issue.py --title "Test" --file issue.md --dry-run
```

### Create Pull Request

```bash
# Auto-detect branch, auto-generate description from commits
python3 .github/workflows/scripts/create_pr.py \
    --title "feat(storage): add Redis backend"

# Link to issue (adds "Closes #42" automatically)
python3 .github/workflows/scripts/create_pr.py \
    --title "fix(auth): resolve token validation" \
    --closes 42

# Custom description from file
python3 .github/workflows/scripts/create_pr.py \
    --title "feat(bot): add webhooks" \
    --file pr_description.md

# Draft PR (for work in progress)
python3 .github/workflows/scripts/create_pr.py \
    --title "feat(api): WIP new endpoint" \
    --draft

# Custom base branch (default is 'main')
python3 .github/workflows/scripts/create_pr.py \
    --title "feat: feature" \
    --base develop

# Dry run (preview PR without creating)
python3 .github/workflows/scripts/create_pr.py \
    --title "feat: test" \
    --dry-run
```

**Features:**

- ✅ Auto-detects current branch
- ✅ Validates conventional commit format
- ✅ Auto-generates description from commits
- ✅ Links issues with `--closes N`
- ✅ Supports draft PRs
- ✅ Dry-run mode for preview

### Check CI Status

```bash
# Check PR CI status
python3 .github/workflows/scripts/check_ci.py --pr 5

# Check specific commit
python3 .github/workflows/scripts/check_ci.py --commit abc123

# Check latest commit on branch
python3 .github/workflows/scripts/check_ci.py --branch main

# List recent open PRs with CI status
python3 .github/workflows/scripts/check_ci.py --list-prs

# List all PRs (open and closed)
python3 .github/workflows/scripts/check_ci.py --list-prs --state all

# JSON output (for automation)
python3 .github/workflows/scripts/check_ci.py --pr 5 --json
```

**Features:**

- ✅ Check CI status for PRs
- ✅ Check CI status for commits
- ✅ Check CI status for branches
- ✅ List recent PRs with status
- ✅ JSON output for automation
- ✅ Shows check duration
- ✅ Exit code 1 if checks failing

**Requirements:**

- Classic token with `repo` scope (for check runs access)
- Or fine-grained token with `Commit statuses: Read` permission

## 📚 Module: `github_helper.py`

Unified GitHub API helper for all scripts.

```python
from github_helper import get_repo, get_github_client

# Get repository (auto-detected from git)
repo = get_repo()

# Or specify explicitly
repo = get_repo("sensiloles/telegram-bot-stack")

# Get authenticated client
gh = get_github_client()
user = gh.get_user()
print(f"Authenticated as: {user.login}")

# List issues
for issue in repo.get_issues(state='open'):
    print(f"#{issue.number}: {issue.title}")

# Create issue
issue = repo.create_issue(
    title="Bug: Something broke",
    body="Detailed description...",
    labels=["bug", "priority:high"]
)
print(f"Created: {issue.html_url}")
```

### Features

- ✅ Automatic token loading from `.env`
- ✅ Auto-detect repository from git remote
- ✅ Proper error handling with helpful messages
- ✅ Type hints for better IDE support
- ✅ Auto-installs PyGithub if missing

## 🔧 Setup

### 1. Install Dependencies

```bash
pip install PyGithub
```

Or let the scripts auto-install it.

### 2. Configure Token

Create `.env` in workspace root:

```bash
GITHUB_TOKEN=your_github_token_here
```

Or export to environment:

```bash
export GITHUB_TOKEN=your_token
```

### 3. Token Permissions

Your token needs:

- `repo` scope (full repository access)
- For public repos: `public_repo` scope is enough

## 📖 Script Reference

### `github_helper.py`

Core module with reusable functions:

- `load_token()` - Load token from .env or environment
- `get_github_client()` - Get authenticated Github client
- `get_repo()` - Get Repository object
- `get_repo_from_git()` - Auto-detect repo from git remote
- `format_issue_list()` - Format issues for display
- `format_issue_detail()` - Format single issue with details

### `read_issues.py`

Read and list GitHub issues:

- Get specific issue by number
- List issues with filters (state, labels)
- JSON export for automation
- Brief or detailed output

### `create_issue.py`

Create GitHub issues:

- From markdown file or stdin
- With labels, assignees, milestones
- Dry-run mode to preview
- Interactive mode

### `create_pr.py`

Create GitHub Pull Requests:

- Auto-detects current branch
- Validates conventional commit format
- Auto-generates description from commits
- Links to issues automatically
- Supports draft PRs
- Custom base branch support

### `check_ci.py`

Check GitHub Actions CI status:

- Check CI status for Pull Requests
- Check CI status for specific commits
- Check CI status for branches
- List recent PRs with CI status
- JSON output for automation
- Shows check duration and details

### `pr_ready.py`

Check if PR is ready to merge:

- Verify all CI checks passed
- Check for merge conflicts
- Verify PR approvals
- Check mergeable state
- Exit code for scripting (0 = ready, 1 = not ready)

### `project_overview.py`

Quick project status snapshot:

- Git status and branch info
- Test coverage summary
- Open PRs with CI status
- Open issues
- Quick command reference

## 🎯 Common Patterns

### For Cursor Agent

**Check current phase:**

```bash
python3 .github/workflows/scripts/read_issues.py --list --state open
```

**Read active issue:**

```bash
python3 .github/workflows/scripts/read_issues.py 4
```

**Create new phase issue:**

```bash
# 1. Write issue content to file
cat > /tmp/issue_content.md << 'EOF'
## Phase Description
...
EOF

# 2. Create issue
python3 .github/workflows/scripts/create_issue.py \
    --title "[Phase] Phase 1.1: Component Name" \
    --file /tmp/issue_content.md \
    --labels "phase-1,enhancement"
```

**Create Pull Request:**

```bash
# After committing and pushing feature branch
python3 .github/workflows/scripts/create_pr.py \
--title "feat(storage): add Redis backend" \
--closes 42
```

**Check CI Status:**

```bash
# Check if PR is ready to merge
python3 .github/workflows/scripts/check_ci.py --pr 5

# Check PR readiness (all checks)
python3 .github/workflows/scripts/pr_ready.py --pr 5

# Project overview
python3 .github/workflows/scripts/project_overview.py
```

### For Automation

**Export all open issues to JSON:**

```bash
python3 .github/workflows/scripts/read_issues.py --list --json > issues.json
```

**Create issue from pipeline:**

```bash
python3 generate_report.py | python3 .github/workflows/scripts/create_issue.py \
    --title "Weekly Report" \
    --labels report
```

## 🔄 Migration from Old Scripts

**Old way (gh CLI):**

```bash
gh issue list
gh issue view 4
gh issue create --title "Bug" --body "..."
```

**New way (PyGithub):**

```bash
python3 .github/workflows/scripts/read_issues.py --list
python3 .github/workflows/scripts/read_issues.py 4
echo "..." | python3 .github/workflows/scripts/create_issue.py --title "Bug"
```

**Why PyGithub?**

- ✅ Works reliably with personal access tokens
- ✅ No GraphQL permission issues
- ✅ Better error messages
- ✅ Programmatic API for complex operations
- ✅ Proven to work (successfully created Issues #1, #2, #3, #4)

## 💡 Tips

1. **Token in .env**: Keep token in `.env` (it's in `.gitignore`)
2. **Auto-detection**: Scripts auto-detect repo from git remote
3. **JSON mode**: Use `--json` for automation/parsing
4. **Dry run**: Test with `--dry-run` before creating issues
5. **Labels**: Separate labels with commas: `bug,priority:high`

## 🐛 Troubleshooting

**"GITHUB_TOKEN not found"**

- Check `.env` file exists and contains `GITHUB_TOKEN=...`
- Or export: `export GITHUB_TOKEN=your_token`

**"401 Unauthorized"**

- Token is invalid or expired
- Token needs `repo` scope

**"404 Not Found"**

- Repository doesn't exist or you don't have access
- Check repository name format: `owner/repo`

**"Could not detect repository"**

- Not in git repository
- Use `--repo owner/repo` explicitly

## 🔗 Related Files

- `.github/PROJECT_STATUS.md` - Project status and workflow
- `.github/HOW_TO_CREATE_ISSUES.md` - Deprecated (use this guide)
- `.cursorrules` - Agent workflow rules
