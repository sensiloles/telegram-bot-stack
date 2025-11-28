"""Pytest configuration for integration tests."""

import functools
import logging
import os
import sys
from pathlib import Path
from typing import Generator

import pytest
import yaml
from click.testing import Result

# Load environment variables from .env file if it exists
_env_file = Path(__file__).parent / ".env"
if _env_file.exists():
    from dotenv import load_dotenv

    load_dotenv(_env_file)
elif not os.getenv("TEST_BOT_TOKEN"):
    # Provide default fake token for testing if .env doesn't exist
    os.environ.setdefault(
        "TEST_BOT_TOKEN",
        "1234567890:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA_",  # Fake token for testing
    )

# Configure logging for integration tests
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
    force=True,  # Override any existing config
)

# Set specific loggers to DEBUG for more details
logging.getLogger("tests.integration.fixtures.mock_vps").setLevel(logging.DEBUG)

# Reduce logging to avoid spam from keepalive requests and config loading
logging.getLogger("paramiko").setLevel(logging.WARNING)
logging.getLogger("paramiko.transport").setLevel(logging.WARNING)
logging.getLogger("invoke").setLevel(logging.WARNING)
logging.getLogger("fabric").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Helper functions for CLI testing
def get_cli_output(result: Result, runner=None) -> str:
    """Safely extract output from CliRunner result.

    This function handles the case where CliRunner closes file descriptors
    after invoke(), making result.output inaccessible.

    Args:
        result: CliRunner result object
        runner: Optional CliRunner instance (for charset detection)

    Returns:
        Decoded output string, empty string if extraction fails
    """
    try:
        return result.output
    except (ValueError, OSError):
        # Fallback: try to read from stdout_bytes directly
        charset = "utf-8"
        if runner and hasattr(runner, "charset"):
            charset = runner.charset

        stdout_bytes = getattr(result, "stdout_bytes", None)
        if stdout_bytes:
            try:
                return stdout_bytes.decode(charset, "replace").replace("\r\n", "\n")
            except (ValueError, AttributeError, OSError):
                pass

    return ""


def assert_cli_success(
    result: Result, runner=None, expected_output: str = None
) -> None:
    """Assert CLI command succeeded.

    Args:
        result: CliRunner result object
        runner: Optional CliRunner instance
        expected_output: Optional string that should be in output

    Raises:
        AssertionError: If command failed or expected output not found
    """
    output = get_cli_output(result, runner)
    assert (
        result.exit_code == 0
    ), f"Command failed with exit code {result.exit_code}: {output}"

    if expected_output:
        assert (
            expected_output.lower() in output.lower()
        ), f"Expected output '{expected_output}' not found in: {output[:200]}"


def assert_cli_error(result: Result, runner=None, error_message: str = None) -> None:
    """Assert CLI command failed.

    Args:
        result: CliRunner result object
        runner: Optional CliRunner instance
        error_message: Optional string that should be in error output

    Raises:
        AssertionError: If command succeeded or error message not found
    """
    output = get_cli_output(result, runner)
    assert (
        result.exit_code != 0
    ), f"Command should have failed but succeeded: {output[:200]}"

    if error_message:
        assert (
            error_message.lower() in output.lower()
        ), f"Expected error message '{error_message}' not found in: {output[:200]}"


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
            "name": "test-bot",  # Keep as literal for fixture, tests use TEST_BOT_NAME constant
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
