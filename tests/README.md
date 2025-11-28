# Tests

Comprehensive test suite for telegram-bot-stack framework.

## Structure

```
tests/
├── unit/              # Unit tests (fast, isolated, no Docker)
│   ├── agent/         # Agent functionality tests
│   ├── cli/           # CLI commands tests
│   ├── core/          # Core framework tests
│   └── examples/      # Example bots tests
│
├── integration/       # Integration tests (fast, no Mock VPS)
│   ├── bot/           # Bot user flow tests
│   ├── deployment/    # Config, Docker templates, CLI
│   └── fixtures/      # Test infrastructure (Mock VPS)
│
├── e2e/               # E2E tests (slow, requires Mock VPS + Docker)
│   └── deployment/    # Full deployment workflow tests
│       ├── test_full_deployment_flow.py
│       ├── test_secrets_management.py
│       ├── test_backup_restore.py
│       ├── test_rollback_version_tracking.py
│       └── test_health_monitoring.py
│
└── conftest.py        # Shared pytest fixtures
```

## Quick Start

### Run All Tests

```bash
pytest tests/
```

### Run by Type

```bash
# Unit tests only (fastest, no Docker)
make test-unit
pytest tests/unit/ -v

# Fast tests (unit + basic integration, ~1min)
make test-fast

# Integration tests (basic, no Mock VPS)
make test-integration
pytest tests/integration/ -v

# E2E deployment tests (requires Mock VPS, ~5-30min)
make test-deploy
pytest tests/e2e/deployment/ -v

# All E2E tests
make test-e2e
pytest tests/e2e/ -v
```

### Run with Coverage

```bash
# All tests with coverage
pytest --cov=telegram_bot_stack --cov-report=html

# Unit tests with coverage
pytest tests/unit/ --cov=telegram_bot_stack --cov-report=term
```

## Test Types

### 🔬 Unit Tests (`tests/unit/`)

**What**: Test individual functions, methods, classes in isolation

**Characteristics**:

- ⚡ **Fast**: Milliseconds per test
- 🔒 **Isolated**: Use mocks, no external dependencies
- 🎯 **Focused**: One component per test
- 📊 **Coverage**: 440+ tests, 70%+ coverage

**Run**: `pytest tests/unit/` or `make test-unit`

**Docs**: [`tests/unit/README.md`](unit/README.md)

### 🔗 Integration Tests (`tests/integration/`)

**What**: Test component interactions (basic, no full deployment)

**Characteristics**:

- ⚡ **Fast**: ~1-2 minutes total
- 🚫 **No Docker**: No Mock VPS required
- 🧩 **Components**: Config, templates, CLI, bot flows
- 📊 **Coverage**: 25+ tests

**Run**: `pytest tests/integration/` or `make test-integration`

**Docs**: [`tests/integration/README.md`](integration/README.md)

### 🎯 E2E Tests (`tests/e2e/`)

**What**: Full deployment workflows with Mock VPS

**Characteristics**:

- 🐌 **Slow**: ~5-30 minutes (Docker builds)
- 🐳 **Docker**: Requires Mock VPS container
- 🔄 **Realistic**: Complete deployment cycles
- 📊 **Coverage**: 60+ tests

**Run**: `pytest tests/e2e/` or `make test-e2e`

**Docs**: [`tests/e2e/README.md`](e2e/README.md)

## Running Tests

### Prerequisites

```bash
# Install dependencies
pip install -e ".[dev]"

# For integration tests
docker --version  # Docker required
```

### Make Commands

```bash
make test                  # Run all tests (461 tests, ~16s) - E2E skipped by default
make test-fast            # ⚡ Quick validation (unit + basic integration, ~16s)
make test-unit            # Unit tests only (~10s)
make test-integration     # Integration tests (basic, ~1s)
make test-deploy          # E2E deployment tests (requires Mock VPS, ~5-30min)
make test-e2e             # All E2E tests (~5-30min, runs with --run-e2e)
make coverage             # Run tests with coverage report
make build-mock-vps       # Build Mock VPS image (required for E2E)
make test-all-versions    # Test on Python 3.9-3.12 (via tox)
```

**Note:** E2E tests (53 tests in `tests/e2e/`) are skipped by default to avoid Docker-in-Docker issues locally. Use `make test-e2e` or `pytest --run-e2e` to run them explicitly.

### Pytest Options

```bash
# Verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=telegram_bot_stack --cov-report=term

# Run E2E tests (skipped by default)
pytest tests/ --run-e2e

# Stop on first failure
pytest tests/ -x

# Run specific test
pytest tests/unit/core/test_storage.py::test_save_and_load

# Run tests matching pattern
pytest tests/ -k "storage"

# Show print statements
pytest tests/ -s

# Parallel execution (faster)
pytest tests/unit/ -n auto
```

### CI/CD

Tests run automatically in GitHub Actions on every pull request:

**Unit Tests** (`.github/workflows/unit-tests.yml`):

- ✅ Required for PR merge
- 🚀 Fast (2-3 minutes)
- 🐍 Python 3.9, 3.10, 3.11, 3.12
- 📊 Coverage uploaded to Codecov

**Integration Tests** (`.github/workflows/integration-tests.yml`):

- ✅ Required for PR merge
- ⚡ Fast (1-2 minutes)
- 🚫 No Docker required
- 🐍 Python 3.11, 3.12

**E2E Tests** (`.github/workflows/e2e-tests.yml`):

- ⚠️ Non-blocking (won't prevent merge)
- 🐳 Requires Docker + Mock VPS
- 🐍 Python 3.12 only
- ⏱️ Timeout: 45 minutes

**Code Quality:**

- **Lint** (`.github/workflows/lint.yml`): Ruff linter + formatter
- **Type Check** (`.github/workflows/type-check.yml`): mypy (non-blocking)

## Coverage

### Current Status

- **Total**: ~70%
- **Target**: ≥80%
- **Required**: ≥50% (CI)

### Generate Reports

```bash
# HTML report
pytest --cov=telegram_bot_stack --cov-report=html
open htmlcov/index.html

# Terminal report
pytest --cov=telegram_bot_stack --cov-report=term-missing

# XML report (for CI)
pytest --cov=telegram_bot_stack --cov-report=xml
```

## Writing Tests

### File Naming

```
test_<module_name>.py      # Test file
Test<ClassName>             # Test class
test_<function_name>        # Test function
```

### Example

```python
"""Test module for my_feature."""

import pytest
from telegram_bot_stack.my_module import MyClass


class TestMyClass:
    """Tests for MyClass."""

    def test_basic_functionality(self):
        """Test basic functionality works."""
        obj = MyClass()
        result = obj.method("input")
        assert result == "expected"

    def test_error_handling(self):
        """Test error is raised for invalid input."""
        obj = MyClass()
        with pytest.raises(ValueError):
            obj.method(None)
```

### Best Practices

1. **One assertion per test** (when possible)
2. **Descriptive test names** (`test_add_user_with_duplicate_id_fails`)
3. **Arrange-Act-Assert** pattern
4. **Use fixtures** for shared setup
5. **Test edge cases** (None, empty, large values)
6. **Add docstrings** to explain what's tested

## Fixtures

### Shared Fixtures (`tests/conftest.py`)

- `temp_storage` - Temporary MemoryStorage
- `user_manager` - UserManager instance
- `admin_manager` - AdminManager instance
- `mock_telegram_update` - Mock Telegram update
- `mock_telegram_context` - Mock Telegram context
- `sample_user_data` - Sample user dictionary
- `sample_admin_data` - Sample admin list

### Integration Fixtures (`tests/integration/conftest.py`)

- `deployment_config` - Deployment configuration
- `get_cli_output` - Helper for CLI command testing
- `assert_cli_success` - Assert CLI command succeeded
- `assert_cli_error` - Assert CLI command failed

### E2E Fixtures (`tests/e2e/conftest.py`, `tests/integration/fixtures/mock_vps.py`)

- `mock_vps` - Mock VPS (session-scoped, reused)
- `clean_vps` - Clean VPS (function-scoped, isolated)
- `test_bot_project` - Test bot project setup
- `deployed_bot` - Fully deployed bot on Mock VPS

## Configuration

### pytest.ini (pyproject.toml)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-ra",
    "--strict-markers",
    "--cov-fail-under=50",
]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
]
```

### tox.ini

Multi-version testing configuration for Python 3.9-3.12.

```bash
# Run on all versions
tox

# Run on specific version
tox -e py39
tox -e py312
```

## Troubleshooting

### Import Errors

```bash
# Reinstall package in development mode
pip install -e ".[dev]"
```

### Docker Issues (Integration Tests)

```bash
# Check Docker is running
docker ps

# Clean up containers
docker compose -f tests/integration/fixtures/docker-compose.mock-vps.yml down -v
```

### Slow Tests

```bash
# Find slow tests
pytest --durations=10

# Skip slow tests
pytest -m "not slow"

# Run in parallel
pip install pytest-xdist
pytest -n auto
```

### Coverage Issues

```bash
# Check missing lines
pytest --cov-report=term-missing

# Exclude files from coverage
# Edit .coveragerc or pyproject.toml [tool.coverage.run]
```

## Future Testing Improvements

See GitHub issues with `testing` label for planned improvements.

### High Priority

- [ ] Increase unit test coverage to 85%+
- [ ] Add E2E tests for complete bot lifecycle
- [ ] Add performance/load testing
- [ ] Add contract/API tests

### Medium Priority

- [ ] Add property-based testing (Hypothesis)
- [ ] Add mutation testing (mutmut)
- [ ] Add snapshot testing
- [ ] Add visual regression tests (for CLI output)

### Low Priority

- [ ] Add fuzz testing
- [ ] Add security testing (Bandit integration)
- [ ] Add dependency vulnerability scanning
- [ ] Add test result analytics

## Resources

- **pytest**: https://docs.pytest.org/
- **Coverage.py**: https://coverage.readthedocs.io/
- **unittest.mock**: https://docs.python.org/3/library/unittest.mock.html
- **Testing Guide**: `CONTRIBUTING.md`

## Statistics

```bash
# Count tests
pytest --collect-only | grep "test session starts" -A 1

# Test execution time
pytest --durations=0
```

**Current Stats** (as of 2025-11-28):

- Total tests: **514**
  - Unit tests: ~450 (88%)
  - Integration tests: ~25 (5%)
  - E2E tests: ~60 (12%) - deployment workflows
- Average execution time:
  - Unit: ~30s
  - Integration (fast): ~30s
  - E2E: ~5-30min (Docker builds)
- Coverage: 70% (unit only)

---

For specific test type documentation, see:

- [`tests/unit/README.md`](unit/README.md) - Unit testing guide
- [`tests/integration/README.md`](integration/README.md) - Integration testing guide
- [`tests/e2e/README.md`](e2e/README.md) - E2E testing guide
