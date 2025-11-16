# GitHub Workflows Scripts

Automation scripts for GitHub workflows and issue management.

## 📋 Scripts Overview

### Cloud Agent Scripts

Scripts for automated issue management via Cloud Agent:

- **`auto_label.py`** - Automatic issue labeling based on content
- **`generate_subtasks.py`** - Break down issues into subtasks
- **`add_acceptance_criteria.py`** - Generate acceptance criteria for issues
- **`analyze_context.py`** - Analyze codebase context for issues
- **`parse_command.py`** - Parse slash commands in issue comments
- **`execute_command.py`** - Execute parsed commands

### Issue Management Scripts

#### `read_issues.py` - GitHub Issues Reader

Read and manage GitHub issues from command line or workflows.

**Features:**

- ✅ Read specific issues by number
- ✅ List issues with filters (state, labels)
- ✅ JSON export for automation
- ✅ Works with GitHub CLI or API
- ✅ Auto-detects repository from git

**Usage:**

```bash
# Read specific issue
python .github/workflows/scripts/read_issues.py 1

# List all open issues
python .github/workflows/scripts/read_issues.py --list

# List issues with labels
python .github/workflows/scripts/read_issues.py --list --labels "refactor"

# Export to JSON
python .github/workflows/scripts/read_issues.py 1 --json
```

**Command Line Options:**

```bash
usage: read_issues.py [-h] [--list] [--state {open,closed,all}]
                      [--labels LABELS] [--limit LIMIT] [--repo REPO]
                      [--json] [--brief]
                      [issue_number]

Options:
  issue_number          Issue number to read
  --list               List issues instead of reading specific one
  --state              Filter by state: open, closed, all (default: open)
  --labels LABELS      Filter by labels (comma-separated)
  --limit LIMIT        Max issues to list (default: 30)
  --repo REPO          Repository in format owner/repo (auto-detected)
  --json               Output raw JSON
  --brief              Show brief output without full body
```

**Authentication:**

The script supports multiple authentication methods:

1. **GitHub CLI** (recommended):

   ```bash
   gh auth login
   ```

2. **Environment Variable**:

   ```bash
   export GITHUB_TOKEN="your_token_here"
   ```

3. **From .env**:
   ```bash
   source .env
   export GITHUB_TOKEN=$GITHUB_TOKEN
   ```

**Examples:**

```bash
# Get issue with full details
python .github/workflows/scripts/read_issues.py 1

# Get brief summary
python .github/workflows/scripts/read_issues.py 1 --brief

# List all open issues
python .github/workflows/scripts/read_issues.py --list

# List closed issues
python .github/workflows/scripts/read_issues.py --list --state closed

# Filter by multiple labels
python .github/workflows/scripts/read_issues.py --list --labels "bug,priority:high"

# Export to JSON for processing
python .github/workflows/scripts/read_issues.py 1 --json | jq '.title'

# List issues from specific repo
python .github/workflows/scripts/read_issues.py --list --repo "owner/repo"
```

**Use in Workflows:**

```yaml
- name: Read issue
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    python .github/workflows/scripts/read_issues.py ${{ github.event.issue.number }} --json
```

## 🔧 Development

### Requirements

- Python 3.9+
- GitHub CLI (`gh`) - optional but recommended
- Environment variable `GITHUB_TOKEN` for API access

### Adding New Scripts

When adding new scripts:

1. Add shebang: `#!/usr/bin/env python3`
2. Make executable: `chmod +x script_name.py`
3. Add comprehensive docstring
4. Update this README
5. Follow project code style (ruff)

### Testing Scripts Locally

```bash
# Install dependencies
pip install -e .

# Test script help
python .github/workflows/scripts/read_issues.py --help

# Test with different auth methods
gh auth status  # Check gh CLI
echo $GITHUB_TOKEN  # Check token
```

## 📚 Script Details

### Cloud Agent Workflow

The Cloud Agent scripts work together in the following flow:

1. **Issue/Comment Event** → Trigger workflow
2. **`parse_command.py`** → Detect slash commands
3. **`execute_command.py`** → Route to appropriate handler
4. **Handler Scripts** → Process request:
   - `auto_label.py` - Add labels
   - `generate_subtasks.py` - Create subtasks
   - `add_acceptance_criteria.py` - Add criteria
   - `analyze_context.py` - Analyze code context

### Issue Reader Workflow

The `read_issues.py` script can be used:

1. **Standalone** - Command line tool for manual issue management
2. **In Workflows** - Automated issue processing
3. **With Other Tools** - JSON export for integration

## 🚀 Usage in Workflows

### Example: Process New Issues

```yaml
name: Process New Issue

on:
  issues:
    types: [opened]

jobs:
  process:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Read issue details
        id: issue
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          ISSUE_DATA=$(python .github/workflows/scripts/read_issues.py \
            ${{ github.event.issue.number }} --json)
          echo "title=$(echo $ISSUE_DATA | jq -r '.title')" >> $GITHUB_OUTPUT

      - name: Process issue
        run: |
          echo "Processing issue: ${{ steps.issue.outputs.title }}"
```

### Example: Generate Issue Report

```yaml
name: Weekly Issue Report

on:
  schedule:
    - cron: "0 9 * * 1" # Every Monday at 9am

jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate report
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python .github/workflows/scripts/read_issues.py --list \
            --state all --limit 100 --json > issues_report.json

          # Process report...
```

## 🐛 Troubleshooting

### Common Issues

**"Could not detect repository"**

```bash
# Specify repository explicitly
python .github/workflows/scripts/read_issues.py --list --repo "owner/repo"
```

**"API request failed: 401"**

```bash
# Authenticate
gh auth login
# OR
export GITHUB_TOKEN="your_token"
```

**"Issue not found"**

```bash
# Verify issue exists
python .github/workflows/scripts/read_issues.py --list
```

## 🔒 Security

- Never commit `GITHUB_TOKEN` or credentials
- Use GitHub Secrets in workflows
- Respect API rate limits (5000 requests/hour authenticated)
- Use GitHub CLI for better rate limits and caching

## 📖 Documentation

- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [GitHub REST API](https://docs.github.com/en/rest)
- [GitHub Actions](https://docs.github.com/en/actions)

---

**Note**: All scripts respect `.gitignore` and `.cursorignore` settings. Sensitive data should never be committed.
