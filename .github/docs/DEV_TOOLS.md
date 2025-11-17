# 🛠️ Development Tools & Workflow

Complete guide to all development tools and shortcuts in telegram-bot-stack.

## 🚀 Quick Start

```bash
# One command to see everything
make help           # All Make commands
./dev help          # All CLI commands
python3 .github/workflows/scripts/project_overview.py  # Project status
```

## 📦 Tool Categories

### 1. Makefile Commands

Fast shortcuts for common tasks:

```bash
# Testing
make test          # Run all tests
make test-fast     # Quick tests (no coverage)
make test-cov      # Tests with coverage report
make test-unit     # Only unit tests

# Code Quality
make lint          # Check code style
make lint-fix      # Auto-fix issues
make format        # Format code
make type-check    # Type checking

# CI/CD
make ci            # Run all CI checks locally
make pr-check PR=5 # Check PR CI status

# Git & GitHub
make status        # Project status
make issue-list    # List issues
make pr-create TITLE="..." # Create PR

# Shortcuts
make t            # test
make l            # lint
make f            # format
make s            # status
```

### 2. CLI Wrapper (`./dev`)

Interactive command-line interface:

```bash
# Status
./dev status                    # Project overview

# Testing
./dev test                      # All tests
./dev test fast                 # Fast tests
./dev test cov                  # With coverage
./dev test unit                 # Unit tests only

# Code Quality
./dev lint                      # Check code
./dev lint --fix                # Auto-fix
./dev format                    # Format code
./dev typecheck                 # Type check

# CI/CD
./dev ci run                    # Run CI locally
./dev ci check                  # Check current branch
./dev ci check main             # Check specific branch

# Pull Requests
./dev pr check 5                # Check PR #5
./dev pr create --title "..."   # Create PR
./dev pr list                   # List PRs

# Issues
./dev issue list                # List issues
./dev issue read 4              # Read issue #4

# Utils
./dev clean                     # Clean artifacts
./dev setup                     # Setup environment
```

### 3. GitHub Automation Scripts

Located in `.github/workflows/scripts/`:

#### Issue Management

```bash
# List issues
python3 .github/workflows/scripts/read_issues.py --list

# Read specific issue
python3 .github/workflows/scripts/read_issues.py 4

# Create issue
python3 .github/workflows/scripts/create_issue.py \
  --title "Bug: Fix tests" \
  --file issue.md \
  --labels bug
```

#### Pull Requests

```bash
# Create PR
python3 .github/workflows/scripts/create_pr.py \
  --title "feat(storage): add Redis" \
  --closes 42

# Check CI status
python3 .github/workflows/scripts/check_ci.py --pr 5

# Check if ready to merge
python3 .github/workflows/scripts/pr_ready.py --pr 5

# List recent PRs
python3 .github/workflows/scripts/check_ci.py --list-prs
```

#### Project Status

```bash
# Quick overview
python3 .github/workflows/scripts/project_overview.py

# Detailed overview
python3 .github/workflows/scripts/project_overview.py --detailed
```

## 🎯 Common Workflows

### 1. Start New Feature

```bash
# 1. Create branch
git checkout -b feature/my-feature

# 2. Check status
./dev status

# 3. Make changes and test
./dev test fast

# 4. Lint and format
./dev lint --fix
./dev format

# 5. Run full CI locally
./dev ci run

# 6. Commit and push
git add .
git commit -m "feat(scope): description"
git push -u origin feature/my-feature

# 7. Create PR
./dev pr create --title "feat(scope): description" --closes 42

# Or with make
make pr-create TITLE="feat(scope): description" CLOSES=42
```

### 2. Check PR Before Review

```bash
# Quick check
./dev pr check 5

# Detailed readiness check
python3 .github/workflows/scripts/pr_ready.py --pr 5

# View full CI details
python3 .github/workflows/scripts/check_ci.py --pr 5
```

### 3. Daily Development

```bash
# Morning: Check project status
./dev status

# Run tests while developing
make t              # Quick alias for test

# Check code frequently
make l              # Quick alias for lint

# Format before commit
make f              # Quick alias for format

# Full check before push
make ci             # All CI checks
```

### 4. Debugging CI Issues

```bash
# 1. Check what's failing
./dev pr check 5

# 2. Run tests locally
make test-cov

# 3. Check specific test
pytest tests/core/test_storage.py -v

# 4. Lint
make lint-fix

# 5. Type check
make type-check

# 6. Run full CI
make ci
```

## 🎨 Tool Comparison

| Task           | Make                         | ./dev                           | Direct Script                                                  |
| -------------- | ---------------------------- | ------------------------------- | -------------------------------------------------------------- |
| Run tests      | `make test`                  | `./dev test`                    | `pytest`                                                       |
| Check CI       | `make pr-check PR=5`         | `./dev pr check 5`              | `python3 .github/workflows/scripts/check_ci.py --pr 5`         |
| Create PR      | `make pr-create TITLE="..."` | `./dev pr create --title "..."` | `python3 .github/workflows/scripts/create_pr.py --title "..."` |
| Project status | `make status`                | `./dev status`                  | `python3 .github/workflows/scripts/project_overview.py`        |

**When to use what:**

- **Make:** Traditional, fast, great for CI/CD
- **./dev:** Interactive, modern, user-friendly
- **Direct scripts:** Maximum control, automation, scripting

## 💡 Tips & Tricks

### 1. Fastest Workflow

```bash
# Use shortcuts
make t        # Instead of make test
make l        # Instead of make lint
make s        # Instead of make status

# Chain commands
make l && make t && make pr-check PR=5
```

### 2. Automation

```bash
# Check if PR ready in scripts
if python3 .github/workflows/scripts/pr_ready.py --pr 5 --quiet; then
  echo "Ready to merge!"
else
  echo "Not ready yet"
fi

# Get CI status as JSON
python3 .github/workflows/scripts/check_ci.py --pr 5 --json
```

### 3. Development Shell

```bash
# Start Python shell with imports
make dev-shell

# In shell:
# >>> from telegram_bot_stack import *
# >>> # Test components interactively
```

### 4. Watch Mode

```bash
# Tests re-run on file changes (requires pytest-watch)
make test-watch
```

## 📚 Documentation

- **[Scripts Reference](scripts.md)** - All automation scripts
- **[Git Workflow](workflow/git-flow.md)** - Git Flow guide
- **[PR Automation](workflow/pr-automation.md)** - PR automation details
- **[Setup Guide](setup/getting-started.md)** - Environment setup

## 🤖 For AI Agents

**Priority tools to use:**

1. `make status` - Quick project overview
2. `python3 .github/workflows/scripts/read_issues.py --list` - See open issues
3. `python3 .github/workflows/scripts/check_ci.py --pr N` - Check CI
4. `python3 .github/workflows/scripts/create_pr.py` - Create PRs

**Workflow:**

```bash
# 1. Check status
make status

# 2. Work on issue
python3 .github/workflows/scripts/read_issues.py 4

# 3. Test changes
make test-fast

# 4. Create PR
python3 .github/workflows/scripts/create_pr.py \
  --title "feat: description" \
  --closes 4
```

## 🔧 Troubleshooting

### "Command not found: make"

Install make: `brew install make` (macOS) or use `./dev` instead

### "./dev: Permission denied"

Run: `chmod +x dev`

### "GITHUB_TOKEN not found"

Set token: See [Token Setup Guide](setup/token-setup.md)

### Scripts fail with import errors

Install dependencies: `make setup` or `pip install -e ".[dev,github-actions]"`

## 🎯 Summary

**Three ways to do everything:**

1. **Makefile** - `make test`, `make lint`, `make status`
2. **CLI Wrapper** - `./dev test`, `./dev lint`, `./dev status`
3. **Direct Scripts** - Full control for automation

**Pick what works best for you!**

All tools are designed to work together and make development faster and more enjoyable.

---

**Questions?** Check the [main docs](README.md) or open an issue!
