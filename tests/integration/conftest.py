"""Pytest configuration for integration tests."""

import functools
import logging
import os
import sys
from pathlib import Path
from typing import Generator

import pytest
import yaml

# Configure logging for integration tests
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
    force=True,  # Override any existing config
)

# Set specific loggers to DEBUG for more details
logging.getLogger("tests.integration.fixtures.mock_vps").setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)


def log_test(func):
    """Decorator to add logging to integration tests."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        test_name = func.__name__
        logger.info("=" * 80)
        logger.info(f"TEST: {test_name} - Starting")
        logger.info("=" * 80)
        try:
            result = func(*args, **kwargs)
            logger.info(f"TEST: {test_name} - PASSED ✓")
            logger.info("=" * 80)
            return result
        except Exception as e:
            logger.error(f"TEST: {test_name} - FAILED ✗")
            logger.error(f"Error: {e}")
            logger.info("=" * 80)
            raise

    return wrapper


# Pytest hooks for automatic test logging
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    """Log test execution with detailed information."""
    test_name = item.nodeid
    logger.info("")
    logger.info("▶" * 40)
    logger.info(f"▶▶▶ TEST STARTING: {test_name}")
    logger.info("▶" * 40)
    logger.info("")

    outcome = yield

    logger.info("")
    if outcome.excinfo is None:
        logger.info("✓" * 40)
        logger.info(f"✓✓✓ TEST PASSED: {test_name}")
        logger.info("✓" * 40)
    else:
        logger.error("✗" * 40)
        logger.error(f"✗✗✗ TEST FAILED: {test_name}")
        logger.error(f"Error type: {outcome.excinfo[0].__name__}")
        logger.error(f"Error message: {str(outcome.excinfo[1])[:200]}")
        logger.error("✗" * 40)
    logger.info("")


# Import fixtures to make them available
from tests.integration.fixtures.mock_vps import (  # noqa: F401, E402
    MockVPS,
    clean_vps,
    mock_vps,
)


@pytest.fixture
def deployment_config(
    clean_vps: MockVPS,  # noqa: F811
    tmp_path: Path,
) -> Generator[Path, None, None]:
    """Create deploy.yaml configuration for tests.

    This fixture creates a complete deploy.yaml file with all necessary
    configuration for deployment tests. This solves the CliRunner isolation
    issue where files created in one invoke() are not available in another.

    Args:
        clean_vps: Mock VPS fixture
        tmp_path: Pytest temporary directory

    Yields:
        Path to deploy.yaml file
    """
    from telegram_bot_stack.cli.utils.secrets import SecretsManager

    config = {
        "vps": {
            "host": clean_vps.host,
            "user": clean_vps.user,
            "ssh_key": clean_vps.ssh_key_path,
            "port": clean_vps.port,
        },
        "bot": {
            "name": "test-bot",
            "token_env": "BOT_TOKEN",
            "entry_point": "bot.py",
            "python_version": "3.11",
        },
        "deployment": {
            "method": "docker",
            "auto_restart": True,
            "log_rotation": True,
        },
        "secrets": {
            "encryption_key": SecretsManager.generate_key(),
        },
        "resources": {
            "memory_limit": "256M",
            "memory_reservation": "128M",
            "cpu_limit": "0.5",
            "cpu_reservation": "0.25",
        },
        "logging": {
            "level": "INFO",
            "max_size": "5m",
            "max_files": "5",
        },
        "environment": {
            "timezone": "UTC",
        },
        "backup": {
            "enabled": True,
            "auto_backup_before_update": True,
            "auto_backup_before_cleanup": True,
            "retention_days": 7,
            "max_backups": 10,
        },
    }

    # Change to tmp_path so deploy.yaml is created there
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        deploy_yaml = tmp_path / "deploy.yaml"
        with open(deploy_yaml, "w") as f:
            yaml.safe_dump(config, f)

        yield deploy_yaml
    finally:
        os.chdir(original_cwd)
