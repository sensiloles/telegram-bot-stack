# Merge PR Guide

> **🚀 Quick Method:** Use `merge_pr.py` script for automated merging. See [PR Automation Guide](../../PR_AUTOMATION.md) for details.

## Quick Start

### One-Command Merge

```bash
# Merge current branch's PR (auto-detect)
python3 .github/workflows/scripts/merge_pr.py

# Merge and delete branches
python3 .github/workflows/scripts/merge_pr.py --cleanup

# Merge specific PR
python3 .github/workflows/scripts/merge_pr.py --pr 42
```

### What It Does Automatically

1. ✅ Finds PR number from current branch
2. ✅ Checks CI status
3. ✅ Merges with squash method
4. ✅ Switches to main branch
5. ✅ Pulls latest changes
6. ✅ Optionally deletes local AND remote branches
7. ✅ Shows release status

## PR Types & Release Detection

### Release PR

**Contains:** `feat`, `fix`, `perf` commits

**Result:**

- ✅ Merged with squash
- 🚀 Triggers semantic release workflow
- 📦 Creates new version tag
- 📝 Generates changelog

**Version Impact:**

- `feat:` → MINOR bump (0.1.0 → 0.2.0)
- `fix:` → PATCH bump (0.1.0 → 0.1.1)
- `perf:` → PATCH bump
- `feat!` or `BREAKING CHANGE:` → MAJOR bump (0.x.x → 1.0.0)

### Non-Release PR

**Contains:** `docs`, `chore`, `refactor`, `style`, `test`, `ci` commits

**Result:**

- ✅ Merged with squash
- ℹ️ No version bump
- ℹ️ No release created

## Complete Workflow

### 1. Check PR Status

```bash
# Check CI status
python3 .github/workflows/scripts/check_ci.py --pr 5

# Check if ready to merge
python3 .github/workflows/scripts/pr_ready.py --pr 5
```

### 2. Merge PR

```bash
# Simple merge (keeps branches)
python3 .github/workflows/scripts/merge_pr.py --pr 5

# Merge with cleanup (deletes branches)
python3 .github/workflows/scripts/merge_pr.py --pr 5 --cleanup
```

### 3. Verify Release

```bash
# Check GitHub Actions for release workflow
# View releases: https://github.com/owner/repo/releases
```

## Merge Options

### Script Options

```bash
--pr NUMBER           # Specific PR number (default: auto-detect)
--cleanup             # Delete local and remote branches after merge
--no-switch           # Don't switch to main after merge
--dry-run             # Preview without merging
```

### Examples

```bash
# Auto-detect and merge
python3 .github/workflows/scripts/merge_pr.py

# Merge and cleanup
python3 .github/workflows/scripts/merge_pr.py --cleanup

# Merge specific PR
python3 .github/workflows/scripts/merge_pr.py --pr 42

# Preview merge
python3 .github/workflows/scripts/merge_pr.py --dry-run
```

## Conventional Commits

PR titles determine version bump:

| Type     | Version Impact        | Example                            |
| -------- | --------------------- | ---------------------------------- |
| `feat:`  | MINOR (0.1.0 → 0.2.0) | `feat(storage): add Redis backend` |
| `fix:`   | PATCH (0.1.0 → 0.1.1) | `fix(auth): token validation`      |
| `perf:`  | PATCH (0.1.0 → 0.1.1) | `perf(query): optimize search`     |
| `docs:`  | No bump               | `docs(readme): update install`     |
| `chore:` | No bump               | `chore(deps): update libs`         |
| `feat!:` | MAJOR (0.x.x → 1.0.0) | `feat!: breaking change`           |

## Troubleshooting

### "Could not find PR for branch"

**Cause:** No PR exists for current branch.

**Solution:** Create PR first:

```bash
python3 .github/workflows/scripts/create_pr.py --title "feat: description"
```

### "CI checks failed"

**Cause:** Tests or linting failed.

**Solution:**

```bash
# Check what failed
python3 .github/workflows/scripts/check_ci.py --pr 5

# Fix issues, commit, push
git add .
git commit -m "fix: resolve CI issues"
git push

# Wait for CI to pass
python3 .github/workflows/scripts/check_ci.py --pr 5
```

### "Merge conflict detected"

**Cause:** Branch has conflicts with main.

**Solution:**

```bash
# Update your branch
git checkout feature/my-feature
git fetch origin
git merge origin/main
# Resolve conflicts
git commit
git push
```

### "Not on feature branch"

**Cause:** Trying to merge from main branch.

**Solution:**

```bash
# Check current branch
git branch --show-current

# Switch to feature branch
git checkout feature/my-feature

# Then merge
python3 .github/workflows/scripts/merge_pr.py
```

## Release Workflow

After merging a release PR:

1. **Release workflow starts automatically** (GitHub Actions)
2. **Semantic-release analyzes commits** (determines version bump)
3. **New version tag created** (e.g., v0.2.0)
4. **Changelog generated** (from commit messages)
5. **GitHub Release created** (with release notes)
6. **Package built** (optional: publish to PyPI)

**View releases:**

- GitHub: https://github.com/owner/repo/releases
- Tags: https://github.com/owner/repo/tags

## Best Practices

### 1. Check CI Before Merge

```bash
python3 .github/workflows/scripts/pr_ready.py --pr 5
```

### 2. Use Cleanup Flag

```bash
# Automatically delete branches after merge
python3 .github/workflows/scripts/merge_pr.py --cleanup
```

### 3. Verify Release Type

```bash
# Check PR commits to know if release will trigger
git log main..feature/my-feature --oneline | grep -E "^[a-f0-9]+ (feat|fix|perf)"
```

### 4. Follow Conventional Commits

Always use proper commit format:

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation only

## For AI Agents

**Recommended workflow:**

```bash
# 1. Verify PR is ready
python3 .github/workflows/scripts/check_ci.py --pr N

# 2. Merge with cleanup
python3 .github/workflows/scripts/merge_pr.py --cleanup

# 3. Notify user
# - PR merged successfully
# - Switched to main branch
# - Branches deleted
# - Release workflow started (if applicable)
```

## Related Documentation

- **[PR Automation Guide](../../PR_AUTOMATION.md)** - Complete PR automation
- **[Git Flow](../workflow/git-flow.md)** - Full Git workflow
- **[Scripts README](../../workflows/scripts/README.md)** - All scripts
- **[Issue Linking](../workflow/issue-linking.md)** - Link PRs to issues

---

**💡 Tip:** Use `merge_pr.py --cleanup` for fastest workflow - it does everything automatically!
