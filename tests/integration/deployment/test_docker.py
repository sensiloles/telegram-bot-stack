"""Tests for Docker file generation."""

from pathlib import Path

import yaml

from telegram_bot_stack.cli.utils.deployment import (
    DeploymentConfig,
    DockerTemplateRenderer,
)

TEST_BOT_NAME = "test-bot"


class TestDockerfileGeneration:
    """Test Dockerfile template rendering."""

    def test_dockerfile_basic_generation(self, tmp_path: Path) -> None:
        """Test Dockerfile can be generated with basic config."""
        config = DeploymentConfig()
        config.set("bot.name", TEST_BOT_NAME)
        config.set("bot.python_version", "3.11")
        config.set("bot.entry_point", "bot.py")

        renderer = DockerTemplateRenderer(config, has_secrets=False)
        dockerfile_content = renderer.render_dockerfile()

        # Verify essential content
        assert "FROM python:3.11" in dockerfile_content
        assert "bot.py" in dockerfile_content
        assert "WORKDIR /app" in dockerfile_content
        assert "USER botuser" in dockerfile_content  # Security: non-root user

    def test_dockerfile_different_python_versions(self, tmp_path: Path) -> None:
        """Test Dockerfile with different Python versions."""
        for version in ["3.9", "3.10", "3.11", "3.12"]:
            config = DeploymentConfig()
            config.set("bot.python_version", version)
            config.set("bot.entry_point", "bot.py")

            renderer = DockerTemplateRenderer(config, has_secrets=False)
            content = renderer.render_dockerfile()

            assert f"FROM python:{version}" in content


class TestDockerComposeGeneration:
    """Test docker-compose.yml template rendering."""

    def test_compose_basic_generation(self, tmp_path: Path) -> None:
        """Test docker-compose.yml can be generated."""
        config = DeploymentConfig()
        config.set("bot.name", TEST_BOT_NAME)
        config.set("resources.memory_limit", "256M")
        config.set("resources.cpu_limit", "0.5")
        config.set("resources.memory_reservation", "128M")
        config.set("resources.cpu_reservation", "0.25")
        config.set("environment.timezone", "UTC")
        config.set("logging.level", "INFO")
        config.set("logging.max_size", "5m")
        config.set("logging.max_files", "5")

        renderer = DockerTemplateRenderer(config, has_secrets=False)
        compose_content = renderer.render_compose()

        # Parse YAML
        compose_data = yaml.safe_load(compose_content)

        # Verify structure
        assert "services" in compose_data
        assert "bot" in compose_data["services"]
        assert compose_data["services"]["bot"]["container_name"] == TEST_BOT_NAME
        assert compose_data["services"]["bot"]["restart"] == "always"

    def test_compose_resource_limits(self, tmp_path: Path) -> None:
        """Test docker-compose includes resource limits."""
        config = DeploymentConfig()
        config.set("bot.name", TEST_BOT_NAME)
        config.set("resources.memory_limit", "512M")
        config.set("resources.cpu_limit", "1.0")
        config.set("resources.memory_reservation", "256M")
        config.set("resources.cpu_reservation", "0.5")
        config.set("environment.timezone", "UTC")
        config.set("logging.level", "INFO")
        config.set("logging.max_size", "10m")
        config.set("logging.max_files", "3")

        renderer = DockerTemplateRenderer(config, has_secrets=False)
        compose_content = renderer.render_compose()

        compose_data = yaml.safe_load(compose_content)

        # Verify resource limits
        bot_service = compose_data["services"]["bot"]
        assert "deploy" in bot_service
        assert "resources" in bot_service["deploy"]
        assert bot_service["deploy"]["resources"]["limits"]["memory"] == "512M"
        assert bot_service["deploy"]["resources"]["limits"]["cpus"] == "1.0"


class TestMakefileGeneration:
    """Test Makefile template rendering."""

    def test_makefile_generation(self, tmp_path: Path) -> None:
        """Test Makefile can be generated."""
        config = DeploymentConfig()
        config.set("bot.name", TEST_BOT_NAME)

        renderer = DockerTemplateRenderer(config, has_secrets=False)
        makefile_content = renderer.render_makefile()

        # Verify essential targets
        assert "build" in makefile_content
        assert "up" in makefile_content
        assert "down" in makefile_content
        assert "logs" in makefile_content
        assert "status" in makefile_content
        assert TEST_BOT_NAME in makefile_content

    def test_makefile_docker_compose_detection(self, tmp_path: Path) -> None:
        """Test Makefile includes docker compose version detection."""
        config = DeploymentConfig()
        config.set("bot.name", TEST_BOT_NAME)

        renderer = DockerTemplateRenderer(config, has_secrets=False)
        makefile_content = renderer.render_makefile()

        # Should detect both v1 and v2
        assert (
            "docker compose" in makefile_content or "DOCKER_COMPOSE" in makefile_content
        )
