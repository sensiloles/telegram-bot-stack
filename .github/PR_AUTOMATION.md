# 🤖 Pull Request Automation

Automated workflow for creating Pull Requests using Python scripts.

## 🎯 Overview

Instead of manually creating PRs on GitHub web interface, use our automation script:

```bash
python3 .github/workflows/scripts/create_pr.py \
    --title "feat(storage): add Redis backend" \
    --closes 42
```

**Benefits:**

- ✅ Validates conventional commit format
- ✅ Auto-generates description from commits
- ✅ Links to issues automatically
- ✅ Creates PR without leaving terminal
- ✅ Supports draft PRs and custom branches
- ✅ Dry-run mode for preview

## 🚀 Quick Start

### 1. Complete Your Work

```bash
# Make changes
git add .
git commit -m "feat(storage): add Redis backend"
git push origin feature/redis-backend
```

### 2. Create PR

```bash
# Basic (auto-generates description)
python3 .github/workflows/scripts/create_pr.py \
    --title "feat(storage): add Redis backend"

# With issue linking
python3 .github/workflows/scripts/create_pr.py \
    --title "feat(storage): add Redis backend" \
    --closes 42

# Output:
# ✅ Pull Request created successfully!
#    Number: #10
#    URL: https://github.com/owner/repo/pull/10
```

### 3. PR is Ready!

- ✅ Title in conventional format
- ✅ Description auto-generated from commits
- ✅ Issue linked (auto-closes on merge)
- ✅ CI checks run automatically
- ✅ Ready for review

## 📝 Usage

### Basic Usage

```bash
# Current branch → main
python3 .github/workflows/scripts/create_pr.py \
    --title "feat(bot): add webhook support"
```

**What it does:**

1. Detects current branch automatically
2. Validates title format: `type(scope): description`
3. Gets commits between `main` and current branch
4. Generates description from commit messages
5. Creates PR with checklist

### With Issue Linking

```bash
# Links to issue #42 (adds "Closes #42")
python3 .github/workflows/scripts/create_pr.py \
    --title "fix(auth): resolve token expiration" \
    --closes 42
```

**Result:**

```markdown
## Changes

- fix(auth): resolve token expiration
- test(auth): add token expiration tests

## Related Issue

Closes #42

## Checklist

- [x] Code follows project style guidelines
      ...
```

### Custom Description

```bash
# Create detailed description file
cat > /tmp/pr_desc.md << 'EOF'
## What Changed

Implemented Redis backend with connection pooling.

## Why

Redis provides faster performance for high-traffic scenarios.

## Testing

- Unit tests added
- Integration tests passing
- Load tested with 10k req/s
EOF

# Create PR with custom description
python3 .github/workflows/scripts/create_pr.py \
    --title "feat(storage): add Redis backend" \
    --file /tmp/pr_desc.md \
    --closes 42
```

### Draft PR

```bash
# Create draft PR for WIP features
python3 .github/workflows/scripts/create_pr.py \
    --title "feat(api): new endpoint (WIP)" \
    --draft
```

### Custom Base Branch

```bash
# PR to 'develop' instead of 'main'
python3 .github/workflows/scripts/create_pr.py \
    --title "feat: feature" \
    --base develop
```

### Dry Run

```bash
# Preview what would be created
python3 .github/workflows/scripts/create_pr.py \
    --title "feat(storage): add Redis" \
    --closes 42 \
    --dry-run

# Output shows:
# - Repository
# - Branches (from → to)
# - Full PR description
# - List of commits
# - No actual PR created
```

## 🎨 Title Format

**Required format:** `type(scope): description`

### Valid Types

| Type       | Usage            | Version Impact      |
| ---------- | ---------------- | ------------------- |
| `feat`     | New features     | MINOR (0.1.0→0.2.0) |
| `fix`      | Bug fixes        | PATCH (0.1.0→0.1.1) |
| `docs`     | Documentation    | None                |
| `refactor` | Code refactoring | None                |
| `test`     | Tests            | None                |
| `chore`    | Maintenance      | None                |
| `perf`     | Performance      | PATCH (0.1.0→0.1.1) |
| `style`    | Formatting       | None                |
| `ci`       | CI/CD changes    | None                |

### Examples

```bash
# ✅ Good
feat(storage): add Redis backend
fix(auth): resolve token validation
docs(api): update storage interface

# ❌ Bad
Add Redis           # Missing type
feat: Redis         # Too vague
Storage backend     # Missing type
```

## 🔧 All Options

```bash
python3 .github/workflows/scripts/create_pr.py \
    --title "feat(scope): description"    # Required: PR title
    --closes 42                            # Optional: Issue to close
    --file pr_desc.md                      # Optional: Custom description file
    --draft                                # Optional: Create as draft
    --base develop                         # Optional: Base branch (default: main)
    --head feature/xyz                     # Optional: Source branch (auto-detected)
    --repo owner/repo                      # Optional: Repository (auto-detected)
    --no-validate                          # Optional: Skip title validation
    --dry-run                              # Optional: Preview without creating
```

## 🤖 For AI Agent

### Optimal Workflow

```python
# 1. Complete work and commit
git commit -m "feat(storage): add Redis backend"
git push origin feature/redis

# 2. Create PR via script
python3 .github/workflows/scripts/create_pr.py \
    --title "feat(storage): add Redis backend" \
    --closes 42

# 3. Inform user
print("✅ Pull Request created!")
print("   URL: https://github.com/owner/repo/pull/10")
print("   CI checks will run automatically")
print("   Issue #42 will close on merge")
```

### Decision Tree

```
After pushing branch:
  ↓
Is there an issue?
  ├─ YES → Use --closes N
  ├─ NO → Continue
  ↓
Is PR ready for review?
  ├─ YES → Create normal PR
  ├─ NO → Create draft PR (--draft)
  ↓
Create PR with script:
  python3 .github/workflows/scripts/create_pr.py \
      --title "type(scope): description" \
      [--closes N] \
      [--draft]
  ↓
Inform user with PR URL
```

### When to Use Script vs Manual

**Use Script:**

- ✅ Standard feature branches
- ✅ Single logical change
- ✅ Conventional commit format
- ✅ Terminal-based workflow

**Manual (GitHub Web):**

- ⚠️ Complex multi-repo changes
- ⚠️ Requires special formatting/images
- ⚠️ Cross-repository PRs
- ⚠️ User prefers web interface

### Agent Template

After pushing changes, agent should:

```bash
# Create PR
python3 .github/workflows/scripts/create_pr.py \
    --title "feat(storage): add Redis backend" \
    --closes 42

# Then tell user:
"""
✅ Changes committed and pushed to feature/redis-backend
🔄 Pull Request created automatically!
   Number: #10
   URL: https://github.com/owner/repo/pull/10

Next steps:
- CI checks running (tests, linting, type checking)
- Review and merge when ready
- Issue #42 will auto-close on merge
- Automatic release will trigger after merge
"""
```

## 📊 PR Description Format

### Auto-Generated (Default)

```markdown
## Changes

- feat(storage): add Redis backend
- feat(storage): add connection pooling
- test(storage): add Redis integration tests

## Related Issue

Closes #42

## Checklist

- [x] Code follows project style guidelines
- [x] Self-review completed
- [x] Comments added for complex code
- [x] Documentation updated (if needed)
- [x] No new warnings generated
- [x] Tests added/updated (if applicable)
- [x] All tests passing locally
```

### Custom (From File)

```markdown
## What Changed

Detailed explanation of changes...

## Why

Rationale...

## Testing

How it was tested...

## Related Issue

Closes #42
```

## 🔍 Validation

### Title Validation

Script automatically validates:

```python
# Pattern: type(scope): description
✅ feat(storage): add Redis
✅ fix: resolve bug
❌ Add feature        # Missing type
❌ FEAT: feature      # Wrong case
❌ feat add feature   # Missing colon
```

**To skip validation:**

```bash
python3 .github/workflows/scripts/create_pr.py \
    --title "Whatever title" \
    --no-validate
```

### Branch Validation

```bash
# Error if on base branch
$ git checkout main
$ python3 .github/workflows/scripts/create_pr.py --title "feat: feature"
❌ Error: Cannot create PR from main to main
Please create a feature branch first
```

### Commit Validation

```bash
# Warning if no commits
$ python3 .github/workflows/scripts/create_pr.py --title "feat: feature"
⚠️  Warning: No commits found between main and feature/xyz
# Still creates PR (might be first commit)
```

## 🛠️ Setup

### Requirements

```bash
# Install PyGithub
pip install PyGithub
```

### Configure Token

```bash
# Option 1: .env file (recommended)
echo "GITHUB_TOKEN=your_token_here" >> .env

# Option 2: Environment variable
export GITHUB_TOKEN=your_token_here
```

### Token Permissions

Token needs `repo` scope:

- Full repository access
- Create/edit pull requests
- Read/write issues

## 🐛 Troubleshooting

### "Invalid PR title format"

```bash
❌ PR title must follow format: type(scope): description

# Fix: Use conventional format
--title "feat(storage): add Redis"
```

### "Cannot create PR from main to main"

```bash
❌ Error: Cannot create PR from main to main

# Fix: Create feature branch
git checkout -b feature/my-feature
```

### "Pull request already exists"

```bash
❌ Pull Request already exists for feature/xyz -> main

# PR already created, check GitHub
```

### "No commits between main and feature/xyz"

```bash
⚠️  Warning: No commits found

# Possible reasons:
1. Already merged
2. Branches are identical
3. Branch name mismatch
```

### "401 Unauthorized"

```bash
❌ Invalid token or missing 'repo' scope

# Fix: Check token in .env
# Ensure token has 'repo' scope
```

## 📚 Examples

### Simple Feature

```bash
# 1. Create feature branch
git checkout -b feature/add-logging

# 2. Make changes and commit
git add .
git commit -m "feat(core): add structured logging"
git push origin feature/add-logging

# 3. Create PR
python3 .github/workflows/scripts/create_pr.py \
    --title "feat(core): add structured logging"

# Result: PR created with auto-generated description
```

### Bug Fix with Issue

```bash
# 1. Create fix branch
git checkout -b fix/42-token-expiration

# 2. Fix and commit
git commit -m "fix(auth): resolve token expiration"
git push origin fix/42-token-expiration

# 3. Create PR linked to issue
python3 .github/workflows/scripts/create_pr.py \
    --title "fix(auth): resolve token expiration" \
    --closes 42

# Result: PR linked to issue #42
```

### Documentation Update

```bash
# 1. Update docs
git checkout -b docs/api-reference
git commit -m "docs(api): update storage interface"
git push origin docs/api-reference

# 2. Create PR
python3 .github/workflows/scripts/create_pr.py \
    --title "docs(api): update storage interface"

# Result: PR with docs type (no version bump)
```

### Work in Progress

```bash
# 1. Start feature
git checkout -b feature/websockets
git commit -m "feat(bot): WIP websocket support"
git push origin feature/websockets

# 2. Create draft PR
python3 .github/workflows/scripts/create_pr.py \
    --title "feat(bot): add websocket support (WIP)" \
    --draft

# Result: Draft PR (not ready for review)
```

## 🔗 Related Documentation

- [Git Workflow Guide](.github/GIT_WORKFLOW.md) - Complete Git Flow documentation
- [PR Naming Guide](.github/PR_NAMING_GUIDE.md) - PR title conventions
- [Issue-PR Linking](.github/LINKING_ISSUES.md) - How to link issues
- [Scripts README](.github/workflows/scripts/README.md) - All automation scripts

---

**Automate your workflow!** 🚀
