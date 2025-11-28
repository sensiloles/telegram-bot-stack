"""Pytest configuration for deployment integration tests."""

import os
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
\"\"\"Test bot for deployment integration tests.\"\"\"

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
# No telegram dependencies needed for integration tests
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
