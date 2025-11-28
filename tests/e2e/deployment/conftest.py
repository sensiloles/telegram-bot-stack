"""Pytest configuration for deployment E2E tests."""

import os
import re
from pathlib import Path
from typing import Generator

import pytest

from tests.integration.fixtures.mock_vps import MockVPS


@pytest.fixture
def test_bot_project(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a minimal test bot project.

    Creates a simple bot with all necessary files for deployment testing:
    - bot.py: Minimal bot script
    - requirements.txt: Dependencies
    - data/: Data directory for persistence

    Args:
        tmp_path: Pytest temporary directory

    Yields:
        Path to bot project directory
    """
    # Create bot.py
    bot_py = tmp_path / "bot.py"
    bot_py.write_text("""#!/usr/bin/env python3
\"\"\"Test bot for deployment E2E tests.\"\"\"

import logging
import os
import sys
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    \"\"\"Run test bot (just logs and stays alive).\"\"\"
    logger.info("Test bot started!")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")

    # Check for BOT_TOKEN
    token = os.getenv("BOT_TOKEN")
    if token:
        logger.info(f"BOT_TOKEN found: {token[:10]}...")
    else:
        logger.warning("BOT_TOKEN not found!")

    # Create/check data directory
    data_dir = Path("/app/data") if Path("/app").exists() else Path("data")
    data_dir.mkdir(exist_ok=True)
    logger.info(f"Data directory: {data_dir}")

    # Write a test file
    test_file = data_dir / "test.txt"
    test_file.write_text(f"Bot started at {time.time()}")
    logger.info(f"Created test file: {test_file}")

    # Keep running
    logger.info("Bot is running... (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(10)
            logger.info("Bot heartbeat - still alive")
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")


if __name__ == "__main__":
    main()
""")

    # Create requirements.txt
    requirements = tmp_path / "requirements.txt"
    requirements.write_text("""# Test bot requirements
# No telegram dependencies needed for E2E tests
python-telegram-bot>=22.3
cryptography>=42.0.0
""")

    # Create data directory
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # Create .gitkeep to ensure directory is tracked
    (data_dir / ".gitkeep").write_text("")

    # Change to tmp_path for deployment commands
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    yield tmp_path

    # Cleanup
    os.chdir(original_cwd)


@pytest.fixture
def deployed_bot(
    test_bot_project: Path,
    deployment_config: Path,
    clean_vps: MockVPS,
) -> Generator[dict, None, None]:
    """Deploy test bot to Mock VPS.

    This fixture handles the full deployment process and cleanup.
    Useful for testing update, rollback, and monitoring features.

    Args:
        test_bot_project: Test bot project fixture
        deployment_config: Deployment config fixture
        clean_vps: Clean VPS fixture

    Yields:
        Dictionary with deployment information:
        - vps: MockVPS instance
        - bot_name: Bot name
        - remote_dir: Remote deployment directory
        - config_path: Path to deploy.yaml
    """
    from telegram_bot_stack.cli.utils.deployment import DeploymentConfig

    # Load config to get bot name
    config = DeploymentConfig(str(deployment_config))
    bot_name = config.get("bot.name")
    remote_dir = f"/opt/{bot_name}"

    # Deploy bot using the up command
    # Note: We'll use VPSConnection directly for more control in tests
    from telegram_bot_stack.cli.utils.vps import VPSConnection

    vps = VPSConnection(
        host=clean_vps.host,
        user=clean_vps.user,
        ssh_key=clean_vps.ssh_key_path,
        port=clean_vps.port,
    )

    deployment_info = {
        "vps": vps,
        "bot_name": bot_name,
        "remote_dir": remote_dir,
        "config_path": deployment_config,
        "project_path": test_bot_project,
    }

    yield deployment_info

    # Cleanup: stop and remove bot
    try:
        # Stop bot container
        vps.run_command(
            f"cd {remote_dir} && docker compose down -v 2>/dev/null || true",
            hide=True,
        )
        # Remove deployment directory
        vps.run_command(f"rm -rf {remote_dir}", hide=True)
    finally:
        vps.close()


def convert_bind_mounts_to_volumes(compose_content: str, bot_name: str) -> str:
    """Convert bind mounts to named volumes for Docker-in-Docker compatibility.

    In E2E tests with Docker-in-Docker, bind mounts like ./data:/app/data don't work
    because the host Docker daemon can't access paths inside the Mock VPS container.
    This function converts them to named volumes which work correctly in DinD.

    Args:
        compose_content: Original docker-compose.yml content
        bot_name: Bot name for volume naming

    Returns:
        Modified docker-compose.yml content with named volumes

    Example:
        Input:  volumes:\n      - ./data:/app/data:rw
        Output: volumes:\n      - test-bot-data:/app/data:rw
                ...
                volumes:
                  test-bot-data:
                    driver: local
    """
    # Replace bind mounts with named volumes
    # Pattern: ./path:/container/path or ./path:/container/path:rw
    modified_content = compose_content

    # Track which volumes we need to create
    volumes_to_create = []

    # Replace ./data mount
    if "./data:/app/data" in modified_content:
        volume_name = f"{bot_name}-data"
        modified_content = re.sub(
            r"\./data:/app/data(:\w+)?",
            f"{volume_name}:/app/data\\1",
            modified_content,
        )
        volumes_to_create.append(volume_name)

    # Replace ./logs mount
    if "./logs:/app/logs" in modified_content:
        volume_name = f"{bot_name}-logs"
        modified_content = re.sub(
            r"\./logs:/app/logs(:\w+)?",
            f"{volume_name}:/app/logs\\1",
            modified_content,
        )
        volumes_to_create.append(volume_name)

    # Add volumes section if we have volumes to create
    if volumes_to_create:
        # Check if volumes section already exists
        if "\nvolumes:\n" in modified_content:
            # Append to existing volumes section
            volumes_section = "\nvolumes:\n"
            for vol_name in volumes_to_create:
                volumes_section += f"  {vol_name}:\n    driver: local\n"
            # Find the networks section and insert before it
            modified_content = modified_content.replace(
                "\nnetworks:\n", f"{volumes_section}\nnetworks:\n"
            )
        else:
            # Add new volumes section before networks
            volumes_section = "\nvolumes:\n"
            for vol_name in volumes_to_create:
                volumes_section += f"  {vol_name}:\n    driver: local\n"
            modified_content = modified_content.replace(
                "\nnetworks:\n", f"{volumes_section}\nnetworks:\n"
            )

    return modified_content
