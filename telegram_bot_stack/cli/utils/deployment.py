"""
Deployment configuration and template rendering utilities.
"""

import os
from pathlib import Path
from typing import Any, Dict

import yaml  # type: ignore[import-untyped]
from jinja2 import Environment, FileSystemLoader
from rich.console import Console

console = Console()


class DeploymentConfig:
    """Manages deployment configuration."""

    def __init__(self, config_path: str = "deploy.yaml"):
        """Initialize deployment configuration.

        Args:
            config_path: Path to deployment config file
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}

        if self.config_path.exists():
            self.load()

    def load(self) -> None:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path) as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            console.print(f"[red]Failed to load config: {e}[/red]")
            raise

    def save(self) -> None:
        """Save configuration to YAML file."""
        try:
            with open(self.config_path, "w") as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            console.print(f"[green]✓ Configuration saved to {self.config_path}[/green]")
        except Exception as e:
            console.print(f"[red]Failed to save config: {e}[/red]")
            raise

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.

        Args:
            key: Configuration key (supports nested keys with dots)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value: Any = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key.

        Args:
            key: Configuration key (supports nested keys with dots)
            value: Value to set
        """
        keys = key.split(".")
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def validate(self) -> bool:
        """Validate configuration.

        Returns:
            True if configuration is valid, False otherwise
        """
        required_keys = [
            "vps.host",
            "vps.user",
            "bot.name",
            "bot.token_env",
        ]

        for key in required_keys:
            if self.get(key) is None:
                console.print(f"[red]Missing required configuration: {key}[/red]")
                return False

        return True


class DockerTemplateRenderer:
    """Renders Docker templates with configuration."""

    def __init__(self, config: DeploymentConfig):
        """Initialize template renderer.

        Args:
            config: Deployment configuration
        """
        self.config = config

        # Get templates directory
        templates_dir = Path(__file__).parent.parent / "templates" / "docker"
        self.env = Environment(loader=FileSystemLoader(str(templates_dir)))

    def render_dockerfile(self) -> str:
        """Render Dockerfile from template.

        Returns:
            Rendered Dockerfile content
        """
        template = self.env.get_template("Dockerfile.template")

        return template.render(
            bot_name=self.config.get("bot.name", "telegram-bot"),
            python_version=self.config.get("bot.python_version", "3.11"),
            bot_entry_point=self.config.get("bot.entry_point", "bot.py"),
        )

    def render_compose(self) -> str:
        """Render docker-compose.yml from template.

        Returns:
            Rendered docker-compose.yml content
        """
        template = self.env.get_template("docker-compose.yml.template")

        return template.render(
            bot_name=self.config.get("bot.name", "telegram-bot"),
            memory_limit=self.config.get("resources.memory_limit", "256M"),
            memory_reservation=self.config.get("resources.memory_reservation", "128M"),
            cpu_limit=self.config.get("resources.cpu_limit", "0.5"),
            cpu_reservation=self.config.get("resources.cpu_reservation", "0.25"),
            timezone=self.config.get("environment.timezone", "UTC"),
            log_level=self.config.get("logging.level", "INFO"),
            log_max_size=self.config.get("logging.max_size", "5m"),
            log_max_files=self.config.get("logging.max_files", "5"),
        )

    def render_dockerignore(self) -> str:
        """Render .dockerignore from template.

        Returns:
            Rendered .dockerignore content
        """
        template = self.env.get_template(".dockerignore.template")
        return template.render()

    def render_makefile(self) -> str:
        """Render Makefile from template.

        Returns:
            Rendered Makefile content
        """
        template = self.env.get_template("Makefile.template")

        return template.render(
            bot_name=self.config.get("bot.name", "telegram-bot"),
        )

    def render_all(self, output_dir: Path) -> None:
        """Render all templates to output directory.

        Args:
            output_dir: Directory to write rendered templates
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Render and write Dockerfile
        dockerfile = output_dir / "Dockerfile"
        dockerfile.write_text(self.render_dockerfile())
        console.print(f"[green]✓ Generated {dockerfile}[/green]")

        # Render and write docker-compose.yml
        compose = output_dir / "docker-compose.yml"
        compose.write_text(self.render_compose())
        console.print(f"[green]✓ Generated {compose}[/green]")

        # Render and write .dockerignore
        dockerignore = output_dir / ".dockerignore"
        dockerignore.write_text(self.render_dockerignore())
        console.print(f"[green]✓ Generated {dockerignore}[/green]")

        # Render and write Makefile
        makefile = output_dir / "Makefile"
        makefile.write_text(self.render_makefile())
        console.print(f"[green]✓ Generated {makefile}[/green]")


def create_env_file(
    config: DeploymentConfig,
    output_path: Path,
    secrets_manager: Any = None,
    vps_connection: Any = None,
) -> None:
    """Create .env file for deployment.

    Args:
        config: Deployment configuration
        output_path: Path to write .env file
        secrets_manager: Optional SecretsManager instance to load secrets
        vps_connection: Optional VPSConnection instance (required if secrets_manager provided)
    """
    env_content = f"""# Environment variables for {config.get("bot.name")}
# Generated by telegram-bot-stack
# Note: Sensitive secrets are loaded from .secrets.env on VPS

# Additional environment variables
TZ={config.get("environment.timezone", "UTC")}
LOG_LEVEL={config.get("logging.level", "INFO")}
PRODUCTION=true
"""

    # Try to load secrets from VPS if secrets_manager is provided
    if secrets_manager and vps_connection:
        try:
            decrypted_secrets = secrets_manager.load_secrets_to_env(vps_connection)
            if decrypted_secrets:
                # Add secrets as comments (actual values loaded from .secrets.env)
                env_content += "\n# Secrets loaded from .secrets.env on VPS:\n"
                for key in sorted(decrypted_secrets.keys()):
                    env_content += f"# {key}=***\n"
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load secrets: {e}[/yellow]")
    else:
        # Fallback: try to get from environment (for backward compatibility)
        bot_token_env = config.get("bot.token_env", "BOT_TOKEN")
        bot_token = os.getenv(bot_token_env)

        if bot_token:
            env_content += (
                "\n# Legacy: token from environment (consider using secrets)\n"
            )
            env_content += f"{bot_token_env}={bot_token}\n"
        else:
            console.print(
                f"[yellow]⚠️  Warning: {bot_token_env} not found. Use 'deploy secrets set' to store it securely.[/yellow]"
            )

    # Add custom environment variables
    env_config = config.get("environment", {})
    for key, value in env_config.items():
        if key not in ["timezone"]:  # Skip already added keys
            env_content += f"{key}={value}\n"

    output_path.write_text(env_content)
    console.print(f"[green]✓ Generated {output_path}[/green]")
