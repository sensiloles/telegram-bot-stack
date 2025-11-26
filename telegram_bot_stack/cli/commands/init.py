"""Initialize a new bot project with full dev environment."""

import subprocess
import sys
from pathlib import Path
from typing import Optional

import click

from telegram_bot_stack.cli.utils import dependencies, venv
from telegram_bot_stack.cli.utils.ide import (
    create_pycharm_settings,
    create_vscode_settings,
)
from telegram_bot_stack.cli.utils.linting import (
    create_precommit_config,
    install_precommit_hooks,
)
from telegram_bot_stack.cli.utils.makefile import create_makefile
from telegram_bot_stack.cli.utils.testing import create_test_structure


@click.command()
@click.argument("name")
@click.option(
    "--package-manager",
    type=click.Choice(["pip", "poetry", "pdm"]),
    default="pip",
    help="Package manager to use (default: pip)",
)
@click.option(
    "--python-version",
    default=None,
    help="Python version (e.g., 3.11). Defaults to current Python.",
)
@click.option(
    "--with-linting/--no-linting",
    default=True,
    help="Setup linting (ruff, mypy, pre-commit)",
)
@click.option(
    "--with-testing/--no-testing",
    default=True,
    help="Setup testing (pytest, fixtures)",
)
@click.option(
    "--ide",
    type=click.Choice(["vscode", "pycharm", "none"]),
    default="vscode",
    help="IDE to configure (default: vscode)",
)
@click.option(
    "--git/--no-git",
    default=True,
    help="Initialize Git repository",
)
@click.option(
    "--install-deps/--no-install-deps",
    default=True,
    help="Install dependencies after setup",
)
def init(
    name: str,
    package_manager: str,
    python_version: Optional[str],
    with_linting: bool,
    with_testing: bool,
    ide: str,
    git: bool,
    install_deps: bool,
) -> None:
    """Initialize a new bot project with full development environment.

    Creates a complete bot project with:
    - Virtual environment
    - Dependencies (telegram-bot-stack)
    - Linting (ruff, mypy, pre-commit)
    - Testing (pytest)
    - IDE configuration (VS Code/PyCharm)
    - Git initialization

    Example:

        telegram-bot-stack init my-awesome-bot

        telegram-bot-stack init my-bot --with-linting --ide vscode --git
    """
    project_path = Path.cwd() / name

    # Check if project already exists
    if project_path.exists():
        click.secho(f"❌ Error: Directory '{name}' already exists", fg="red")
        sys.exit(1)

    click.secho(f"\n🚀 Creating bot project: {name}\n", fg="cyan", bold=True)

    try:
        # 1. Create project directory
        project_path.mkdir(parents=True)
        click.secho(f"✅ Created project directory: {project_path}", fg="green")

        # 2. Create basic project structure
        _create_project_structure(project_path, name)

        # 3. Create virtual environment
        click.echo("\n📦 Setting up virtual environment...")
        venv_path = venv.create_virtualenv(project_path, python_version)

        # 4. Create dependency files (always use pyproject.toml - PEP 621)
        click.echo("\n📝 Creating dependency configuration...")
        py_version = (
            python_version or f"{sys.version_info.major}.{sys.version_info.minor}"
        )

        # Always create pyproject.toml (modern standard, works with pip, poetry, pdm)
        dependencies.create_pyproject_toml(
            project_path, name, py_version, with_linting, with_testing
        )

        # 5. Install dependencies
        if install_deps:
            click.echo("\n📦 Installing dependencies...")
            click.echo("  (This may take a minute...)")
            try:
                from telegram_bot_stack.cli.utils.venv import get_venv_pip

                pip = get_venv_pip(venv_path)

                # Install project in editable mode with dependencies
                if package_manager == "pip":
                    # Use pip to install from pyproject.toml
                    cmd = [str(pip), "install", "-e", ".", "--quiet"]
                    if with_linting or with_testing:
                        cmd.append(".[dev]")

                    subprocess.run(
                        cmd, cwd=project_path, check=True, capture_output=True
                    )
                    click.secho(
                        "  ✅ Installed dependencies from pyproject.toml", fg="green"
                    )
                elif package_manager == "poetry":
                    # Use poetry
                    subprocess.run(
                        ["poetry", "install"],
                        cwd=project_path,
                        check=True,
                        capture_output=True,
                    )
                    click.secho("  ✅ Installed dependencies with Poetry", fg="green")
                elif package_manager == "pdm":
                    # Use pdm
                    subprocess.run(
                        ["pdm", "install"],
                        cwd=project_path,
                        check=True,
                        capture_output=True,
                    )
                    click.secho("  ✅ Installed dependencies with PDM", fg="green")

            except (
                RuntimeError,
                subprocess.CalledProcessError,
                FileNotFoundError,
            ) as e:
                click.secho(f"  ⚠️  Warning: {e}", fg="yellow")
                click.echo("  You can install dependencies later with:")
                click.echo(f"    cd {name}")
                click.echo(f"    {venv.get_activation_command(venv_path)}")
                if package_manager == "pip":
                    click.echo("    pip install -e .[dev]")
                elif package_manager == "poetry":
                    click.echo("    poetry install")
                elif package_manager == "pdm":
                    click.echo("    pdm install")

        # 6. Create Makefile
        click.echo("\n📋 Creating development configuration...")
        create_makefile(project_path)
        # Note: pyproject.toml already created in step 4 with all tool configs

        # 7. Setup linting
        if with_linting:
            click.echo("\n🔍 Setting up linting...")

            create_precommit_config(project_path)

            if install_deps:
                try:
                    install_precommit_hooks(project_path, venv_path)
                except RuntimeError as e:
                    click.secho(f"  ⚠️  Warning: {e}", fg="yellow")
                    click.echo("  You can install hooks later with:")
                    click.echo("    pre-commit install")

        # 7. Setup testing
        if with_testing:
            click.echo("\n🧪 Setting up testing...")
            create_test_structure(project_path, name)

        # 8. Setup IDE
        if ide == "vscode":
            click.echo("\n💻 Configuring VS Code...")
            py_version = (
                python_version or f"{sys.version_info.major}.{sys.version_info.minor}"
            )
            create_vscode_settings(project_path, py_version)
        elif ide == "pycharm":
            click.echo("\n💻 Configuring PyCharm...")
            create_pycharm_settings(project_path)

        # 10. Setup Git
        if git:
            click.echo("\n📚 Initializing Git...")
            from telegram_bot_stack.cli.utils import git as git_utils

            git_utils.create_gitignore(project_path)
            git_utils.init_git(project_path, initial_commit=True)

        # 11. Success message
        _print_success_message(name, venv_path, with_linting, with_testing)

    except Exception as e:
        click.secho(f"\n❌ Error during project initialization: {e}", fg="red")
        click.echo("\nCleaning up...")
        import shutil

        if project_path.exists():
            shutil.rmtree(project_path)
        sys.exit(1)


def _create_project_structure(project_path: Path, bot_name: str) -> None:
    """Create basic project structure with bot.py and README.

    Args:
        project_path: Path to the project directory
        bot_name: Name of the bot
    """
    # Create bot.py
    bot_content = '''"""Main bot implementation."""

import asyncio
import logging
import os

from telegram_bot_stack import BotBase, MemoryStorage

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class Bot(BotBase):
    """Main bot class."""

    def get_welcome_message(self) -> str:
        """Return welcome message for new users."""
        return (
            "👋 Welcome! I'm a bot built with telegram-bot-stack.\\n\\n"
            "Available commands:\\n"
            "/start - Show this message\\n"
            "/help - Get help"
        )


def main() -> None:
    """Run the bot."""
    # Get bot token from environment
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN environment variable not set!")
        logger.info("Please create a .env file with your bot token:")
        logger.info("  echo 'BOT_TOKEN=your_token_here' > .env")
        return

    # Initialize bot with storage
    storage = MemoryStorage()
    bot = Bot(storage=storage)

    # Run bot
    logger.info("Starting bot...")
    asyncio.run(bot.run())


if __name__ == "__main__":
    main()
'''

    (project_path / "bot.py").write_text(bot_content)

    # Create .env.example
    env_example = """# Telegram Bot Token (get from @BotFather)
BOT_TOKEN=your_bot_token_here

# Optional: Admin user IDs (comma-separated)
# ADMIN_IDS=123456789,987654321
"""

    (project_path / ".env.example").write_text(env_example)

    # Create README.md
    readme = f"""# {bot_name}

A Telegram bot built with [telegram-bot-stack](https://github.com/sensiloles/telegram-bot-stack).

## Quick Start

1. **Get your bot token** from [@BotFather](https://t.me/BotFather)

2. **Create `.env` file** with your token:
   ```bash
   echo "BOT_TOKEN=your_token_here" > .env
   ```

3. **Run the bot**:
   ```bash
   telegram-bot-stack dev
   ```

   Or manually:
   ```bash
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   python bot.py
   ```

## Development

### Using CLI Commands

The project includes convenient CLI commands:

```bash
# Run bot in development mode (auto-reload on code changes)
telegram-bot-stack dev

# Validate project configuration
telegram-bot-stack validate

# Run tests
make test

# Format code
make format

# Lint code
make lint

# Type checking
make type-check

# Run all CI checks
make ci
```

### Using Makefile

The project includes a Makefile with common development commands:

```bash
make help        # Show all available commands
make test        # Run tests
make test-cov    # Run tests with coverage
make lint        # Run linter
make lint-fix    # Run linter and auto-fix issues
make format      # Format code
make format-check # Check code formatting
make type-check  # Type checking
make dev         # Run bot in development mode
make validate    # Validate project configuration
make install     # Install dependencies
make clean       # Clean cache files
make ci          # Run all CI checks (lint, type-check, test)
```

### Manual Commands

If you prefer to run commands manually:

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Run tests
pytest

# Format code
ruff format .

# Lint code
ruff check .

# Type checking
mypy .
```

## Project Structure

```
{bot_name}/
├── bot.py              # Main bot implementation
├── .env                # Environment variables (not in git)
├── .env.example        # Example environment variables
├── pyproject.toml      # Project config, dependencies, and tool settings
├── Makefile            # Development commands
├── tests/              # Test files
│   ├── conftest.py     # Pytest fixtures
│   └── test_bot.py     # Bot tests
└── README.md           # This file
```

## Documentation

- [telegram-bot-stack Documentation](https://github.com/sensiloles/telegram-bot-stack)
- [python-telegram-bot Documentation](https://docs.python-telegram-bot.org/)

## License

MIT
"""

    (project_path / "README.md").write_text(readme)

    click.secho(
        "  ✅ Created project files (bot.py, README.md, .env.example)", fg="green"
    )


def _print_success_message(
    name: str,
    venv_path: Path,
    with_linting: bool,
    with_testing: bool,
) -> None:
    """Print success message with next steps.

    Args:
        name: Project name
        venv_path: Path to virtual environment
        with_linting: Whether linting was configured
        with_testing: Whether testing was configured
    """
    activation_cmd = venv.get_activation_command(venv_path)

    click.secho("\n" + "=" * 70, fg="green")
    click.secho("🎉 Success! Your bot project is ready!", fg="green", bold=True)
    click.secho("=" * 70 + "\n", fg="green")

    click.echo("📋 Next steps:\n")
    click.secho(f"  1. cd {name}", fg="cyan")
    click.secho(f"  2. {activation_cmd}", fg="cyan")
    click.secho('  3. echo "BOT_TOKEN=your_token_here" > .env', fg="cyan")
    click.secho("  4. python bot.py", fg="cyan")

    click.echo("\n💡 Tips:\n")
    click.echo("  • Get your bot token from @BotFather")
    click.echo("  • Edit bot.py to customize your bot")
    click.echo("  • Use 'telegram-bot-stack dev' to run bot with auto-reload")
    click.echo("  • Use 'make help' to see all available commands")

    if with_testing:
        click.echo("  • Run tests: make test or pytest")

    if with_linting:
        click.echo("  • Format code: make format or ruff format .")
        click.echo("  • Lint code: make lint or ruff check .")

    click.echo("\n📚 Documentation:")
    click.echo("  https://github.com/sensiloles/telegram-bot-stack\n")
