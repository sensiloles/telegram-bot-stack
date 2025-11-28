"""Pytest configuration for integration tests."""

import os
from pathlib import Path
from typing import Generator

import pytest
import yaml

# Import fixtures to make them available
from tests.integration.fixtures.mock_vps import (  # noqa: F401
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
