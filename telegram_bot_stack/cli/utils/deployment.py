"""
Deployment configuration and template rendering utilities.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict

import yaml  # type: ignore[import-untyped]
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from rich.console import Console

console = Console()


def escape_env_value(value: str) -> str:
    """Escape a value for use in .env file format.

    Properly escapes newlines, quotes, backslashes, and other special characters
    to prevent injection attacks and format corruption.

    Args:
        value: The value to escape

    Returns:
        Properly escaped value safe for .env file format
    """
    # Check if value contains special characters that need escaping
    needs_quoting = any(
        char in value for char in ["\n", "\r", "\t", '"', "\\", " ", "#", "=", "$", "`"]
    )

    if not needs_quoting:
        # Simple value, no escaping needed
        return value

    # Escape backslashes first (must be done before escaping quotes)
    escaped = value.replace("\\", "\\\\")
    # Escape double quotes
    escaped = escaped.replace('"', '\\"')
    # Escape newlines
    escaped = escaped.replace("\n", "\\n")
    # Escape carriage returns
    escaped = escaped.replace("\r", "\\r")
    # Escape tabs
    escaped = escaped.replace("\t", "\\t")
    # Escape dollar signs (shell variable expansion)
    escaped = escaped.replace("$", "\\$")
    # Escape backticks (command substitution)
    escaped = escaped.replace("`", "\\`")

    # Wrap in double quotes
    return f'"{escaped}"'


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


def _find_templates_dir(template_type: str) -> Path:
    """Find templates directory using multiple fallback strategies.

    Args:
        template_type: Type of templates (e.g., 'docker', 'systemd')

    Returns:
        Path to templates directory

    Raises:
        FileNotFoundError: If templates directory not found
    """
    # Strategy 1: Relative to this file (development)
    base_dir = Path(__file__).parent.parent
    templates_dir = base_dir / "templates" / template_type
    if templates_dir.exists():
        return templates_dir

    # Strategy 2: Relative to package root (installed package)
    # Try to find telegram_bot_stack package location
    try:
        import telegram_bot_stack.cli.templates

        package_path = Path(telegram_bot_stack.cli.templates.__file__).parent
        templates_dir = package_path / template_type
        if templates_dir.exists():
            return templates_dir
    except (ImportError, AttributeError):
        pass

    # Strategy 3: Check common installation paths
    for path in sys.path:
        templates_dir = (
            Path(path) / "telegram_bot_stack" / "cli" / "templates" / template_type
        )
        if templates_dir.exists():
            return templates_dir

    raise FileNotFoundError(
        f"Templates directory not found for '{template_type}'. "
        f"Expected: {base_dir / 'templates' / template_type}"
    )


class DockerTemplateRenderer:
    """Renders Docker templates with configuration."""

    def __init__(self, config: DeploymentConfig, has_secrets: bool = False):
        """Initialize template renderer.

        Args:
            config: Deployment configuration
            has_secrets: Whether secrets are configured (affects docker-compose template)
        """
        self.config = config
        self.has_secrets = has_secrets

        # Get templates directory with fallback strategies
        try:
            templates_dir = _find_templates_dir("docker")
        except FileNotFoundError as e:
            console.print(f"[red]❌ {e}[/red]")
            raise

        if not templates_dir.exists():
            raise FileNotFoundError(
                f"Docker templates directory not found: {templates_dir}"
            )

        self.env = Environment(loader=FileSystemLoader(str(templates_dir)))

    def render_dockerfile(self) -> str:
        """Render Dockerfile from template.

        Returns:
            Rendered Dockerfile content

        Raises:
            TemplateNotFound: If template file not found
        """
        try:
            template = self.env.get_template("Dockerfile.template")
        except TemplateNotFound:
            raise FileNotFoundError(
                "Dockerfile.template not found. "
                "Please ensure templates are installed correctly."
            )

        return template.render(
            bot_name=self.config.get("bot.name", "telegram-bot"),
            python_version=self.config.get("bot.python_version", "3.11"),
            bot_entry_point=self.config.get("bot.entry_point", "bot.py"),
        )

    def render_compose(self) -> str:
        """Render docker-compose.yml from template.

        Returns:
            Rendered docker-compose.yml content

        Raises:
            TemplateNotFound: If template file not found
        """
        try:
            template = self.env.get_template("docker-compose.yml.template")
        except TemplateNotFound:
            raise FileNotFoundError(
                "docker-compose.yml.template not found. "
                "Please ensure templates are installed correctly."
            )

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
            has_secrets=self.has_secrets,
        )

    def render_dockerignore(self) -> str:
        """Render .dockerignore from template.

        Returns:
            Rendered .dockerignore content

        Raises:
            TemplateNotFound: If template file not found
        """
        try:
            template = self.env.get_template(".dockerignore.template")
        except TemplateNotFound:
            raise FileNotFoundError(
                ".dockerignore.template not found. "
                "Please ensure templates are installed correctly."
            )
        return template.render()

    def render_makefile(self) -> str:
        """Render Makefile from template.

        Returns:
            Rendered Makefile content

        Raises:
            TemplateNotFound: If template file not found
        """
        try:
            template = self.env.get_template("Makefile.template")
        except TemplateNotFound:
            raise FileNotFoundError(
                "Makefile.template not found. "
                "Please ensure templates are installed correctly."
            )

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


class SystemdTemplateRenderer:
    """Renders systemd templates with configuration."""

    def __init__(self, config: DeploymentConfig, has_secrets: bool = False):
        """Initialize template renderer.

        Args:
            config: Deployment configuration
            has_secrets: Whether secrets are configured
        """
        self.config = config
        self.has_secrets = has_secrets

        # Get templates directory with fallback strategies
        try:
            templates_dir = _find_templates_dir("systemd")
        except FileNotFoundError:
            # If systemd templates don't exist, create them inline
            templates_dir = None
        self.templates_dir = templates_dir

    def render_service_file(self) -> str:
        """Render systemd service file.

        Returns:
            Rendered systemd service file content
        """
        bot_name = self.config.get("bot.name", "telegram-bot")
        bot_entry_point = self.config.get("bot.entry_point", "bot.py")
        remote_dir = f"/opt/{bot_name}"
        python_version = self.config.get("bot.python_version", "3.11")
        user = self.config.get("vps.user", "root")
        timezone = self.config.get("environment.timezone", "UTC")
        log_level = self.config.get("logging.level", "INFO")

        # Generate service file content
        service_content = f"""[Unit]
Description=Telegram Bot: {bot_name}
After=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={remote_dir}
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="TZ={timezone}"
Environment="LOG_LEVEL={log_level}"
Environment="PRODUCTION=true"
ExecStart=/usr/bin/python{python_version} {remote_dir}/{bot_entry_point}
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier={bot_name}

# Resource limits
MemoryLimit={self.config.get("resources.memory_limit", "256M")}
CPUQuota={self.config.get("resources.cpu_limit", "50")}%

[Install]
WantedBy=multi-user.target
"""

        return service_content

    def render_all(self, output_dir: Path) -> None:
        """Render all templates to output directory.

        Args:
            output_dir: Directory to write rendered templates
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Render and write systemd service file
        bot_name = self.config.get("bot.name", "telegram-bot")
        service_file = output_dir / f"{bot_name}.service"
        service_file.write_text(self.render_service_file())
        console.print(f"[green]✓ Generated {service_file}[/green]")


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
            escaped_token = escape_env_value(bot_token)
            env_content += f"{bot_token_env}={escaped_token}\n"
        else:
            console.print(
                f"[yellow]⚠️  Warning: {bot_token_env} not found. Use 'deploy secrets set' to store it securely.[/yellow]"
            )

    # Add custom environment variables
    env_config = config.get("environment", {})
    for key, value in env_config.items():
        if key not in ["timezone"]:  # Skip already added keys
            escaped_value = escape_env_value(str(value))
            env_content += f"{key}={escaped_value}\n"

    output_path.write_text(env_content)
    console.print(f"[green]✓ Generated {output_path}[/green]")
