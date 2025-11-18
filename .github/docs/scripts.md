# GitHub Automation Scripts

> **📖 Main Documentation:** See [../workflows/scripts/README.md](../workflows/scripts/README.md) for complete script documentation.

This page provides quick reference and links.

## Script Location

All scripts are in: `.github/workflows/scripts/`

## Quick Reference

### Issue Management

```bash
# List issues
python3 .github/workflows/scripts/read_issues.py --list

# Read specific issue
python3 .github/workflows/scripts/read_issues.py 4

# Create issue
python3 .github/workflows/scripts/create_issue.py --title "Bug: Fix" --file issue.md
```

### Pull Requests

```bash
# Create PR
python3 .github/workflows/scripts/create_pr.py --title "feat: add feature" --closes 42

# Merge PR
python3 .github/workflows/scripts/merge_pr.py

# Check CI
python3 .github/workflows/scripts/check_ci.py --pr 5
```

### Project Status

```bash
# Quick overview
python3 .github/workflows/scripts/project_overview.py
```

## Available Scripts

| Script                       | Purpose                      | Quick Example                     |
| ---------------------------- | ---------------------------- | --------------------------------- |
| `read_issues.py`             | List and read issues         | `--list --state open`             |
| `create_issue.py`            | Create GitHub issues         | `--title "Bug" --file issue.md`   |
| `create_pr.py`               | Create pull requests         | `--title "feat: add" --closes 42` |
| `merge_pr.py`                | Merge PRs automatically      | `--cleanup`                       |
| `check_ci.py`                | Check CI status              | `--pr 5`                          |
| `pr_ready.py`                | Check if PR ready to merge   | `--pr 5`                          |
| `project_overview.py`        | Project status snapshot      | No args needed                    |
| `github_helper.py`           | Helper module for scripts    | Import in Python                  |
| `auto_label.py`              | Auto-label issues            | Used in workflows                 |
| `add_acceptance_criteria.py` | Generate acceptance criteria | Used in workflows                 |
| `generate_subtasks.py`       | Break down complex issues    | Used in workflows                 |
| `analyze_context.py`         | Analyze repository context   | Used in workflows                 |
| `analyze_pr.py`              | Analyze PR changes           | Used in workflows                 |
| `parse_command.py`           | Parse slash commands         | Used in workflows                 |
| `execute_command.py`         | Execute parsed commands      | Used in workflows                 |

## Setup

### 1. Install Dependencies

```bash
pip install PyGithub
# Or
pip install -e ".[github-actions]"
```

### 2. Configure Token

Create `.env`:

```bash
GITHUB_TOKEN=your_github_token_here
```

## Documentation Links

- **[Complete Script Documentation](../workflows/scripts/README.md)** - Detailed usage for all scripts
- **[PR Automation Guide](../PR_AUTOMATION.md)** - PR workflow automation
- **[Git Workflow](workflow/git-flow.md)** - Complete Git Flow guide
- **[DEV Tools](DEV_TOOLS.md)** - All development tools

## Quick Workflows

### For Cursor Agent

```bash
# 1. Check open issues
python3 .github/workflows/scripts/read_issues.py --list

# 2. Read specific issue
python3 .github/workflows/scripts/read_issues.py 4

# 3. Work on issue...

# 4. Create PR
python3 .github/workflows/scripts/create_pr.py --title "feat: description" --closes 4

# 5. Merge when ready
python3 .github/workflows/scripts/merge_pr.py
```

### For Developers

```bash
# Create and merge PR workflow
git checkout -b feature/my-feature
# ... make changes ...
git commit -m "feat: add feature"
git push -u origin feature/my-feature
python3 .github/workflows/scripts/create_pr.py --title "feat: add feature" --closes 42
# ... wait for review and CI ...
python3 .github/workflows/scripts/merge_pr.py --cleanup
```

## Help

All scripts support `--help`:

```bash
python3 .github/workflows/scripts/create_pr.py --help
python3 .github/workflows/scripts/merge_pr.py --help
```

---

**📖 For detailed documentation, see:** [../workflows/scripts/README.md](../workflows/scripts/README.md)
