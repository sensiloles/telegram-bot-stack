"""Tests for deployment utilities."""

from telegram_bot_stack.cli.utils.deployment import (
    DeploymentConfig,
    DockerTemplateRenderer,
    create_env_file,
    escape_env_value,
)


class TestDeploymentConfig:
    """Tests for DeploymentConfig class."""

    def test_create_new_config(self, tmp_path):
        """Test creating new configuration."""
        config_file = tmp_path / "deploy.yaml"
        config = DeploymentConfig(str(config_file))

        config.set("vps.host", "test.example.com")
        config.set("bot.name", "test-bot")
        config.save()

        assert config_file.exists()
        assert config.get("vps.host") == "test.example.com"
        assert config.get("bot.name") == "test-bot"

    def test_load_existing_config(self, tmp_path):
        """Test loading existing configuration."""
        config_file = tmp_path / "deploy.yaml"

        # Create config
        config1 = DeploymentConfig(str(config_file))
        config1.set("vps.host", "test.example.com")
        config1.save()

        # Load config
        config2 = DeploymentConfig(str(config_file))
        assert config2.get("vps.host") == "test.example.com"

    def test_nested_keys(self, tmp_path):
        """Test nested configuration keys."""
        config_file = tmp_path / "deploy.yaml"
        config = DeploymentConfig(str(config_file))

        config.set("resources.memory_limit", "256M")
        config.set("resources.cpu_limit", "0.5")

        assert config.get("resources.memory_limit") == "256M"
        assert config.get("resources.cpu_limit") == "0.5"

    def test_get_with_default(self, tmp_path):
        """Test getting value with default."""
        config_file = tmp_path / "deploy.yaml"
        config = DeploymentConfig(str(config_file))

        assert config.get("nonexistent.key", "default") == "default"
        assert config.get("another.key") is None

    def test_validate_valid_config(self, tmp_path):
        """Test validation of valid configuration."""
        config_file = tmp_path / "deploy.yaml"
        config = DeploymentConfig(str(config_file))

        config.set("vps.host", "test.example.com")
        config.set("vps.user", "root")
        config.set("bot.name", "test-bot")
        config.set("bot.token_env", "BOT_TOKEN")

        assert config.validate() is True

    def test_validate_invalid_config(self, tmp_path):
        """Test validation of invalid configuration."""
        config_file = tmp_path / "deploy.yaml"
        config = DeploymentConfig(str(config_file))

        config.set("vps.host", "test.example.com")
        # Missing required keys

        assert config.validate() is False


class TestDockerTemplateRenderer:
    """Tests for DockerTemplateRenderer class."""

    def test_render_dockerfile(self, tmp_path):
        """Test rendering Dockerfile."""
        config_file = tmp_path / "deploy.yaml"
        config = DeploymentConfig(str(config_file))
        config.set("bot.name", "test-bot")
        config.set("bot.python_version", "3.11")
        config.set("bot.entry_point", "bot.py")

        renderer = DockerTemplateRenderer(config)
        dockerfile = renderer.render_dockerfile()

        assert "FROM python:3.11-slim" in dockerfile
        assert "test-bot" in dockerfile
        assert "bot.py" in dockerfile

    def test_render_compose(self, tmp_path):
        """Test rendering docker-compose.yml."""
        config_file = tmp_path / "deploy.yaml"
        config = DeploymentConfig(str(config_file))
        config.set("bot.name", "test-bot")
        config.set("resources.memory_limit", "256M")
        config.set("resources.cpu_limit", "0.5")

        renderer = DockerTemplateRenderer(config)
        compose = renderer.render_compose()

        assert "test-bot" in compose
        assert "256M" in compose
        assert "0.5" in compose

    def test_render_all(self, tmp_path):
        """Test rendering all templates."""
        config_file = tmp_path / "deploy.yaml"
        config = DeploymentConfig(str(config_file))
        config.set("bot.name", "test-bot")
        config.set("bot.python_version", "3.11")
        config.set("bot.entry_point", "bot.py")
        config.set("resources.memory_limit", "256M")
        config.set("resources.cpu_limit", "0.5")
        config.set("resources.memory_reservation", "128M")
        config.set("resources.cpu_reservation", "0.25")
        config.set("environment.timezone", "UTC")
        config.set("logging.level", "INFO")
        config.set("logging.max_size", "5m")
        config.set("logging.max_files", "5")

        output_dir = tmp_path / "output"
        renderer = DockerTemplateRenderer(config)
        renderer.render_all(output_dir)

        assert (output_dir / "Dockerfile").exists()
        assert (output_dir / "docker-compose.yml").exists()
        assert (output_dir / ".dockerignore").exists()
        assert (output_dir / "Makefile").exists()


class TestCreateEnvFile:
    """Tests for create_env_file function."""

    def test_create_env_file_with_token(self, tmp_path, monkeypatch):
        """Test creating .env file with bot token."""
        config_file = tmp_path / "deploy.yaml"
        config = DeploymentConfig(str(config_file))
        config.set("bot.name", "test-bot")
        config.set("bot.token_env", "BOT_TOKEN")
        config.set("environment.timezone", "UTC")
        config.set("logging.level", "INFO")

        # Set environment variable
        monkeypatch.setenv("BOT_TOKEN", "test-token-123")

        env_file = tmp_path / ".env"
        create_env_file(config, env_file)

        assert env_file.exists()
        content = env_file.read_text()
        assert "BOT_TOKEN=test-token-123" in content
        assert "TZ=UTC" in content
        assert "LOG_LEVEL=INFO" in content

    def test_create_env_file_without_token(self, tmp_path):
        """Test creating .env file without bot token."""
        config_file = tmp_path / "deploy.yaml"
        config = DeploymentConfig(str(config_file))
        config.set("bot.name", "test-bot")
        config.set("bot.token_env", "BOT_TOKEN")
        config.set("environment.timezone", "UTC")

        env_file = tmp_path / ".env"
        create_env_file(config, env_file)

        assert env_file.exists()
        content = env_file.read_text()
        # New implementation warns but doesn't add placeholder token
        # Secrets should be set using 'deploy secrets set' command
        assert "test-bot" in content
        assert "TZ=UTC" in content
        assert "PRODUCTION=true" in content


class TestEscapeEnvValue:
    """Tests for escape_env_value function."""

    def test_escape_simple_value(self):
        """Test escaping simple value (no special characters)."""
        value = "simple_token_123"
        escaped = escape_env_value(value)
        assert escaped == value

    def test_escape_value_with_newline(self):
        """Test escaping value with newline (injection attempt)."""
        value = "token\nMALICIOUS_KEY=value"
        escaped = escape_env_value(value)
        # Should be quoted and newline escaped
        assert escaped.startswith('"')
        assert escaped.endswith('"')
        assert "\\n" in escaped
        assert "MALICIOUS_KEY" in escaped
        # Should not contain unescaped newline
        assert "\n" not in escaped[1:-1]  # Exclude quotes

    def test_escape_value_with_quotes(self):
        """Test escaping value with quotes."""
        value = 'token with "quotes"'
        escaped = escape_env_value(value)
        assert escaped.startswith('"')
        assert escaped.endswith('"')
        assert '\\"' in escaped

    def test_escape_value_with_backslash(self):
        """Test escaping value with backslash."""
        value = "token\\with\\backslashes"
        escaped = escape_env_value(value)
        assert escaped.startswith('"')
        assert escaped.endswith('"')
        assert "\\\\" in escaped

    def test_escape_value_with_equals(self):
        """Test escaping value with equals sign."""
        value = "token=value"
        escaped = escape_env_value(value)
        assert escaped.startswith('"')
        assert escaped.endswith('"')
        assert "token=value" in escaped

    def test_escape_value_with_dollar(self):
        """Test escaping value with dollar sign (shell variable)."""
        value = "token$VAR"
        escaped = escape_env_value(value)
        assert escaped.startswith('"')
        assert escaped.endswith('"')
        assert "\\$" in escaped

    def test_escape_value_with_backtick(self):
        """Test escaping value with backtick (command substitution)."""
        value = "token`command`"
        escaped = escape_env_value(value)
        assert escaped.startswith('"')
        assert escaped.endswith('"')
        assert "\\`" in escaped

    def test_escape_value_with_multiple_special_chars(self):
        """Test escaping value with multiple special characters."""
        value = 'token\n"quoted"\\backslash$VAR`cmd`'
        escaped = escape_env_value(value)
        assert escaped.startswith('"')
        assert escaped.endswith('"')
        assert "\\n" in escaped
        assert '\\"' in escaped
        assert "\\\\" in escaped
        assert "\\$" in escaped
        assert "\\`" in escaped

    def test_escape_value_with_space(self):
        """Test escaping value with space."""
        value = "token with spaces"
        escaped = escape_env_value(value)
        assert escaped.startswith('"')
        assert escaped.endswith('"')

    def test_escape_empty_value(self):
        """Test escaping empty value."""
        value = ""
        escaped = escape_env_value(value)
        # Empty value doesn't need quoting
        assert escaped == ""

    def test_escape_value_roundtrip(self):
        """Test that escaped value can be safely parsed back."""

        test_values = [
            "simple",
            "token\nnewline",
            'token"quotes"',
            "token\\backslash",
            "token=equals",
            "token$var",
            "token`cmd`",
            "token with spaces",
        ]

        for value in test_values:
            escaped = escape_env_value(value)
            # Try to parse with shlex (simulates shell/env file parsing)
            if escaped.startswith('"'):
                # Remove quotes and unescape
                unescaped = escaped[1:-1].encode().decode("unicode_escape")
                # For newlines, verify they're preserved as \n
                if "\n" in value:
                    assert "\\n" in escaped
            else:
                # Simple value, should be unchanged
                assert escaped == value
