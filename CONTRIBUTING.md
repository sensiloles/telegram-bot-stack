# Contributing to telegram-bot-stack

Thank you for your interest in contributing! This document provides guidelines and setup instructions.

## Quick Start

### 1. Fork and Clone

```bash
# Fork on GitHub, then clone
git clone https://github.com/YOUR_USERNAME/telegram-bot-stack.git
cd telegram-bot-stack
```

### 2. Set Up Development Environment

**Unix (Linux, macOS):**

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

**Windows (PowerShell):**

```powershell
# Create virtual environment
python -m venv venv
venv\Scripts\Activate.ps1

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

**Windows (cmd):**

```cmd
# Create virtual environment
python -m venv venv
venv\Scripts\activate.bat

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

**Using cross-platform task runner:**

All platforms can use `scripts/tasks.py` for development:

```bash
# Setup development environment (cross-platform)
python scripts/tasks.py dev
```

### 3. Configure GitHub Automation (Optional)

Create `.env` file in project root:

```bash
# Generate token: https://github.com/settings/tokens
# Required scopes: repo, workflow
GITHUB_TOKEN=ghp_your_token_here
```

Verify setup:

```bash
python3 .github/workflows/scripts/check_setup.py
```

## Development Workflow

### 1. Create Feature Branch

**NEVER push to main directly!**

```bash
# Ensure you're on main and up to date
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/my-feature
# or fix/bug-name, docs/update-guide, etc.
```

### 2. Make Changes

- Write code
- Add/update tests (maintain >=80% coverage)
- Update documentation
- Follow code style (see below)

### 3. Test Your Changes

**Option A: Using Makefile (Unix only):**

```bash
# Run tests
make test-fast

# Check coverage
make coverage

# Run linter
make lint

# Format code
make format
```

**Option B: Using scripts/tasks.py (cross-platform, recommended for Windows):**

```bash
# Run tests
python scripts/tasks.py test-fast

# Check coverage
python scripts/tasks.py coverage

# Run linter
python scripts/tasks.py lint

# Format code
python scripts/tasks.py format
```

**Option C: Direct commands (all platforms):**

```bash
# Run tests
pytest

# Check coverage
pytest --cov=telegram_bot_stack --cov-report=term

# Run linter
ruff check .

# Format code
ruff format .

# Type check
mypy telegram_bot_stack/
```

### 4. Commit Changes

Use **Conventional Commits** format:

```bash
git add .
git commit -m "type(scope): description"
```

**Types:**

- `feat` - New feature (MINOR version bump)
- `fix` - Bug fix (PATCH version bump)
- `docs` - Documentation only
- `test` - Test updates
- `refactor` - Code refactoring
- `chore` - Maintenance
- `perf` - Performance improvements

**Examples:**

```bash
git commit -m "feat(storage): add Redis backend"
git commit -m "fix(auth): resolve token validation bug"
git commit -m "docs(readme): update installation steps"
```

### 5. Push and Create PR

```bash
# Push to your fork
git push -u origin feature/my-feature

# Create PR using automation (if configured)
python3 .github/workflows/scripts/create_pr.py \
  --title "feat(scope): description" \
  --closes <issue_number>

# Or create PR manually on GitHub
```

### 6. Address Review Comments

```bash
# Make changes
git add .
git commit -m "fix: address review comments"
git push
```

### 7. After Merge

```bash
# Update your fork
git checkout main
git pull upstream main
git push origin main

# Delete feature branch
git branch -d feature/my-feature
git push origin --delete feature/my-feature
```

## Code Style

### Python Style Guide

- Follow PEP 8
- Use type hints for all functions
- Write docstrings for public APIs
- Keep functions focused and small
- Use meaningful variable names

### Linting

We use `ruff` for linting and formatting:

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check . --fix

# Format code
ruff format .
```

### Type Checking

We use `mypy` for type checking:

```bash
mypy telegram_bot_stack/
```

### Comments and Documentation

- All comments and docstrings in **English**
- Document public APIs with comprehensive docstrings
- Keep comments up to date with code
- Use comments to explain "why", not "what"

## Testing

### Writing Tests

- Tests go in `tests/` directory
- Mirror source structure: `telegram_bot_stack/storage/base.py` → `tests/core/test_storage.py`
- Use fixtures from `tests/conftest.py`
- Write both unit and integration tests

### Test Requirements

- Maintain **>=80% coverage** for `telegram_bot_stack/`
- All tests must pass before merging
- Test edge cases and error conditions
- Use mocks for external dependencies

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/core/test_storage.py

# Specific test
pytest tests/core/test_storage.py::test_json_storage_basic

# With coverage
pytest --cov=telegram_bot_stack --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Documentation

### When to Update Docs

- Adding new features → Update API reference
- Changing behavior → Update relevant guides
- Fixing bugs → Update if documented behavior changes
- New examples → Add to examples/ with README

### Documentation Files

- `README.md` - Project overview, quick start
- `docs/api_reference.md` - API documentation
- `docs/architecture.md` - System design
- `docs/storage_guide.md` - Storage backend guide
- `docs/quickstart.md` - Tutorial
- `docs/migration_guide.md` - Migration between versions

### Documentation Style

- Write in clear, simple English
- Use code examples liberally
- Test all code examples
- Keep examples up to date
- Use emoji sparingly (1 per section max)

## Project Structure

```
telegram-bot-stack/
├── telegram_bot_stack/     # Main package
│   ├── bot_base.py        # Base bot class
│   ├── admin_manager.py   # Admin management
│   ├── user_manager.py    # User tracking
│   ├── decorators.py      # Helper decorators
│   ├── storage/           # Storage backends
│   └── cli/               # CLI tools
├── tests/                 # Test suite
│   ├── core/             # Core tests
│   ├── examples/         # Example bot tests
│   └── integration/      # Integration tests
├── examples/             # Example bots
├── docs/                 # Documentation
├── .github/              # GitHub workflows
│   ├── workflows/        # CI/CD workflows
│   └── workflows/scripts/ # Automation scripts
└── scripts/              # Utility scripts
```

## GitHub Automation Scripts

Located in `.github/workflows/scripts/`:

### Issue Management

- `read_issues.py` - List and read issues
- `create_issue.py` - Create new issue
- `update_issue.py` - Update issue

### PR Management

- `create_pr.py` - Create pull request
- `list_prs.py` - List pull requests
- `merge_pr.py` - Merge pull request

### Utilities

- `check_setup.py` - Verify configuration

See `.github/workflows/scripts/README.md` for detailed usage.

## Release Process

Releases are automated via GitHub Actions on merge to main:

1. Conventional commits determine version bump

   - `feat:` → MINOR (1.13.0 → 1.14.0)
   - `fix:` → PATCH (1.13.0 → 1.13.1)
   - `feat!:` → MAJOR (1.x.x → 2.0.0)

2. Version is updated in `pyproject.toml`
3. Git tag is created
4. Package is published to PyPI
5. GitHub release is created

**Manual release** (maintainers only):

```bash
python3 .github/workflows/scripts/create_release.py --auto
```

## Common Issues

### Import Errors After Installation

```bash
# Reinstall in development mode
pip install -e ".[dev]"
```

### Pre-commit Hook Fails

```bash
# Update hooks
pre-commit autoupdate

# Run manually
pre-commit run --all-files
```

### Tests Fail Locally

```bash
# Clear cache
pytest --cache-clear

# Reinstall dependencies
pip install -e ".[dev]" --force-reinstall
```

### GitHub Token Issues

```bash
# Check token
python3 .github/workflows/scripts/check_setup.py

# Regenerate if needed
# https://github.com/settings/tokens
```

## Getting Help

- **Issues:** https://github.com/sensiloles/telegram-bot-stack/issues
- **Discussions:** https://github.com/sensiloles/telegram-bot-stack/discussions
- **Documentation:** [docs/](docs/)

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

## Recognition

Contributors are recognized in:

- GitHub contributors page
- Release notes for significant contributions
- Project README (for major features)

Thank you for contributing! 🎉
