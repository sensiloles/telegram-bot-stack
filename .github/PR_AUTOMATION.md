# Pull Request Automation Guide

Complete guide to automated PR creation and management using Python scripts.

## Quick Reference

### Create PR (Automated)

```bash
# Auto-detect branch, auto-generate description
python3 .github/workflows/scripts/create_pr.py --title "feat(storage): add Redis backend"

# Link to issue (auto-closes on merge)
python3 .github/workflows/scripts/create_pr.py --title "fix(auth): token validation" --closes 42

# Draft PR for work in progress
python3 .github/workflows/scripts/create_pr.py --title "feat: WIP feature" --draft
```

### Merge PR (One Command)

```bash
# Merge current branch's PR (auto-detect PR number)
python3 .github/workflows/scripts/merge_pr.py

# Merge and delete both local and remote branches
python3 .github/workflows/scripts/merge_pr.py --cleanup

# Merge specific PR
python3 .github/workflows/scripts/merge_pr.py --pr 42
```

### Check PR Status

```bash
# Check CI status
python3 .github/workflows/scripts/check_ci.py --pr 5

# Check if ready to merge
python3 .github/workflows/scripts/pr_ready.py --pr 5

# List recent PRs
python3 .github/workflows/scripts/check_ci.py --list-prs
```

## Features

### Auto-Create PR

**Benefits:**

- ✅ Validates conventional commit format
- ✅ Auto-generates description from commits
- ✅ Links issues with `--closes N`
- ✅ Auto-assigns to you
- ✅ Supports draft PRs
- ✅ Dry-run mode for preview

**Script:** `.github/workflows/scripts/create_pr.py`

### One-Command Merge

**What it does automatically:**

1. Finds PR number from current branch
2. Checks CI status
3. Merges with squash method
4. Switches to main branch
5. Pulls latest changes
6. Optionally deletes local AND remote branches (with `--cleanup`)
7. Shows release status

**Script:** `.github/workflows/scripts/merge_pr.py`

### CI Status Check

**Check:**

- PR CI status
- Commit CI status
- Branch CI status
- List PRs with status

**Script:** `.github/workflows/scripts/check_ci.py`

## Common Workflows

### 1. Feature Development

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes and commit
git add .
git commit -m "feat(scope): description"
git push -u origin feature/my-feature

# 3. Create PR automatically
python3 .github/workflows/scripts/create_pr.py \
  --title "feat(scope): description" \
  --closes 42

# Output:
# ✅ Pull Request created successfully!
#    Number: #10
#    URL: https://github.com/owner/repo/pull/10
#    Issue: Closes #42
#    Status: Ready for review
```

### 2. Merge PR

```bash
# ONE COMMAND - does everything
python3 .github/workflows/scripts/merge_pr.py

# What happens:
# 1. ✓ Found PR #10 for branch feature/my-feature
# 2. ✓ CI checks: All passed
# 3. ✓ PR merged successfully
# 4. ✓ Switched to main branch
# 5. ✓ Pulled latest changes
# 6. ℹ Release workflow started automatically

# With cleanup (deletes branches)
python3 .github/workflows/scripts/merge_pr.py --cleanup
# Also:
# 7. ✓ Deleted local branch feature/my-feature
# 8. ✓ Deleted remote branch origin/feature/my-feature
```

### 3. Check PR Before Merge

```bash
# Quick CI check
python3 .github/workflows/scripts/check_ci.py --pr 5

# Full readiness check
python3 .github/workflows/scripts/pr_ready.py --pr 5
```

## Script Options

### create_pr.py

```bash
# Required
--title TITLE          # PR title (conventional format: type(scope): description)

# Optional
--closes NUMBER        # Link issue (adds "Closes #N")
--file FILE           # Custom description file
--draft               # Create draft PR
--base BRANCH         # Base branch (default: main)
--dry-run             # Preview without creating
```

### merge_pr.py

```bash
# All optional (auto-detects everything)
--pr NUMBER           # Specific PR number (default: auto-detect from branch)
--cleanup             # Delete local and remote branches after merge
--no-switch           # Don't switch to main after merge
--dry-run             # Preview without merging
```

### check_ci.py

```bash
# Check options (one required)
--pr NUMBER           # Check PR CI status
--commit SHA          # Check commit CI status
--branch NAME         # Check branch CI status
--list-prs            # List recent PRs with status

# Output options
--json                # JSON output for automation
--state STATE         # Filter PRs (open/closed/all)
```

## Integration with .cursorrules

The `.cursorrules` file provides these shortcuts for AI agents:

### Quick Merge Command

```bash
python3 .github/workflows/scripts/merge_pr.py
```

This ONE command does everything:

- Find PR
- Merge
- Switch to main
- Pull

### Workflow in .cursorrules

```bash
# 1. Work on feature
git checkout -b feature/xyz

# 2. Commit and push
git commit -m "feat: description"
git push -u origin feature/xyz

# 3. Auto-create PR
python3 .github/workflows/scripts/create_pr.py --title "feat: description" --closes N

# 4. Merge when ready
python3 .github/workflows/scripts/merge_pr.py
```

## Exit Codes

Scripts use standard exit codes for automation:

- `0` - Success
- `1` - Error (CI failed, merge conflict, validation failed)
- `2` - Usage error (missing arguments, invalid options)

### Example Automation

```bash
# Wait for CI to pass before merging
if python3 .github/workflows/scripts/pr_ready.py --pr 5 --quiet; then
  python3 .github/workflows/scripts/merge_pr.py --pr 5
else
  echo "PR not ready - CI still running or failed"
  exit 1
fi
```

## Conventional Commit Format

PR titles must follow conventional commit format:

```
type(scope): description
```

### Types and Version Impact

- `feat:` → MINOR version bump (0.1.0 → 0.2.0)
- `fix:` → PATCH version bump (0.1.0 → 0.1.1)
- `docs:` → No version bump
- `chore:` → No version bump
- `test:` → No version bump
- `refactor:` → No version bump
- `perf:` → PATCH version bump
- `feat!` or `BREAKING CHANGE:` → MAJOR version bump (0.x.x → 1.0.0)

### Examples

```bash
# Good
feat(storage): add Redis backend support
fix(auth): resolve token validation issue
docs(readme): update installation instructions
test(storage): add integration tests
chore(deps): update dependencies

# Bad
add redis                    # Missing type
feat add redis               # Missing colon
FEAT(storage): add redis     # Wrong case
```

## Dry Run Mode

All scripts support `--dry-run` to preview actions:

```bash
# Preview PR creation
python3 .github/workflows/scripts/create_pr.py \
  --title "feat: test" \
  --dry-run

# Preview merge
python3 .github/workflows/scripts/merge_pr.py --dry-run
```

## JSON Output

For automation and scripting:

```bash
# Get PR status as JSON
python3 .github/workflows/scripts/check_ci.py --pr 5 --json

# Parse with jq
python3 .github/workflows/scripts/check_ci.py --pr 5 --json | jq '.status'
```

## Troubleshooting

### "Could not find PR for branch"

**Solution:** PR doesn't exist yet. Create it first:

```bash
python3 .github/workflows/scripts/create_pr.py --title "feat: description"
```

### "CI checks failed"

**Solution:** Fix issues, push new commits, wait for CI:

```bash
# Check what failed
python3 .github/workflows/scripts/check_ci.py --pr 5

# After fixing and pushing
python3 .github/workflows/scripts/check_ci.py --pr 5  # Check again
```

### "Branch protection error"

**Solution:** You're on main branch. Create feature branch:

```bash
git checkout -b feature/my-feature
```

### "GITHUB_TOKEN not found"

**Solution:** Create `.env` file:

```bash
echo "GITHUB_TOKEN=your_token_here" > .env
```

## Related Documentation

- **Scripts Reference:** `.github/docs/scripts.md`
- **Git Workflow:** `.github/docs/workflow/git-flow.md`
- **Issue Linking:** `.github/docs/workflow/issue-linking.md`
- **PR Template:** `.github/pull_request_template.md`
- **Agent Rules:** `.cursorrules`

## Quick Links

- **Full Automation Guide:** See `.github/docs/workflow/pr-automation.md`
- **All Scripts:** `.github/workflows/scripts/`
- **Script Help:** `python3 script.py --help`

---

**💡 Tip:** Use `merge_pr.py` - it's the fastest way to merge PRs!
