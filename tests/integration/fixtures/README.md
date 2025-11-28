# Integration Test Fixtures

This directory contains fixtures and infrastructure for integration testing.

## Files

- `Dockerfile.mock-vps` - Docker container definition for mock VPS
- `docker-compose.mock-vps.yml` - Docker Compose configuration
- `mock_vps.py` - Pytest fixtures and utilities
- `__init__.py` - Package initialization

## Mock VPS Setup

### Quick Start

```python
import pytest
from tests.integration.fixtures.mock_vps import MockVPS, clean_vps

def test_deployment(clean_vps: MockVPS):
    """Test with clean VPS environment."""
    # VPS is automatically started and cleaned
    assert clean_vps.host == "localhost"
    assert clean_vps.port == 2222

    # Execute commands on VPS
    exit_code, stdout, stderr = clean_vps.exec("ls /opt")
    assert exit_code == 0
```

### Manual Setup

```bash
# Build and start mock VPS
cd tests/integration/fixtures
docker compose -f docker-compose.mock-vps.yml up -d --build

# Wait for SSH to be ready (~30 seconds)
docker logs -f telegram-bot-stack-mock-vps

# Test SSH connection
ssh -i .ssh-test/id_rsa -p 2222 root@localhost

# Stop and cleanup
docker compose -f docker-compose.mock-vps.yml down -v
```

## Mock VPS Features

### Services

- ✅ SSH Server (port 22, mapped to 2222)
- ✅ Docker Engine
- ✅ Docker Compose
- ✅ Python 3.11
- ✅ systemd (limited in containers)

### Users

- **root** - Deployment user (key-based auth)
- **testuser** - Testing user (password: testpass)

### Networking

- Port 2222 (host) → Port 22 (container)
- Bridge network for isolation

### Storage

- Volume: `mock-vps-data` → `/opt` (persistent)
- Docker socket mounted for container management

## Fixtures

### `mock_vps` (session scope)

Long-lived VPS for faster tests. Container is started once and reused.

```python
def test_fast(mock_vps: MockVPS):
    # Shared state between tests
    # Good for read-only tests
    pass
```

### `clean_vps` (function scope)

Clean VPS for each test. Cleanup before and after.

```python
def test_isolated(clean_vps: MockVPS):
    # Fresh state for each test
    # Good for deployment tests
    pass
```

## MockVPS API

### Connection Properties

```python
vps.host         # "localhost"
vps.port         # 2222
vps.user         # "root"
vps.ssh_key_path # Path to private key
```

### Methods

```python
# Lifecycle
vps.start()      # Start container
vps.stop()       # Stop container
vps.cleanup()    # Remove test containers/volumes

# Execution
exit_code, stdout, stderr = vps.exec("command")

# Container Management
vps.is_container_running("bot-name")
vps.get_container_logs("bot-name")
```

## Troubleshooting

### Container Won't Start

```bash
# Check Docker is running
docker ps

# Check logs
docker logs telegram-bot-stack-mock-vps

# Rebuild container
docker compose -f docker-compose.mock-vps.yml build --no-cache
```

### SSH Connection Refused

```bash
# Check SSH service inside container
docker exec telegram-bot-stack-mock-vps systemctl status ssh

# Check SSH port mapping
docker port telegram-bot-stack-mock-vps 22

# Test SSH manually
ssh -v -i .ssh-test/id_rsa -p 2222 root@localhost
```

### Permission Errors

```bash
# Fix SSH key permissions
chmod 700 .ssh-test
chmod 600 .ssh-test/id_rsa
chmod 644 .ssh-test/id_rsa.pub
```

## Maintenance

### Update Base Image

```dockerfile
# Dockerfile.mock-vps
FROM ubuntu:24.04  # Update version
```

### Update Docker Compose

```bash
# Check current version
docker-compose version

# Update version in docker-compose.mock-vps.yml
version: '3.9'
```

### Add New Services

```dockerfile
# Dockerfile.mock-vps
RUN apt-get install -y new-service
```

## Security Notes

⚠️ **This is for testing only!**

- SSH password authentication is disabled
- Root login is enabled (for testing)
- Test SSH keys are generated automatically
- Container runs in privileged mode (for Docker-in-Docker)

**Never use this configuration in production!**
