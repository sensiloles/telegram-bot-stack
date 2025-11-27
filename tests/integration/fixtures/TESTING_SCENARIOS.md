# Testing Scenarios for VPS Requirements

This document describes different VPS configurations for testing edge cases.

## Available Configurations

### 1. Default Configuration (`default`)

Full-featured VPS with all dependencies:

- ✅ Ubuntu 22.04
- ✅ Python 3.11
- ✅ Docker + Docker Compose
- ✅ SSH Server
- ✅ systemd

**Use for**: Normal deployment tests

### 2. No Docker Configuration (`no_docker`)

VPS without Docker installed:

- ✅ Ubuntu 22.04
- ✅ Python 3.11
- ✅ SSH Server
- ❌ No Docker
- ❌ No Docker Compose

**Use for**: Testing missing Docker scenarios

**Tests**:

- `test_deploy_up_no_docker` - Deployment fails gracefully
- `test_doctor_missing_docker` - Doctor detects missing Docker

### 3. Old Python Configuration (`old_python`)

VPS with outdated Python version:

- ✅ Ubuntu 20.04
- ⚠️ Python 3.8 (below minimum 3.9)
- ✅ Docker + Docker Compose
- ✅ SSH Server

**Use for**: Testing Python version compatibility

**Tests**:

- `test_deploy_up_old_python` - Warns about old Python
- `test_minimum_python_version` - Version validation

### 4. Minimal Configuration (`minimal`)

Bare minimum VPS:

- ✅ Ubuntu 22.04
- ✅ SSH Server
- ❌ No Python
- ❌ No Docker
- ❌ No system packages

**Use for**: Testing fresh VPS setup

**Tests**:

- `test_deploy_up_no_python3` - Missing Python
- `test_deploy_validates_before_upload` - Early validation

## Usage Example

### Using Custom Configuration in Tests

```python
# tests/integration/test_custom.py

import pytest
from tests.integration.fixtures.mock_vps import MockVPS
from tests.integration.fixtures.mock_vps_configs import (
    get_dockerfile_for_config,
    get_docker_compose_for_config,
)

@pytest.fixture
def vps_no_docker(tmp_path):
    """Create VPS without Docker."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    # Write custom Dockerfile
    dockerfile = config_dir / "Dockerfile.mock-vps-no-docker"
    dockerfile.write_text(get_dockerfile_for_config("no_docker"))

    # Write custom docker-compose.yml
    compose_file = config_dir / "docker-compose.yml"
    compose_file.write_text(get_docker_compose_for_config("no_docker"))

    # Start custom VPS
    vps = MockVPS(port=2223)  # Use different port
    vps.start()

    yield vps

    vps.cleanup()
    vps.stop()

def test_with_custom_vps(vps_no_docker):
    """Test deployment on VPS without Docker."""
    # Docker should not be available
    exit_code, stdout, stderr = vps_no_docker.exec("docker --version")
    assert exit_code != 0

    # Python should be available
    exit_code, stdout, stderr = vps_no_docker.exec("python3 --version")
    assert exit_code == 0
```

## Test Matrix

| Configuration | Python | Docker | Docker Compose | systemd | Use Case           |
| ------------- | ------ | ------ | -------------- | ------- | ------------------ |
| default       | 3.11   | ✅     | ✅             | ✅      | Normal deployment  |
| no_docker     | 3.11   | ❌     | ❌             | ✅      | Missing Docker     |
| old_python    | 3.8    | ✅     | ✅             | ✅      | Old Python version |
| minimal       | ❌     | ❌     | ❌             | ❌      | Fresh VPS          |

## Creating Custom Configurations

### Step 1: Define Dockerfile

```python
# tests/integration/fixtures/mock_vps_configs.py

def get_dockerfile_for_config(config: MockVPSConfig) -> str:
    if config == "your_custom_config":
        return """
FROM ubuntu:22.04
# ... your custom setup ...
"""
```

### Step 2: Use in Tests

```python
@pytest.fixture
def custom_vps():
    config = "your_custom_config"
    # ... setup VPS with custom config ...
```

## Common Test Patterns

### Testing Missing Dependencies

```python
def test_missing_dependency(clean_vps: MockVPS):
    # Remove dependency
    clean_vps.exec("apt-get remove -y package-name")

    # Try deployment
    result = runner.invoke(main, ["deploy", "up"])

    # Should fail gracefully
    assert result.exit_code != 0
    assert "package-name" in result.output.lower()
```

### Testing Version Requirements

```python
def test_version_requirement(clean_vps: MockVPS):
    # Check current version
    exit_code, stdout, _ = clean_vps.exec("python3 --version")

    # Verify minimum version
    assert "Python 3.9" in stdout or "Python 3.1" in stdout
```

### Testing Auto-Recovery

```python
def test_auto_recovery(clean_vps: MockVPS):
    # Break something
    clean_vps.exec("systemctl stop docker")

    # Deployment should detect and suggest fix
    result = runner.invoke(main, ["deploy", "up"])

    assert "docker" in result.output.lower()
    assert "not running" in result.output.lower()
```

## Best Practices

1. **Use `clean_vps` for tests that modify VPS state**

   - Ensures isolation between tests
   - Automatic cleanup before/after

2. **Test both detection and recovery**

   - Detect missing dependencies
   - Provide helpful error messages
   - Suggest fixes (e.g., "Run: apt-get install docker")

3. **Test early validation**

   - Check requirements before uploading files
   - Fast failure is better than slow failure

4. **Document expected behavior**
   - What should happen when Docker is missing?
   - Should deployment auto-install or fail?

## Related Issues

- **#85**: Integration tests for deployment
- **#88**: Doctor command for diagnostics
- **#80**: Deployment verification

## Future Enhancements

- [ ] Add auto-installation of missing dependencies
- [ ] Add more granular version checks
- [ ] Add network connectivity tests
- [ ] Add disk space validation
- [ ] Add memory requirements checks
