# 🔀 Merge PR Guide

Simple guide for merging Pull Requests via CLI.

## 📋 Overview

Merge PRs with intelligent release detection:

- ✅ Analyzes commits (feat/fix vs docs/chore)
- ✅ Detects if PR will trigger release
- ✅ Uses squash merge for clean history
- ✅ Validates CI checks before merge

## 🚀 Quick Start

### 1. Check PR Status

```bash
# Check if CI passed
./dev pr check 5

# Analyze PR type
./dev merge analyze 5
```

### 2. Merge PR

```bash
# Merge PR (squash merge)
./dev merge now 5

# Dry run (preview)
./dev merge now 5 --dry-run
```

## 📊 PR Types

### Release PR

**Contains:** `feat`, `fix`, `perf` commits

**Result:**

- ✅ Merged with squash
- 🚀 Triggers semantic release
- 📦 Creates new version tag
- 📝 Generates changelog

**Example:**

```bash
./dev merge analyze 5
# Output:
# PR Type: RELEASE
# Will Trigger Release: ✅ YES
# Version Bump: MINOR
# Merge Strategy: squash

./dev merge now 5
# PR #5 merged → Release v0.2.0 created
```

### Non-Release PR

**Contains:** `docs`, `chore`, `refactor`, `style`, `test`, `ci` commits

**Result:**

- ✅ Merged with squash
- ℹ️ No version bump
- ℹ️ No release created

**Example:**

```bash
./dev merge analyze 7
# Output:
# PR Type: NON-RELEASE
# Will Trigger Release: ❌ NO
# Version Bump: NONE

./dev merge now 7
# PR #7 merged (no release)
```

## 🛠️ CLI Commands

### Analyze PR

Check if PR will trigger a release:

```bash
./dev merge analyze <pr_number>
```

**Output:**

```
============================================================
📊 PR Analysis for #5
============================================================

PR Type: RELEASE
Will Trigger Release: ✅ YES
Version Bump: MINOR
Merge Strategy: squash

Commit Types Found:
  - feat: 3
  - fix: 1
  - docs: 2
```

### Merge PR

Merge PR with squash:

```bash
# Merge now
./dev merge now <pr_number>

# Preview (dry run)
./dev merge now <pr_number> --dry-run
```

**Output (successful merge):**

```
============================================================
🔀 Merging PR #5
============================================================

Title: feat(workflow): add PR automation
Base: main
Head: feature/automation
PR Type: release
Will Release: ✅ YES
Merge Method: squash

⏳ Attempting to merge...

✅ PR #5 merged successfully!
Merge commit: abc1234

🚀 Release workflow will start automatically
Monitor at: https://github.com/owner/repo/actions
```

## ⚠️ Prerequisites

### Before Merging

1. **CI checks must pass:**

   ```bash
   ./dev pr check 5
   # All checks should be ✅
   ```

2. **No merge conflicts:**

   ```bash
   # PR must be mergeable
   ```

3. **Required reviews (if configured):**
   ```bash
   # Get approvals from team
   ```

## 🎯 Workflow

### For AI Agent

```bash
# 1. Check current work
./dev status

# 2. List PRs
./dev pr list

# 3. Check specific PR
./dev pr check 5

# 4. Analyze PR type
./dev merge analyze 5

# 5. Merge if ready
./dev merge now 5

# Agent will notify user:
# ✅ PR #5 merged successfully!
# 🚀 Release v0.2.0 will be created automatically
```

### For Developer

```bash
# Quick merge after CI passes
./dev pr check 5 && ./dev merge now 5

# Or with analysis
./dev merge analyze 5 && ./dev merge now 5
```

## 🔧 Troubleshooting

### CI Checks Not Passing

```bash
./dev pr check 5
# ⚠️ 1 check(s) failing!

# Wait for checks or fix issues
# Then try again
```

### Merge Conflicts

```bash
# Output: ❌ PR has conflicts and cannot be merged

# Resolve conflicts in branch
git pull origin main
# ... resolve conflicts ...
git push

# Then merge
./dev merge now 5
```

### API Errors

```bash
# 403 Forbidden: Check token permissions
# 405 Method Not Allowed: Required reviews not satisfied
# 422 Validation Failed: Branch not up to date

# See .github/TOKEN_SETUP_GUIDE.md for token setup
```

## 📈 Version Bumps

Based on conventional commits:

| Commits                        | Version Bump | Example       |
| ------------------------------ | ------------ | ------------- |
| `feat:`                        | MINOR        | 0.1.0 → 0.2.0 |
| `fix:`                         | PATCH        | 0.1.0 → 0.1.1 |
| `perf:`                        | PATCH        | 0.1.0 → 0.1.1 |
| `docs:`, `chore:`, etc         | NONE         | No release    |
| `feat!:` or `BREAKING CHANGE:` | MAJOR        | 0.x.x → 1.0.0 |

## 📚 See Also

- [PR Naming Guide](../PR_NAMING_GUIDE.md)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Workflow](../workflow/git-flow.md)
- [Token Setup](../TOKEN_SETUP_GUIDE.md)

---

**Last Updated:** 2024-11-17
