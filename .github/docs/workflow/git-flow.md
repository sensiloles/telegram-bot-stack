# 🔄 Git Workflow Guide

Git workflow for `telegram-bot-stack` project using **GitHub Flow with Semantic Versioning**.

## 🎯 Workflow Overview

```
┌─────────────┐
│   feature   │───┐
│   branch    │   │
└─────────────┘   │
                  │  Pull Request
┌─────────────┐   │  + Review
│   bugfix    │───┤  + Tests
│   branch    │   │  + Approval
└─────────────┘   │
                  ↓
              ┌────────┐      Auto-release
              │  main  │──────────────────→ v0.2.0
              └────────┘      (on merge)
                  ↑
                  │  Hotfix PR
┌─────────────┐   │  (emergency)
│   hotfix    │───┘
│   branch    │
└─────────────┘
```

## 📋 Branch Strategy

### Main Branch (Protected)

- **Name:** `main`
- **Purpose:** Production-ready code
- **Protection:**
  - ✅ Require pull request reviews
  - ✅ Require status checks to pass
  - ✅ No direct pushes
  - ✅ No force pushes
- **Auto-actions:**
  - Run tests on every PR
  - Auto-release on merge (semantic versioning)

### Feature Branches

- **Naming:** `feature/<description>` or `feat/<description>`
- **Examples:**
  - `feature/add-redis-storage`
  - `feat/webhook-support`
- **Lifetime:** Short-lived (delete after merge)
- **Base:** `main`
- **Merge to:** `main` via Pull Request

### Bugfix Branches

- **Naming:** `fix/<description>` or `bugfix/<description>`
- **Examples:**
  - `fix/storage-race-condition`
  - `bugfix/admin-permission-check`
- **Lifetime:** Short-lived (delete after merge)
- **Base:** `main`
- **Merge to:** `main` via Pull Request

### Hotfix Branches

- **Naming:** `hotfix/<version>` or `hotfix/<description>`
- **Examples:**
  - `hotfix/v0.1.1`
  - `hotfix/critical-security-fix`
- **Purpose:** Emergency fixes for production
- **Lifetime:** Very short-lived
- **Base:** `main`
- **Merge to:** `main` via expedited PR

### Documentation Branches

- **Naming:** `docs/<description>`
- **Examples:**
  - `docs/update-api-reference`
  - `docs/add-examples`
- **Can be merged faster:** Documentation-only changes

## 🚀 Development Workflow

### 1. Start New Feature

```bash
# Update main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/my-awesome-feature

# Make changes
# ... code ...

# Commit with conventional commits
git add .
git commit -m "feat(storage): add Redis backend support"
```

### 2. Push and Create PR

```bash
# Push branch
git push origin feature/my-awesome-feature

# Create PR on GitHub
# GitHub will suggest creating PR automatically
```

### 3. PR Review Process

1. **Automated checks run:**

   - ✅ Tests (Python 3.9-3.12)
   - ✅ Linting (Ruff)
   - ✅ Coverage (≥80%)
   - ✅ Type checking (mypy)

2. **Code review:**

   - At least 1 approval required
   - Address review comments

3. **Merge:**
   - Click "Squash and merge" or "Merge"
   - Delete branch after merge

### 4. Automatic Release

After merge to `main`:

- GitHub Action automatically:
  - Analyzes commit messages
  - Determines version bump (major/minor/patch)
  - Creates git tag
  - Generates changelog
  - Creates GitHub Release

## 📝 Commit Message Convention

We use **Conventional Commits** for automatic versioning.

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types and Version Bumps

| Type              | Description      | Version Bump              | Example                                |
| ----------------- | ---------------- | ------------------------- | -------------------------------------- |
| `feat`            | New feature      | **MINOR** (0.1.0 → 0.2.0) | `feat(storage): add Redis backend`     |
| `fix`             | Bug fix          | **PATCH** (0.1.0 → 0.1.1) | `fix(auth): resolve token validation`  |
| `docs`            | Documentation    | No release                | `docs: update API reference`           |
| `chore`           | Maintenance      | No release                | `chore: update dependencies`           |
| `refactor`        | Code refactoring | No release                | `refactor: simplify storage interface` |
| `test`            | Tests            | No release                | `test: add Redis storage tests`        |
| `perf`            | Performance      | **PATCH**                 | `perf(storage): optimize JSON reads`   |
| `BREAKING CHANGE` | Breaking change  | **MAJOR** (0.1.0 → 1.0.0) | See below                              |

### Breaking Changes

```bash
# In commit message footer
git commit -m "feat(storage): change interface

BREAKING CHANGE: StorageBackend.save() now returns Result object instead of bool"
```

Or in type:

```bash
git commit -m "feat!: change storage interface"
```

### Examples

```bash
# New feature (minor version bump)
git commit -m "feat(bot): add webhook support"

# Bug fix (patch version bump)
git commit -m "fix(storage): handle connection timeout"

# Documentation (no version bump)
git commit -m "docs(readme): add Redis installation guide"

# Performance improvement (patch)
git commit -m "perf(cache): implement LRU cache for user data"

# Breaking change (major version bump)
git commit -m "feat!: redesign storage API

BREAKING CHANGE: All storage methods now async"
```

## 🔒 Branch Protection Rules

Configure on GitHub: **Settings → Branches → Add rule for `main`**

### Required Settings

```yaml
Branch name pattern: main

✅ Require a pull request before merging
   ✅ Require approvals: 1
   ✅ Dismiss stale pull request approvals when new commits are pushed
   ✅ Require review from Code Owners (optional)

✅ Require status checks to pass before merging
   ✅ Require branches to be up to date before merging
   Required checks:
   - test (Python 3.9)
   - test (Python 3.10)
   - test (Python 3.11)
   - test (Python 3.12)
   - lint
   - type-check

✅ Require conversation resolution before merging

✅ Require linear history (optional - for cleaner history)

✅ Do not allow bypassing the above settings
   ⚠️ Allow administrators to bypass (for emergencies only)

❌ Allow force pushes: Nobody
❌ Allow deletions: Nobody
```

## 🤖 Automatic Release Process

### Setup: GitHub Action for Semantic Release

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    branches:
      - main

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Semantic Release
        uses: python-semantic-release/python-semantic-release@v8
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

### What Happens on Merge

1. **Commit analyzed:** Parse conventional commit messages
2. **Version calculated:** Based on commit types
3. **Version bumped:** Update `pyproject.toml` and `__init__.py`
4. **Changelog generated:** From commit messages
5. **Git tag created:** e.g., `v0.2.0`
6. **GitHub Release created:** With changelog
7. **Optional:** Publish to PyPI (when configured)

### Example

```bash
# You merge PR with commits:
feat(storage): add Redis backend
fix(bot): resolve startup race condition
docs: update examples

# GitHub Action automatically:
# - Bumps version: 0.1.0 → 0.2.0 (feat = minor)
# - Creates tag: v0.2.0
# - Generates changelog
# - Creates GitHub Release
```

## 📊 Release Versioning

We follow **Semantic Versioning (SemVer)**: `MAJOR.MINOR.PATCH`

### Version Components

- **MAJOR** (1.0.0): Breaking changes

  - Triggered by: `BREAKING CHANGE` in commit
  - Example: `0.9.0 → 1.0.0`

- **MINOR** (0.2.0): New features (backward compatible)

  - Triggered by: `feat:` commits
  - Example: `0.1.0 → 0.2.0`

- **PATCH** (0.1.1): Bug fixes
  - Triggered by: `fix:`, `perf:` commits
  - Example: `0.1.0 → 0.1.1`

### Pre-releases

For testing before stable release:

```bash
# Alpha: 0.2.0-alpha.1
# Beta: 0.2.0-beta.1
# RC: 0.2.0-rc.1
```

## 🔥 Hotfix Process

For critical production issues:

```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-security-fix

# 2. Fix the issue
# ... make changes ...

# 3. Commit with fix type
git commit -m "fix(security): patch SQL injection vulnerability

This is a critical security fix that needs immediate release."

# 4. Push and create PR with "hotfix" label
git push origin hotfix/critical-security-fix

# 5. Request expedited review
# 6. Merge ASAP
# 7. Auto-release as patch version
```

## 👥 Collaboration Workflow

### For Contributors

1. **Fork the repository**
2. **Clone your fork:**

   ```bash
   git clone git@github.com:YOUR-USERNAME/telegram-bot-stack.git
   ```

3. **Add upstream remote:**

   ```bash
   git remote add upstream git@github.com:sensiloles/telegram-bot-stack.git
   ```

4. **Create feature branch:**

   ```bash
   git checkout -b feature/my-feature
   ```

5. **Make changes and commit:**

   ```bash
   git commit -m "feat(bot): add new feature"
   ```

6. **Push to your fork:**

   ```bash
   git push origin feature/my-feature
   ```

7. **Create Pull Request** on GitHub

8. **Respond to review feedback**

9. **Squash commits if requested**

### For Maintainers

1. **Review PRs:**

   - Check code quality
   - Verify tests pass
   - Ensure conventional commits
   - Request changes if needed

2. **Merge strategy:**

   - **Squash and merge:** For multiple commits (keeps history clean)
   - **Merge commit:** For well-crafted single commits
   - **Rebase and merge:** For linear history (optional)

3. **After merge:**
   - Delete feature branch
   - Monitor automatic release
   - Verify GitHub Release created

## 📦 Release Checklist

Before merging to main:

- [ ] All tests passing
- [ ] Coverage ≥80%
- [ ] Linter passes (Ruff)
- [ ] Type checking passes (mypy)
- [ ] Documentation updated
- [ ] Changelog-worthy commits use conventional format
- [ ] Breaking changes documented
- [ ] PR description is clear

## 🎯 Quick Reference

### Common Commands

```bash
# Start new feature
git checkout main && git pull origin main
git checkout -b feature/my-feature

# Update feature branch with main
git checkout main && git pull origin main
git checkout feature/my-feature
git merge main

# Squash commits before merge (if needed)
git rebase -i main

# Check commit message format
git log --oneline

# Undo last commit (keep changes)
git reset --soft HEAD~1
```

### PR Commands

```bash
# Update PR with review changes
git add .
git commit -m "refactor: address review comments"
git push origin feature/my-feature

# Force push after rebase (use with caution)
git push --force-with-lease origin feature/my-feature
```

## 🆘 Troubleshooting

### PR Checks Failing

```bash
# Run tests locally
pytest

# Run linter
ruff check .

# Run formatter
ruff format .

# Check coverage
pytest --cov=telegram_bot_stack
```

### Merge Conflicts

```bash
# Update your branch with main
git checkout main
git pull origin main
git checkout feature/my-feature
git merge main

# Resolve conflicts
# ... fix conflicts in files ...

git add .
git commit -m "merge: resolve conflicts with main"
git push origin feature/my-feature
```

### Wrong Commit Message

```bash
# Amend last commit message
git commit --amend -m "feat(storage): correct commit message"

# Force push to update PR (if already pushed)
git push --force-with-lease origin feature/my-feature
```

## 📚 Resources

- **Conventional Commits:** https://www.conventionalcommits.org/
- **Semantic Versioning:** https://semver.org/
- **GitHub Flow:** https://guides.github.com/introduction/flow/
- **Branch Protection:** https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches

---

**Ready to contribute?** Follow this workflow and our codebase stays clean and releases are automatic! 🚀
