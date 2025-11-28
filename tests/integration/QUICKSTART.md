# Integration Tests - Quick Start

## TL;DR

```bash
# 1. Make sure Docker is running
docker ps

# 2. Run integration tests
make test-integration

# OR
pytest tests/integration/ -v
```

## What Gets Tested?

- Full deployment flow from `init` to `up`
- SSH connection to VPS
- Docker container deployment
- Secrets management (encryption/decryption)
- Backup/restore functionality
- Health checks
- Deployment teardown
- VPS requirements validation (missing Docker, old Python, etc.)
- Doctor command for diagnostics (issue #88)

## First Time Setup

### 1. Install Dependencies

```bash
pip install -e ".[dev]"
```

### 2. Make Sure Docker is Running

```bash
# Check Docker
docker --version
docker compose version

# Test Docker
docker ps
```

### 3. Run Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Or use the convenience script
./tests/integration/run_integration_tests.sh

# Run specific test suite
./tests/integration/run_integration_tests.sh requirements  # VPS requirements only
./tests/integration/run_integration_tests.sh deployment   # Deployment only

# Or use Makefile
make test-integration
```

## What Happens?

1. **Docker container starts** - Mock VPS (Ubuntu 22.04 + SSH + Docker)
2. **Tests run** - Complete deployment flow verification
3. **Cleanup** - Container stops, resources cleaned up

### Mock VPS Details

- **OS**: Ubuntu 22.04
- **Services**: SSH (port 2222), Docker, systemd
- **User**: root (key-based auth)
- **Network**: localhost:2222

## Example: Manual Test

```bash
# Start mock VPS
cd tests/integration/fixtures
docker compose -f docker-compose.mock-vps.yml up -d

# Wait for SSH (~30 seconds)
docker logs -f telegram-bot-stack-mock-vps

# Test SSH connection (in another terminal)
# Note: SSH key is auto-generated in .ssh-test/
ssh -i .ssh-test/id_rsa -p 2222 root@localhost

# Run commands
ls /opt
docker ps
exit

# Stop mock VPS
docker compose -f docker-compose.mock-vps.yml down -v
```

## Troubleshooting

### Docker Not Running

```
Error: Cannot connect to Docker daemon
```

**Solution**: Start Docker Desktop or Docker service

### Port Already in Use

```
Error: Port 2222 already in use
```

**Solution**:

```bash
# Stop existing container
docker compose -f tests/integration/fixtures/docker-compose.mock-vps.yml down

# Or change port in docker-compose.mock-vps.yml
```

### Tests Timeout

```
Error: SSH connection timeout
```

**Solution**:

```bash
# Check container logs
docker logs telegram-bot-stack-mock-vps

# Restart container
docker compose -f tests/integration/fixtures/docker-compose.mock-vps.yml restart
```

### Permission Denied (SSH)

```
Error: Permission denied (publickey)
```

**Solution**:

```bash
# Fix SSH key permissions
chmod 700 tests/integration/fixtures/.ssh-test
chmod 600 tests/integration/fixtures/.ssh-test/id_rsa
```

## CI/CD

Integration tests run automatically in GitHub Actions:

- **Workflow**: `.github/workflows/integration-tests.yml`
- **Trigger**: Push, PR, manual dispatch
- **Python**: 3.11, 3.12
- **Timeout**: 30 minutes

## Performance

| Stage           | Time                  |
| --------------- | --------------------- |
| Container start | ~30-60s (first time)  |
| Test execution  | ~2-5 min (full suite) |
| Cleanup         | ~10-20s               |
| **Total**       | **~3-7 min**          |

## Next Steps

1. Run tests locally: `make test-integration`
2. Read full docs: [tests/integration/README.md](README.md)
3. Write custom tests: [tests/integration/fixtures/README.md](fixtures/README.md)
4. Check CI status: [GitHub Actions](https://github.com/sensiloles/telegram-bot-stack/actions)

## Related Issues

- **#85**: Integration tests for deployment
- **#27**: VPS Deploy CLI
- **#76**: Rollback mechanism
- **#77**: Health checks
- **#79**: Secrets management
- **#81**: Backup/restore

---

**Need help?** Check [Integration Testing README](README.md) or open an issue!
