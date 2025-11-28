"""Tests for deployment configuration."""

import os
from pathlib import Path

from telegram_bot_stack.cli.utils.deployment import DeploymentConfig

TEST_BOT_NAME = "test-bot"


class TestDeploymentConfig:
    """Test deployment configuration management."""

    def test_config_creation_and_save(self, tmp_path: Path) -> None:
        """Test deployment config can be created and saved."""
        os.chdir(tmp_path)

        config_file = tmp_path / "deploy.yaml"
        config = DeploymentConfig(str(config_file))

        # Set required fields
        config.set("vps.host", "test.example.com")
        config.set("vps.user", "root")
        config.set("bot.name", TEST_BOT_NAME)
        config.set("bot.token_env", "BOT_TOKEN")
        config.save()

        # Verify file exists
        assert config_file.exists()

        # Load and validate
        config2 = DeploymentConfig(str(config_file))
        assert config2.validate(), "Config should be valid"
        assert config2.get("vps.host") == "test.example.com"
        assert config2.get("bot.name") == TEST_BOT_NAME

    def test_config_nested_keys(self, tmp_path: Path) -> None:
        """Test nested configuration keys."""
        config_file = tmp_path / "deploy.yaml"
        config = DeploymentConfig(str(config_file))

        # Set nested values
        config.set("resources.memory_limit", "256M")
        config.set("resources.cpu_limit", "0.5")
        config.set("logging.level", "INFO")

        # Verify retrieval
        assert config.get("resources.memory_limit") == "256M"
        assert config.get("resources.cpu_limit") == "0.5"
        assert config.get("logging.level") == "INFO"

    def test_config_validation_missing_fields(self, tmp_path: Path) -> None:
        """Test config validation fails with missing required fields."""
        config_file = tmp_path / "deploy.yaml"
        config = DeploymentConfig(str(config_file))

        # Set only some required fields
        config.set("vps.host", "test.example.com")

        # Should fail validation
        assert not config.validate(), "Config with missing fields should not validate"
