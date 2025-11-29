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

- Config creation and save, nested keys, validation

**test_docker.py** - Docker file generation

- Dockerfile, docker-compose.yml, Makefile rendering

**test_cli.py** - CLI commands

- deploy init/up/status/down commands, error handling

**test_vps.py** - VPS connections

- Connection creation, ports, invalid hosts, context managers

**test_full_deployment_flow.py** - End-to-end deployment ⭐

- Complete Docker deployment workflow
- Python/Docker auto-installation
- Multi-bot deployments, error scenarios

**test_secrets_management.py** - Secrets encryption ⭐

- Encryption/decryption, CRUD operations
- File security (encrypted at rest, 600 permissions)
- Special characters handling

**test_backup_restore.py** - Backup & restore ⭐

- Backup creation, listing, restoration
- Retention policies, local downloads
- Encrypted secrets in backups

**test_rollback_version_tracking.py** - Version tracking ⭐

- Deployment versioning, rollback to previous/specific version
- Docker image cleanup, git commit tracking

**test_health_monitoring.py** - Health checks ⭐

- Container health status, error logs
- Restart detection, Docker Compose detection

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

## Mock VPS (Required for E2E tests)

For comprehensive deployment tests (⭐ marked), build Mock VPS:

```bash
cd tests/integration/fixtures
docker build -t mock-vps:latest -f Dockerfile.mock-vps .
```

**Note:** Basic tests run without Docker. E2E tests use Docker-in-Docker (~5-15min builds).

## Coverage

**Current:** ~24% (integration tests only)
**Target:** 80% combined (unit + integration)

```bash
pytest tests/integration/ --cov=telegram_bot_stack --cov-report=html
open htmlcov/index.html
```

## Test Results

**Status:** ✅ 26 basic + 60+ E2E tests
**Speed:** Basic ~1s | E2E ~5-30min (Docker builds)
**Coverage:** Deployment workflow, secrets, backup, rollback, health

## CI/CD

Integration tests run in GitHub Actions:

- **Workflow**: `.github/workflows/integration-tests.yml`
- **Trigger**: Every pull request
- **Matrix**: Python 3.9, 3.10, 3.11, 3.12
- **Required**: Must pass for PR merge

## Issues

Report issues: https://github.com/sensiloles/telegram-bot-stack/issues
