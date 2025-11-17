# 🔀 Auto-Merge PR Guide

Comprehensive guide to automatic PR merging with release detection.

## 📋 Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Usage](#usage)
- [PR Types](#pr-types)
- [Merge Strategies](#merge-strategies)
- [CLI Commands](#cli-commands)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Overview

The auto-merge system automatically merges PRs after CI checks pass, with intelligent detection of whether a PR will trigger a release.

### Key Features

- ✅ **Automatic merge** after CI passes
- 🎯 **Release detection** (feat/fix vs docs/chore)
- 🔄 **Smart merge strategies** (squash for releases, merge for non-releases)
- 🏷️ **Label-based activation** (`automerge` label)
- 📊 **Detailed analysis** of PR impact
- 🛡️ **Safety checks** (draft, conflicts, required reviews)

## How It Works

### 1. Enable Auto-Merge

Add the `automerge` label to your PR:

```bash
# Using GitHub CLI
gh pr edit 123 --add-label automerge

# Using dev CLI
./dev merge auto 123

# Or manually on GitHub PR page
```

### 2. Automatic Process

Once labeled, the system:

1. **Waits for CI checks** to complete (timeout: 30 minutes)
2. **Analyzes commits** to determine PR type
3. **Selects merge strategy** based on PR type
4. **Merges PR** when all checks pass
5. **Triggers release** (if applicable)

### 3. Release Workflow

If PR contains `feat`/`fix`/`perf` commits:

```
PR Merged → Release Workflow Triggered → Version Bump → GitHub Release Created
```

## Usage

### Method 1: Auto-Merge (Recommended)

Add label and let automation handle it:

```bash
# Enable auto-merge
./dev merge auto 123

# Or using GitHub CLI
gh pr edit 123 --add-label automerge

# System will:
# 1. Wait for CI checks
# 2. Analyze PR type
# 3. Merge automatically
# 4. Trigger release (if needed)
```

### Method 2: Manual Merge

Merge immediately without waiting:

```bash
# Analyze first
./dev merge analyze 123

# Then merge
./dev merge now 123

# Or with specific method
./dev merge now 123 --method squash

# Dry run
./dev merge now 123 --dry-run
```

## PR Types

### Release PR

**Contains:** `feat`, `fix`, `perf` commits

**Behavior:**

- ✅ Triggers semantic release
- 📦 Creates new version tag
- 📝 Generates changelog
- 🔀 Uses **squash merge**

**Example commits:**

```
feat(storage): add Redis backend
fix(auth): resolve token validation
perf(cache): improve query performance
```

**Result:** Version bump + GitHub Release

### Non-Release PR

**Contains:** `docs`, `chore`, `refactor`, `style`, `test`, `ci` commits

**Behavior:**

- ❌ No version bump
- 📝 No release created
- 🔀 Uses **squash merge**

**Example commits:**

```
docs(readme): update installation guide
chore(deps): update dependencies
refactor(storage): simplify code
test(api): add integration tests
```

**Result:** Changes merged, no release

## Merge Strategy

### Squash Merge (All PRs)

**Used for:** All pull requests

**Advantages:**

- Clean, single commit in main
- Linear history
- Easy to revert
- Professional commit history
- Clear changelog (for releases)

**Commit format for release PRs:**

```
feat(scope): PR title (#123)

PR description

🚀 This PR will trigger a release
```

**Commit format for non-release PRs:**

```
docs(scope): PR title (#123)

PR description
```

## CLI Commands

### Analyze PR

Check if PR will trigger a release:

```bash
./dev merge analyze 123

# Output:
# ============================================================
# 📊 PR Analysis for #123
# ============================================================
#
# PR Type: RELEASE
# Will Trigger Release: ✅ YES
# Version Bump: MINOR
# Merge Strategy: squash
#
# Commit Types Found:
#   - feat: 3
#   - fix: 1
#   - docs: 2
```

### Enable Auto-Merge

Add `automerge` label:

```bash
./dev merge auto 123

# Output:
# 🏷️ Adding 'automerge' label to PR #123...
# ✅ Auto-merge enabled for PR #123
```

### Manual Merge

Merge immediately:

```bash
# Auto-detect strategy
./dev merge now 123

# Force specific method
./dev merge now 123 --method squash
./dev merge now 123 --method merge
./dev merge now 123 --method rebase

# Dry run (preview)
./dev merge now 123 --dry-run
```

## Examples

### Example 1: Release PR

PR with new features:

```bash
# Check what will happen
./dev merge analyze 5

# Output:
# PR Type: RELEASE
# Will Trigger Release: ✅ YES
# Version Bump: MINOR
# Merge Strategy: squash

# Enable auto-merge
./dev merge auto 5

# Or merge now
./dev merge now 5

# Result:
# ✅ PR #5 merged with squash
# 🚀 Release workflow starting...
# 📦 New version: v0.2.0
```

### Example 2: Non-Release PR

PR with only docs:

```bash
# Check
./dev merge analyze 7

# Output:
# PR Type: NON-RELEASE
# Will Trigger Release: ❌ NO
# Version Bump: NONE
# Merge Strategy: merge

# Enable auto-merge
./dev merge auto 7

# Result:
# ✅ PR #7 merged with merge commit
# ℹ️ No release triggered (docs only)
```

### Example 3: Mixed PR

PR with features and docs:

```bash
# Analyze
./dev merge analyze 8

# Output:
# PR Type: RELEASE
# Will Trigger Release: ✅ YES
# Version Bump: MINOR
# Commit Types:
#   - feat: 2
#   - docs: 3

# Note: Even ONE feat/fix makes it a release PR!
```

## Troubleshooting

### Auto-Merge Not Working

**Issue:** PR has `automerge` label but not merging

**Checks:**

1. **Is PR in draft?**

   ```bash
   gh pr view 123 --json isDraft
   # Remove draft: gh pr ready 123
   ```

2. **Are CI checks passing?**

   ```bash
   ./dev pr check 123
   # Wait for checks to complete
   ```

3. **Does PR have conflicts?**

   ```bash
   gh pr view 123 --json mergeable
   # Resolve conflicts first
   ```

4. **Required reviews?**
   ```bash
   # Check branch protection rules
   # Get required approvals
   ```

### Wrong Merge Strategy

**Issue:** Want different merge method

**Solution:**

```bash
# Remove automerge label first
gh pr edit 123 --remove-label automerge

# Merge manually with desired method
./dev merge now 123 --method squash
```

### Release Not Triggered

**Issue:** Expected release but none created

**Check commits:**

```bash
# Verify commit format
git log main~5..main --oneline

# Must start with: feat:, fix:, or perf:
```

**Common mistakes:**

```bash
# ❌ Wrong (no colon)
git commit -m "feat add feature"

# ✅ Correct
git commit -m "feat: add feature"
git commit -m "feat(scope): add feature"
```

### Manual Merge Failed

**Issue:** `./dev merge now` fails

**Debug:**

```bash
# 1. Check PR status
gh pr view 123

# 2. Verify checks
./dev pr check 123

# 3. Try dry run
./dev merge now 123 --dry-run

# 4. Check GitHub token permissions
echo $GITHUB_TOKEN | cut -c1-10
# Needs: contents:write, pull-requests:write
```

## Workflow Configuration

### Required GitHub Settings

**Branch Protection (main):**

1. Go to: Settings → Branches → Branch protection rules
2. Enable:
   - ✅ Require status checks to pass
   - ✅ Require branches to be up to date
   - Select: Test Summary (or your CI check name)
3. Optional:
   - Require approvals (recommended for teams)
   - Require linear history

**Actions Permissions:**

Settings → Actions → General → Workflow permissions:

- ✅ Read and write permissions
- ✅ Allow GitHub Actions to create and approve pull requests

### Disable Auto-Merge

Remove label to disable:

```bash
gh pr edit 123 --remove-label automerge
```

Or configure in `.github/workflows/auto-merge.yml`.

## Best Practices

### 1. Use Conventional Commits

Always follow the format:

```
type(scope): description

- type: feat, fix, docs, etc.
- scope: optional module name
- description: what changed
```

### 2. One Logical Change Per PR

- **Good:** One feature per PR
- **Bad:** Multiple unrelated changes

### 3. Label Early

Add `automerge` label when creating PR (if confident).

### 4. Monitor CI

Watch CI checks before labeling:

```bash
./dev pr check 123
```

### 5. Use Dry Run

Test before merging:

```bash
./dev merge now 123 --dry-run
```

## See Also

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Workflow Guide](../.github/docs/workflow/git-flow.md)
- [Release Automation](../.github/docs/workflow/releases.md)
- [PR Naming Guide](../PR_NAMING_GUIDE.md)

---

**Last Updated:** 2024-11-17
**Maintainers:** Automated via `.github/workflows/auto-merge.yml`
