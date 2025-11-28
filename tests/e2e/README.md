# E2E Tests

End-to-end tests for telegram-bot-stack deployment killer feature.

## Overview

E2E tests validate full deployment workflows using Mock VPS (Docker container simulating a real VPS). These tests are **slower** but provide comprehensive coverage of deployment features including secrets, backups, rollbacks, and health monitoring.

**Speed:** ~5-30 minutes (Docker builds)
**Dependencies:** Docker, Mock VPS image

## Structure

```
tests/e2e/
├── conftest.py              # Shared E2E fixtures
└── deployment/              # Deployment E2E tests
    ├── conftest.py          # Deployment-specific fixtures
    ├── test_full_deployment_flow.py      # Complete deployment workflow ⭐
    ├── test_secrets_management.py        # Secrets encryption/decryption ⭐
    ├── test_backup_restore.py            # Backup & restore ⭐
    ├── test_rollback_version_tracking.py # Version tracking & rollback ⭐
    └── test_health_monitoring.py         # Health checks & monitoring ⭐
```

## Setup

### 1. Build Mock VPS Image

E2E tests require Mock VPS Docker image:

```bash
make build-mock-vps
# or
cd tests/integration/fixtures
docker build -t mock-vps:latest -f Dockerfile.mock-vps .
```

### 2. Run Tests

**Note:** E2E tests are skipped by default (to avoid Docker-in-Docker issues locally). Use `--run-e2e` flag to run them.

```bash
# All E2E tests (recommended - uses Makefile)
make test-e2e

# Deployment E2E tests only
make test-deploy

# With pytest directly (requires --run-e2e flag)
pytest tests/e2e/ -v --run-e2e

# Specific test file
pytest tests/e2e/deployment/test_full_deployment_flow.py -v --run-e2e

# Specific test
pytest tests/e2e/deployment/test_secrets_management.py::TestSecretsEncryption::test_encrypt_decrypt_secret -v --run-e2e

# Without --run-e2e flag, tests will be skipped
pytest tests/e2e/  # Will skip all E2E tests
```

## Test Coverage

### Deployment Flow (`test_full_deployment_flow.py`)

- ✅ Full Docker deployment (init → up → status → logs)
- ✅ Python/Docker auto-installation
- ✅ Multi-bot deployments
- ✅ Error scenarios (invalid config, SSH failures)

### Secrets Management (`test_secrets_management.py`)

- ✅ Encryption/decryption with Fernet
- ✅ CRUD operations (set, get, list, remove)
- ✅ File security (encrypted at rest, 600 permissions)
- ✅ Special characters handling

### Backup & Restore (`test_backup_restore.py`)

- ✅ Backup creation with/without data
- ✅ Backup listing and restoration
- ✅ Retention policies (by count, by age)
- ✅ Local backup downloads
- ✅ Encrypted secrets in backups

### Version Tracking & Rollback (`test_rollback_version_tracking.py`)

- ✅ Deployment versioning
- ✅ Rollback to previous/specific version
- ✅ Docker image cleanup
- ✅ Git commit tracking

### Health Monitoring (`test_health_monitoring.py`)

- ✅ Container health status checks
- ✅ Error log retrieval
- ✅ Restart detection
- ✅ Docker Compose command detection

## CI/CD

E2E tests run in GitHub Actions:

- **Workflow**: `.github/workflows/e2e-tests.yml`
- **Trigger:** PRs to main/develop, manual dispatch
- **Environment:** Ubuntu with Docker
- **Status:** Non-blocking (won't prevent PR merge if they fail)
- **Timeout:** 45 minutes
- **Python:** 3.12 only (latest)
- **Part of**: Release pipeline (`.github/workflows/release.yml`)

## Troubleshooting

### Mock VPS image not found

```bash
Error: docker.errors.ImageNotFound: 404 Client Error for mock-vps
Solution: make build-mock-vps
```

### Tests timing out

E2E tests can be slow due to Docker-in-Docker operations. Increase timeout:

```bash
pytest tests/e2e/ -v --timeout=600
```

### Docker-in-Docker not working

Mock VPS requires privileged mode and may not work in all environments:

- ✅ Works: CI/CD (GitHub Actions), local Docker
- ❌ May fail: Some cloud environments, nested virtualization

### Container cleanup

After failed tests, clean up Docker resources:

```bash
docker ps -a  # List all containers
docker rm -f $(docker ps -aq)  # Remove all containers
docker system prune -af  # Clean up everything
```

## Development Workflow

When working on deployment features:

1. **Write unit tests first** (`tests/unit/`)
2. **Add integration tests** (`tests/integration/`) for basic logic
3. **Add E2E tests** (`tests/e2e/`) for full workflow validation
4. **Run locally** before pushing:
   ```bash
   make test-fast      # Quick validation
   make test-deploy    # E2E deployment tests
   ```
5. **Check CI** after pushing

## Notes

- E2E tests use real Docker containers, not mocks
- Mock VPS simulates a real VPS environment
- Tests are isolated (each test gets a fresh VPS)
- Cleanup is automatic (fixtures handle teardown)
- Logs are verbose for debugging
