# Tests

Comprehensive test suite for telegram-bot-stack framework.

## Structure

```
tests/
├── unit/              # Unit tests (fast, isolated)
│   ├── agent/         # Agent functionality tests
│   ├── cli/           # CLI commands tests
│   ├── core/          # Core framework tests
│   └── examples/      # Example bots tests
│
├── integration/       # Integration tests (slow, Docker required)
│   ├── fixtures/      # Mock VPS and test infrastructure
│   ├── test_deployment.py
│   ├── test_full_flow.py
│   └── test_vps_requirements.py
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
# Unit tests only (fast, no Docker)
pytest tests/unit/ -v
make test-unit

# Integration tests only (slow, requires Docker)
pytest tests/integration/ -v
make test-integration
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

**What**: Test component interactions with real infrastructure

**Characteristics**:

- 🐌 **Slow**: Seconds to minutes per test
- 🐳 **Docker**: Requires Mock VPS container
- 🔄 **Realistic**: Tests real deployment flows
- 📊 **Coverage**: 25+ tests

**Run**: `pytest tests/integration/` or `make test-integration`

**Docs**: [`tests/integration/README.md`](integration/README.md)

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
make test                  # Run all tests
make test-unit            # Run unit tests only
make test-integration     # Run integration tests (Docker required)
make coverage             # Run with coverage report
make test-all-versions    # Test on Python 3.9-3.12 (via tox)
```

### Pytest Options

```bash
# Verbose output
pytest tests/ -v

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

Tests run automatically in GitHub Actions:

**Unit Tests** (`.github/workflows/tests.yml`):

- ✅ Required for PR merge
- 🚀 Fast (2-3 minutes)
- 🐍 Python 3.9, 3.10, 3.11, 3.12
- 📊 Coverage uploaded to Codecov

**Integration Tests** (`.github/workflows/integration-tests.yml`):

- ⚠️ Non-blocking (won't prevent merge)
- 🐳 Requires Docker
- 🐍 Python 3.11, 3.12
- ⏱️ Timeout: 30 minutes

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

- `mock_vps` - Mock VPS (session-scoped, reused)
- `clean_vps` - Clean VPS (function-scoped, isolated)

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

- Total tests: ~465
- Unit tests: ~440 (95%)
- Integration tests: ~25 (5%)
- Average execution time: ~30s (unit), ~5min (integration)
- Coverage: 70%

---

For specific test type documentation, see:

- [`tests/unit/README.md`](unit/README.md) - Unit testing guide
- [`tests/integration/README.md`](integration/README.md) - Integration testing guide
