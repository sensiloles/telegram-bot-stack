# Pull Request Automation

> **📖 Main Guide:** See [.github/PR_AUTOMATION.md](../../PR_AUTOMATION.md) for complete PR automation documentation.

This document provides quick links and workflow-specific details.

## Quick Links

- **[Complete PR Automation Guide](../../PR_AUTOMATION.md)** - Full documentation
- **[Scripts README](../../workflows/scripts/README.md)** - All automation scripts
- **[Git Flow](git-flow.md)** - Complete Git workflow
- **[Issue Linking](issue-linking.md)** - Link PRs to issues

## Quick Commands

### Create PR

```bash
# Auto-detect branch, auto-generate description
python3 .github/workflows/scripts/create_pr.py --title "feat(storage): add Redis backend"

# Link to issue
python3 .github/workflows/scripts/create_pr.py --title "fix(auth): token validation" --closes 42
```

### Merge PR

```bash
# One command - auto-detect PR, merge, switch to main
python3 .github/workflows/scripts/merge_pr.py

# With cleanup (delete branches)
python3 .github/workflows/scripts/merge_pr.py --cleanup
```

### Check PR Status

```bash
# Check CI
python3 .github/workflows/scripts/check_ci.py --pr 5

# Check if ready to merge
python3 .github/workflows/scripts/pr_ready.py --pr 5
```

## Workflow Integration

### GitHub Flow with PR Automation

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes and commit
git add .
git commit -m "feat(scope): description"
git push -u origin feature/my-feature

# 3. Create PR (automated)
python3 .github/workflows/scripts/create_pr.py \
  --title "feat(scope): description" \
  --closes 42

# 4. Wait for CI and review
python3 .github/workflows/scripts/check_ci.py --pr <number>

# 5. Merge (automated)
python3 .github/workflows/scripts/merge_pr.py
```

## Features

### Auto-Create PR

- ✅ Validates conventional commit format
- ✅ Auto-generates description from commits
- ✅ Links issues with `--closes N`
- ✅ Auto-assigns to you
- ✅ Supports draft PRs
- ✅ Dry-run mode

### One-Command Merge

- ✅ Auto-detects PR from branch
- ✅ Checks CI status
- ✅ Merges with squash
- ✅ Switches to main and pulls
- ✅ Optionally deletes branches (`--cleanup`)
- ✅ Shows release status

### CI Status Check

- ✅ Check PR/commit/branch CI
- ✅ List PRs with status
- ✅ JSON output for automation
- ✅ Exit codes for scripting

## Conventional Commits

PR titles must follow format: `type(scope): description`

**Version Impact:**

- `feat:` → MINOR version bump
- `fix:` → PATCH version bump
- `docs:` → No version bump
- `chore:` → No version bump

**Examples:**

```bash
feat(storage): add Redis backend support
fix(auth): resolve token validation issue
docs(readme): update installation instructions
```

## Script Options

### create_pr.py

```bash
--title TITLE          # Required: PR title (conventional format)
--closes NUMBER        # Link issue
--file FILE           # Custom description
--draft               # Draft PR
--base BRANCH         # Base branch (default: main)
--dry-run             # Preview without creating
```

### merge_pr.py

```bash
--pr NUMBER           # Specific PR (default: auto-detect)
--cleanup             # Delete local and remote branches
--no-switch           # Don't switch to main
--dry-run             # Preview without merging
```

### check_ci.py

```bash
--pr NUMBER           # Check PR
--commit SHA          # Check commit
--branch NAME         # Check branch
--list-prs            # List PRs
--json                # JSON output
```

## For AI Agents

**Quick workflow:**

```bash
# 1. Check status
python3 .github/workflows/scripts/read_issues.py --list

# 2. Work on feature
# ... make changes ...

# 3. Create PR
python3 .github/workflows/scripts/create_pr.py \
  --title "feat: description" \
  --closes N

# 4. Merge when ready
python3 .github/workflows/scripts/merge_pr.py
```

## Troubleshooting

**"Could not find PR for branch"**

PR doesn't exist yet. Create it first with `create_pr.py`.

**"CI checks failed"**

Fix issues, push new commits, check status with `check_ci.py`.

**"GITHUB_TOKEN not found"**

Create `.env` file: `echo "GITHUB_TOKEN=your_token" > .env`

---

**📖 For complete documentation, see:** [.github/PR_AUTOMATION.md](../../PR_AUTOMATION.md)
