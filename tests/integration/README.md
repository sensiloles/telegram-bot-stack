# Integration Tests

Integration tests for VPS deployment and bot functionality.

## Structure

```
tests/integration/
├── deployment/          # Deployment tests
│   ├── test_config.py   # Configuration management
│   ├── test_docker.py   # Docker file generation
│   ├── test_cli.py      # CLI commands
│   └── test_vps.py      # VPS connections
├── bot/                 # Bot functionality tests
│   └── test_user_flow.py # User/admin flows
├── fixtures/            # Test fixtures
│   ├── mock_vps.py      # Mock VPS container
│   ├── Dockerfile.mock-vps
│   └── docker-compose.mock-vps.yml
├── conftest.py          # Pytest configuration
└── README.md            # This file
```

## Quick Start

```bash
# Run all integration tests
python3 -m pytest tests/integration/ -v

# Run specific category
python3 -m pytest tests/integration/deployment/ -v
python3 -m pytest tests/integration/bot/ -v

# Run specific test file
python3 -m pytest tests/integration/deployment/test_docker.py -v

# With coverage
python3 -m pytest tests/integration/ --cov=telegram_bot_stack --cov-report=term
```

## Test Categories

### Deployment Tests (`deployment/`)

**test_config.py** - Configuration management

- Config creation and save
- Nested keys handling
- Validation (missing fields)

**test_docker.py** - Docker file generation

- Dockerfile rendering (Python versions, entrypoints)
- docker-compose.yml rendering (resources, limits)
- Makefile generation (targets, compose detection)

**test_cli.py** - CLI commands

- `deploy init` command
- `deploy up` command
- `deploy status` command
- `deploy down` command
- Error handling (missing config)

**test_vps.py** - VPS connections

- Connection object creation
- Custom ports and users
- Invalid host handling
- Context manager support

### Bot Tests (`bot/`)

**test_user_flow.py** - User and admin flows

- User registration
- Admin management
- Storage backends (JSON, Memory, SQL)
- Data persistence
- Complete user lifecycles

## Running Tests

```bash
# All tests (fast, ~1 second)
pytest tests/integration/ -v

# Deployment tests only
pytest tests/integration/deployment/ -v

# Bot tests only
pytest tests/integration/bot/ -v

# Specific test class
pytest tests/integration/deployment/test_docker.py::TestDockerfileGeneration -v

# With output (debugging)
pytest tests/integration/ -v -s

# Parallel execution
pytest tests/integration/ -v -n auto
```

## Mock VPS (Optional)

For advanced SSH testing, build Mock VPS container:

```bash
cd tests/integration/fixtures
docker build -t mock-vps:latest -f Dockerfile.mock-vps .
```

**Note:** Most tests don't require Mock VPS and run without Docker.

## Coverage

**Current:** ~24% (integration tests only)
**Target:** 80% combined (unit + integration)

```bash
pytest tests/integration/ --cov=telegram_bot_stack --cov-report=html
open htmlcov/index.html
```

## Test Results

**Status:** ✅ 26/26 tests passing (100%)
**Speed:** ⚡ ~0.8 seconds
**Dependencies:** Minimal (no Docker required)

## CI/CD

Tests run in GitHub Actions (`.github/workflows/integration-tests.yml`)

## Issues

Report issues: https://github.com/sensiloles/telegram-bot-stack/issues
