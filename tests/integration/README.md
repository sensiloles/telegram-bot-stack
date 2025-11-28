# Integration Tests

This directory contains integration tests for the telegram-bot-stack deployment functionality.

## Overview

Integration tests verify the complete deployment flow from initialization to teardown using a mock VPS environment.

## Mock VPS Environment

### Architecture

The mock VPS is a Docker container that simulates a real VPS server:

- **OS**: Ubuntu 22.04
- **Services**: SSH, Docker, systemd
- **Users**: root (for deployment), testuser (for testing)
- **Port**: SSH on 2222 (mapped from container's 22)

### Components

1. **Dockerfile.mock-vps** - Container definition
2. **docker-compose.mock-vps.yml** - Container orchestration
3. **mock_vps.py** - Python fixtures and utilities

## Running Tests

### Prerequisites

- Docker installed and running
- Docker Compose v2.0+
- Python 3.9+
- pip packages: `pip install -e ".[dev]"`

### Run All Integration Tests

```bash
# From project root
pytest tests/integration/ -v

# Run tests in parallel (faster, requires pytest-xdist)
pytest tests/integration/ -v -n auto

# Run only fast tests (skip slow ones like Docker build)
pytest tests/integration/ -v -m "not slow"

# Run only slow tests
pytest tests/integration/ -v -m "slow"

# Run with detailed output and logging (useful for debugging)
pytest tests/integration/ -v -s --tb=short --log-cli-level=INFO -n auto
```

### Run Specific Test Suite

```bash
# Deployment tests only
./tests/integration/run_integration_tests.sh deployment

# VPS requirements tests only
./tests/integration/run_integration_tests.sh requirements

# Full flow tests only
./tests/integration/run_integration_tests.sh full-flow
```

### Run Specific Test Class

```bash
pytest tests/integration/test_deployment.py::TestDeploymentInit -v
pytest tests/integration/test_vps_requirements.py::TestDockerRequirements -v
```

### Run with Coverage

```bash
pytest tests/integration/ --cov=telegram_bot_stack --cov-report=term
```

### Run in CI Mode

```bash
# Skip slow tests
pytest tests/integration/ -m "not slow" -v
```

## Test Categories

### 1. Deployment Initialization

- `test_deploy_init_interactive` - Interactive setup
- `test_deploy_init_existing_config_no_overwrite` - Config protection
- `test_deploy_init_invalid_ssh_connection` - Error handling

### 2. Deployment Up

- `test_deploy_up_first_time` - First deployment
- `test_deploy_up_without_init` - Error handling

### 3. Deployment Status

- `test_deploy_status_no_deployment` - Status check

### 4. Secrets Management

- `test_secrets_set_and_list` - Secret storage
- `test_secrets_delete` - Secret deletion

### 5. Backup/Restore

- `test_backup_create_and_list` - Backup creation
- (Future) `test_restore_backup` - Data restoration

### 6. Health Checks

- `test_health_check_command` - Health monitoring

### 7. Deployment Down

- `test_deploy_down` - Teardown

### 8. VPS Requirements Validation

- `test_deploy_up_no_docker` - Missing Docker
- `test_deploy_up_docker_not_running` - Docker daemon stopped
- `test_deploy_up_no_docker_compose` - Missing Docker Compose
- `test_deploy_up_old_python` - Outdated Python version
- `test_deploy_up_no_python3` - Missing Python
- `test_doctor_all_requirements_met` - Doctor command (issue #88)
- `test_minimum_docker_version` - Version checks
- `test_minimum_python_version` - Version checks

## Fixtures

### Session-Level Fixtures

- **mock_vps** - Long-lived mock VPS (one per test session)
  - Faster tests (container reused)
  - Shared state between tests

### Function-Level Fixtures

- **clean_vps** - Clean VPS for each test
  - Slower tests (cleanup before/after)
  - Isolated state per test
  - Use for deployment tests

## Writing New Tests

### Example: Testing a New Command

```python
from tests.integration.fixtures.mock_vps import MockVPS

def test_my_command(clean_vps: MockVPS, tmp_path: Path) -> None:
    """Test my new deployment command."""
    os.chdir(tmp_path)
    runner = CliRunner()

    # Initialize deployment
    result_init = runner.invoke(
        main,
        [
            "deploy",
            "init",
            "--host", clean_vps.host,
            "--user", clean_vps.user,
            "--ssh-key", clean_vps.ssh_key_path,
            "--port", str(clean_vps.port),
            "--bot-name", "test-bot",
        ],
    )
    assert result_init.exit_code == 0

    # Test your command
    result = runner.invoke(main, ["deploy", "my-command"])
    assert result.exit_code == 0
    assert "expected output" in result.output
```

### Best Practices

1. **Use clean_vps for deployment tests** - Ensures clean state
2. **Use tmp_path for working directory** - Isolates file operations
3. **Check exit codes AND output** - Verify success and messages
4. **Clean up after yourself** - Remove test files/containers
5. **Add docstrings** - Explain what each test verifies

## Troubleshooting

### Docker Permission Denied

```bash
# Add your user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### SSH Connection Timeout

```bash
# Check container is running
docker ps | grep mock-vps

# Check SSH service
docker exec telegram-bot-stack-mock-vps systemctl status ssh

# View container logs
docker logs telegram-bot-stack-mock-vps
```

### Port Already in Use

```bash
# Stop existing mock VPS
docker compose -f tests/integration/fixtures/docker-compose.mock-vps.yml down

# Or change port in docker-compose.mock-vps.yml
ports:
  - "2223:22"  # Use different port
```

### Tests Hang or Timeout

```bash
# Increase timeout in pytest.ini
timeout = 300

# Or skip slow tests
pytest tests/integration/ -m "not slow"
```

### Clean Up Test Resources

```bash
# Stop all test containers
docker compose -f tests/integration/fixtures/docker-compose.mock-vps.yml down -v

# Remove test images
docker image prune -af

# Remove test volumes
docker volume prune -f
```

## CI/CD Integration

Integration tests run automatically in GitHub Actions:

- **Workflow**: `.github/workflows/integration-tests.yml`
- **Trigger**: Push to main/develop, PRs, manual
- **Matrix**: Python 3.11, 3.12
- **Timeout**: 30 minutes
- **Coverage**: Uploaded to Codecov

### Local CI Simulation

```bash
# Run tests as CI would
docker compose -f tests/integration/fixtures/docker-compose.mock-vps.yml up -d
pytest tests/integration/ -v -m "not slow"
docker compose -f tests/integration/fixtures/docker-compose.mock-vps.yml down -v
```

## Performance

- **Mock VPS startup**: ~30-60 seconds (first time)
- **Test execution**: ~2-5 minutes (full suite)
- **Cleanup**: ~10-20 seconds

## Limitations

1. **Docker-in-Docker** - May have limitations in some CI environments
2. **SSH Key Generation** - Requires SSH client installed
3. **systemd** - May not work in all container configurations
4. **Network isolation** - Tests share host network

## Future Improvements

- [ ] Add systemd service tests
- [ ] Add rollback tests (#76)
- [ ] Add zero-downtime deployment tests (#78)
- [ ] Add multi-environment tests (#83)
- [ ] Add monitoring tests (#82)
- [ ] Optimize container startup time
- [ ] Add Windows/macOS support (Docker Desktop)

## References

- **Issue #85**: https://github.com/sensiloles/telegram-bot-stack/issues/85
- **Deployment Guide**: `docs/deployment_guide.md`
- **Mock VPS Fixture**: `tests/integration/fixtures/mock_vps.py`
