# Unit Tests

Fast, isolated tests for individual functions, methods, and classes.

## Overview

Unit tests verify individual components in isolation without external dependencies like databases, networks, or Docker. They use mocks and stubs to isolate code under test.

**Characteristics:**

- ⚡ **Fast**: Milliseconds per test
- 🔒 **Isolated**: No external dependencies
- 🎯 **Focused**: One function/method per test
- 📊 **Coverage**: ~440 tests, 70%+ coverage

## Structure

```
tests/unit/
├── agent/          # Agent functionality (cache, metrics)
├── cli/            # CLI commands and utilities
├── core/           # Core framework (storage, managers, decorators)
└── examples/       # Example bots verification
```

## Running Tests

### All Unit Tests

```bash
# Via pytest
pytest tests/unit/ -v

# Via make
make test-unit

# With coverage
pytest tests/unit/ --cov=telegram_bot_stack --cov-report=term
```

### Specific Module

```bash
# Core tests only
pytest tests/unit/core/ -v

# CLI tests only
pytest tests/unit/cli/ -v

# Single test file
pytest tests/unit/core/test_storage.py -v

# Single test function
pytest tests/unit/core/test_storage.py::test_save_and_load -v
```

### With Markers

```bash
# Fast tests only (if marked)
pytest tests/unit/ -m "not slow" -v

# Skip certain tests
pytest tests/unit/ -m "not requires_network" -v
```

## Test Categories

### 1. Core Framework (`tests/unit/core/`)

**Storage**:

- `test_storage.py` - JSON storage backend
- `test_sql_storage.py` - SQL storage backend
- Storage factory and interfaces

**Managers**:

- `test_admin_manager.py` - Admin user management
- `test_user_manager.py` - User management

**Bot Base**:

- `test_bot_base.py` - Bot initialization, commands, hooks

**Decorators**:

- `test_decorators.py` - Rate limiting, authentication

### 2. CLI Commands (`tests/unit/cli/`)

**Project Management**:

- `test_init_command.py` - Project initialization
- `test_new_command.py` - New bot creation
- `test_dev_command.py` - Development mode

**Deployment**:

- `test_deploy_command.py` - Deploy commands (init, up, down, status)
- `test_deployment_utils.py` - Config, templates, utilities
- `test_vps_utils.py` - VPS connection, Docker checks

**Security & Backup**:

- `test_secrets.py` - Secrets encryption/decryption
- `test_backup.py` - Backup creation/restoration

**Utilities**:

- `test_utils.py` - Venv, dependencies, git, IDE setup
- `test_version_tracking.py` - Deployment version tracking
- `test_validate_command.py` - Bot validation

### 3. Agent Tools (`tests/unit/agent/`)

- `test_agent_cache.py` - Agent caching system
- `test_agent_metrics.py` - Agent metrics logging

### 4. Example Bots (`tests/unit/examples/`)

- `test_examples.py` - All examples integrity check
- `test_echo_bot.py` - Echo bot functionality
- `test_counter_bot.py` - Counter bot functionality
- `test_menu_bot.py` - Menu bot functionality
- `test_poll_bot.py` - Poll bot functionality
- `test_quit_smoking_bot.py` - Quit smoking bot functionality
- `test_reminder_bot.py` - Reminder bot functionality

## Writing Unit Tests

### Basic Example

```python
"""Test module for my_module."""

import pytest
from telegram_bot_stack.my_module import MyClass


class TestMyClass:
    """Tests for MyClass."""

    def test_initialization(self):
        """Test MyClass initializes correctly."""
        obj = MyClass(param="value")
        assert obj.param == "value"

    def test_method_success(self):
        """Test method succeeds with valid input."""
        obj = MyClass()
        result = obj.method("input")
        assert result == "expected_output"

    def test_method_error(self):
        """Test method raises error with invalid input."""
        obj = MyClass()
        with pytest.raises(ValueError, match="Invalid input"):
            obj.method(None)
```

### Using Mocks

```python
from unittest.mock import Mock, patch, MagicMock

def test_with_mock():
    """Test using mocked dependencies."""
    # Mock external dependency
    mock_storage = Mock()
    mock_storage.load.return_value = {"key": "value"}

    # Test with mock
    manager = MyManager(storage=mock_storage)
    result = manager.get_data("key")

    # Verify mock was called
    mock_storage.load.assert_called_once_with("key")
    assert result == "value"

@patch('telegram_bot_stack.module.external_api')
def test_with_patch(mock_api):
    """Test using patched external API."""
    mock_api.return_value = "mocked_response"

    result = my_function_that_calls_api()

    assert result == "mocked_response"
    mock_api.assert_called_once()
```

### Using Fixtures

```python
import pytest

@pytest.fixture
def sample_storage():
    """Create temporary storage for testing."""
    from telegram_bot_stack.storage import MemoryStorage
    return MemoryStorage()

@pytest.fixture
def sample_user_data():
    """Sample user data."""
    return {
        "user_id": 12345,
        "username": "testuser",
        "first_name": "Test",
    }

def test_with_fixtures(sample_storage, sample_user_data):
    """Test using fixtures."""
    sample_storage.save("user_123", sample_user_data)
    loaded = sample_storage.load("user_123")
    assert loaded == sample_user_data
```

## Best Practices

### 1. Test One Thing

```python
# ✅ Good - tests one behavior
def test_add_user_success():
    manager = UserManager(storage)
    result = manager.add_user(12345)
    assert result is True

# ❌ Bad - tests multiple behaviors
def test_user_operations():
    manager = UserManager(storage)
    manager.add_user(12345)
    manager.remove_user(12345)
    manager.add_admin(12345)
    # Too much in one test
```

### 2. Use Descriptive Names

```python
# ✅ Good - clear what's being tested
def test_add_user_with_duplicate_id_returns_false():
    ...

# ❌ Bad - unclear what's being tested
def test_add_user_2():
    ...
```

### 3. Arrange-Act-Assert (AAA) Pattern

```python
def test_user_registration():
    # Arrange - setup test data
    manager = UserManager(storage)
    user_id = 12345

    # Act - perform action
    result = manager.register_user(user_id)

    # Assert - verify result
    assert result is True
    assert manager.user_exists(user_id)
```

### 4. Test Edge Cases

```python
def test_edge_cases():
    """Test boundary conditions."""
    manager = UserManager(storage)

    # Empty input
    with pytest.raises(ValueError):
        manager.add_user(None)

    # Zero value
    assert manager.add_user(0) is True

    # Large value
    assert manager.add_user(999999999) is True

    # Negative value
    with pytest.raises(ValueError):
        manager.add_user(-1)
```

### 5. Use Parametrize for Multiple Cases

```python
@pytest.mark.parametrize("user_id,expected", [
    (12345, True),
    (67890, True),
    (0, True),
])
def test_add_user_with_various_ids(user_id, expected):
    """Test adding users with different IDs."""
    manager = UserManager(storage)
    result = manager.add_user(user_id)
    assert result == expected
```

## Coverage Goals

- **Target**: ≥80% line coverage for `telegram_bot_stack/`
- **Current**: ~80%
- **Required**: ≥75% (CI requirement)

### Check Coverage

```bash
# Generate coverage report
pytest tests/unit/ --cov=telegram_bot_stack --cov-report=html

# Open in browser
open htmlcov/index.html
```

### Improve Coverage

1. Identify uncovered lines: `pytest --cov-report=term-missing`
2. Add tests for uncovered code
3. Focus on critical paths first (error handling, edge cases)

## CI/CD Integration

Unit tests run automatically in GitHub Actions:

- **Workflow**: `.github/workflows/unit-tests.yml`
- **Trigger**: Every pull request
- **Matrix**: Python 3.9, 3.10, 3.11, 3.12
- **Timeout**: 10 minutes
- **Required**: Must pass for PR merge

## Troubleshooting

### Import Errors

```bash
# Ensure package is installed
pip install -e ".[dev]"
```

### Fixture Not Found

```bash
# Check conftest.py exists in:
# - tests/conftest.py (shared fixtures)
# - tests/unit/core/conftest.py (module-specific)
```

### Tests Too Slow

```bash
# Profile slow tests
pytest tests/unit/ --durations=10
```

## Future Improvements

See GitHub issues with label `testing`:

- [ ] Increase coverage to 85%+ (#TBD)
- [ ] Add property-based testing with Hypothesis (#TBD)
- [ ] Add mutation testing (#TBD)
- [ ] Add performance benchmarks (#TBD)

## References

- **pytest docs**: https://docs.pytest.org/
- **unittest.mock**: https://docs.python.org/3/library/unittest.mock.html
- **Testing best practices**: `CONTRIBUTING.md`
