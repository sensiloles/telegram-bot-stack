"""Initialize a new bot project with full dev environment."""

import subprocess
import sys
from pathlib import Path
from typing import Callable, Optional

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

# Constants
PROJECT_NAME = "telegram-bot-stack"
DEV_EXTRA = "[dev]"


def _find_stack_repo() -> Optional[Path]:
    """Find telegram-bot-stack repository path.

    Checks current file location and parent directories to find
    the telegram-bot-stack repository by looking for pyproject.toml
    with matching project name.

    Returns:
        Path to stack repository if found, None otherwise
    """
    current = Path(__file__).resolve()
    # Check current directory and parents up to 5 levels
    for path in [current.parent] + list(current.parents[:5]):
        pyproject = path / "pyproject.toml"
        if pyproject.exists():
            try:
                # Try to read and verify it's the right project
                content = pyproject.read_text()
                if PROJECT_NAME in content and "[project]" in content:
                    return path
            except Exception:
                continue
    return None


def _validate_project_path(name: str) -> Path:
    """Validate and prepare project path.

    Args:
        name: Project name

    Returns:
        Path to project directory

    Raises:
        SystemExit: If path already exists or is invalid
    """
    project_path = Path.cwd() / name

    if project_path.exists():
        if project_path.is_file():
            click.secho(f"❌ Error: '{name}' is a file, not a directory", fg="red")
        else:
            click.secho(f"❌ Error: Directory '{name}' already exists", fg="red")
        sys.exit(1)

    return project_path


def _install_from_local_repo(
    pip_path: Path, stack_repo: Path, run_subprocess: Callable = subprocess.run
) -> bool:
    """Try to install telegram-bot-stack from local repository.

    Args:
        pip_path: Path to pip executable
        stack_repo: Path to telegram-bot-stack repository
        run_subprocess: Function to run subprocess (for testing)

    Returns:
        True if installation succeeded, False otherwise
    """
    try:
        result = run_subprocess(
            [str(pip_path), "install", "-e", str(stack_repo), "--quiet"],
            check=True,
            capture_output=True,
        )
        click.secho(
            "  ✅ Installed telegram-bot-stack from local repo",
            fg="green",
        )
        return True
    except (subprocess.CalledProcessError, Exception) as e:
        # Log debug info but don't fail - will try PyPI
        if hasattr(e, "stderr") and e.stderr:
            # Only show if there's actual error info
            pass
        return False


def _install_with_pip(
    project_path: Path,
    venv_path: Path,
    name: str,
    with_linting: bool,
    with_testing: bool,
    run_subprocess: Callable = subprocess.run,
) -> bool:
    """Install dependencies using pip.

    Args:
        project_path: Path to project directory
        venv_path: Path to virtual environment
        name: Project name
        with_linting: Whether linting dependencies are needed
        with_testing: Whether testing dependencies are needed
        run_subprocess: Function to run subprocess (for testing)

    Returns:
        True if installation succeeded, False otherwise
    """
    from telegram_bot_stack.cli.utils.venv import get_venv_pip

    pip = get_venv_pip(venv_path)

    # Try to install from local repo first
    stack_repo = _find_stack_repo()
    if stack_repo:
        _install_from_local_repo(pip, stack_repo, run_subprocess)

    # Install project in editable mode
    install_target = "."
    if with_linting or with_testing:
        install_target = f".{DEV_EXTRA}"
    cmd = [str(pip), "install", "-e", install_target, "--quiet"]

    result = run_subprocess(
        cmd,
        cwd=project_path,
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        # Check if error is about telegram-bot-stack not found
        if PROJECT_NAME in result.stderr or "No matching distribution" in result.stderr:
            click.secho(
                "  ⚠️  Warning: Could not install telegram-bot-stack from PyPI",
                fg="yellow",
            )
            click.echo("  This usually means:")
            click.echo("    • Package is not published to PyPI yet")
            click.echo("    • You need to install it manually from source")
            click.echo("\n  To fix this, run:")
            click.echo(f"    cd {name}")
            click.echo(f"    {venv.get_activation_command(venv_path)}")
            click.echo(f"    pip install {PROJECT_NAME}")
            click.echo("    # Or if you have the source:")
            click.echo(f"    pip install -e /path/to/{PROJECT_NAME}")
            click.echo(f"    pip install -e '{DEV_EXTRA}'")
        else:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stderr)
        return False

    click.secho(
        "  ✅ Installed dependencies from pyproject.toml",
        fg="green",
    )
    return True


def _install_with_poetry(
    project_path: Path, run_subprocess: Callable = subprocess.run
) -> bool:
    """Install dependencies using poetry.

    Args:
        project_path: Path to project directory
        run_subprocess: Function to run subprocess (for testing)

    Returns:
        True if installation succeeded, False otherwise
    """
    try:
        run_subprocess(
            ["poetry", "install"],
            cwd=project_path,
            check=True,
            capture_output=True,
        )
        click.secho("  ✅ Installed dependencies with Poetry", fg="green")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _install_with_pdm(
    project_path: Path, run_subprocess: Callable = subprocess.run
) -> bool:
    """Install dependencies using pdm.

    Args:
        project_path: Path to project directory
        run_subprocess: Function to run subprocess (for testing)

    Returns:
        True if installation succeeded, False otherwise
    """
    try:
        run_subprocess(
            ["pdm", "install"],
            cwd=project_path,
            check=True,
            capture_output=True,
        )
        click.secho("  ✅ Installed dependencies with PDM", fg="green")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _install_dependencies(
    project_path: Path,
    venv_path: Path,
    name: str,
    package_manager: str,
    with_linting: bool,
    with_testing: bool,
    run_subprocess: Callable = subprocess.run,
) -> None:
    """Install project dependencies.

    Args:
        project_path: Path to project directory
        venv_path: Path to virtual environment
        name: Project name
        package_manager: Package manager to use (pip, poetry, pdm)
        with_linting: Whether linting dependencies are needed
        with_testing: Whether testing dependencies are needed
        run_subprocess: Function to run subprocess (for testing)
    """
    click.echo("\n📦 Installing dependencies...")
    click.echo("  (This may take a minute...)")

    try:
        if package_manager == "pip":
            _install_with_pip(
                project_path,
                venv_path,
                name,
                with_linting,
                with_testing,
                run_subprocess,
            )
        elif package_manager == "poetry":
            _install_with_poetry(project_path, run_subprocess)
        elif package_manager == "pdm":
            _install_with_pdm(project_path, run_subprocess)

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
            click.echo(f"    pip install {PROJECT_NAME}")
            click.echo(f"    pip install -e '{DEV_EXTRA}'")
        elif package_manager == "poetry":
            click.echo("    poetry install")
        elif package_manager == "pdm":
            click.echo("    pdm install")


def _setup_linting(project_path: Path, venv_path: Path, install_deps: bool) -> None:
    """Setup linting configuration.

    Args:
        project_path: Path to project directory
        venv_path: Path to virtual environment
        install_deps: Whether dependencies are installed
    """
    click.echo("\n🔍 Setting up linting...")
    create_precommit_config(project_path)

    if install_deps:
        try:
            install_precommit_hooks(project_path, venv_path)
        except RuntimeError as e:
            click.secho(f"  ⚠️  Warning: {e}", fg="yellow")
            click.echo("  You can install hooks later with:")
            click.echo("    pre-commit install")


def _setup_testing(project_path: Path, name: str) -> None:
    """Setup testing configuration.

    Args:
        project_path: Path to project directory
        name: Project name
    """
    click.echo("\n🧪 Setting up testing...")
    create_test_structure(project_path, name)


def _setup_ide(project_path: Path, ide: str, python_version: Optional[str]) -> None:
    """Setup IDE configuration.

    Args:
        project_path: Path to project directory
        ide: IDE to configure (vscode, pycharm, none)
        python_version: Python version
    """
    if ide == "vscode":
        click.echo("\n💻 Configuring VS Code...")
        py_version = (
            python_version or f"{sys.version_info.major}.{sys.version_info.minor}"
        )
        create_vscode_settings(project_path, py_version)
    elif ide == "pycharm":
        click.echo("\n💻 Configuring PyCharm...")
        create_pycharm_settings(project_path)


def _setup_git(project_path: Path) -> None:
    """Setup Git repository.

    Args:
        project_path: Path to project directory
    """
    click.echo("\n📝 Creating .gitignore...")
    from telegram_bot_stack.cli.utils import git as git_utils

    git_utils.create_gitignore(project_path)

    click.echo("\n📚 Initializing Git...")
    git_utils.init_git(project_path, initial_commit=True)


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
    project_path = _validate_project_path(name)

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
            _install_dependencies(
                project_path,
                venv_path,
                name,
                package_manager,
                with_linting,
                with_testing,
            )

        # 6. Create Makefile
        click.echo("\n📋 Creating development configuration...")
        create_makefile(project_path)

        # 7. Setup linting
        if with_linting:
            _setup_linting(project_path, venv_path, install_deps)

        # 8. Setup testing
        if with_testing:
            _setup_testing(project_path, name)

        # 9. Setup IDE
        if ide != "none":
            _setup_ide(project_path, ide, python_version)

        # 10. Setup Git (only if --git flag is set)
        if git:
            _setup_git(project_path)

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
        bot_name: Name of the bot (used in README and bot.py)
    """
    # Create bot.py
    bot_content = '''"""Main bot implementation."""

import logging
import os
import signal

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application

from telegram_bot_stack import BotBase, MemoryStorage

# Load environment variables from .env file
load_dotenv()

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
    bot = Bot(storage=storage, bot_name="My Bot")

    # Create and configure application
    application = Application.builder().token(token).build()
    bot.application = application

    # Register handlers
    bot.register_handlers()

    # Set bot commands in Telegram UI
    async def post_init_wrapper(app):
        await bot.set_bot_commands()

    application.post_init = post_init_wrapper

    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        application.stop_running()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run the bot
    logger.info("Press Ctrl+C to stop")
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


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

### Prerequisites

- ✅ All dependencies are already installed (including `python-dotenv`)
- ✅ Virtual environment is set up and ready to use
- ✅ Development tools are configured (linting, testing, IDE settings)

### Getting Started

1. **Open in VS Code/Cursor** (if using VS Code):
   ```bash
   code .
   ```

   Then **select Python interpreter**:
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Python: Select Interpreter"
   - Choose the one ending with `('./{bot_name}/venv': venv)`

   **Note:** If you see import errors (red squiggles), reload the window:
   - Press `Cmd+Shift+P` / `Ctrl+Shift+P`
   - Type "Developer: Reload Window"

2. **Get your bot token** from [@BotFather](https://t.me/BotFather)

3. **Create `.env` file** with your token:
   ```bash
   echo "BOT_TOKEN=your_token_here" > .env
   ```

4. **Run the bot** (recommended - automatically uses virtual environment):
   ```bash
   telegram-bot-stack dev
   ```

   Or run manually:
   ```bash
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   python bot.py
   ```

**Note:** The `telegram-bot-stack dev` command automatically:
- Detects and uses the virtual environment
- Validates your `.env` file
- Provides auto-reload on code changes (enabled by default)
- Shows clear error messages with helpful suggestions

## Development

### Using CLI Commands

The project includes convenient CLI commands:

```bash
# Run bot in development mode (auto-reload enabled by default)
telegram-bot-stack dev

# Run without auto-reload
telegram-bot-stack dev --no-reload

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
├── .env                # Environment variables (not in git) - create this file!
├── .env.example        # Example environment variables
├── pyproject.toml      # Project config, dependencies, and tool settings
├── Makefile            # Development commands
├── venv/               # Virtual environment (auto-created)
├── tests/              # Test files
│   ├── conftest.py     # Pytest fixtures
│   └── test_bot.py     # Bot tests
└── README.md           # This file
```

## Dependencies

All dependencies are automatically installed when you create the project:

- **telegram-bot-stack** - Main framework
- **python-dotenv** - Environment variable loading (included automatically)
- **python-telegram-bot** - Telegram Bot API wrapper
- **Development tools** - ruff, mypy, pytest, pre-commit (if enabled)

You don't need to install anything manually! If you need to reinstall dependencies:

```bash
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -e .
```

## Common Issues

### Import errors in VS Code (red squiggles under imports)

If you see `Import "telegram_bot_stack" could not be resolved` or similar errors:

1. **Select the correct Python interpreter:**
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Python: Select Interpreter"
   - Choose the one with `venv` in the path

2. **Reload the VS Code window:**
   - Press `Cmd+Shift+P` / `Ctrl+Shift+P`
   - Type "Developer: Reload Window"

3. **If still not working, verify the package is installed:**
   ```bash
   source venv/bin/activate
   python -c "import telegram_bot_stack; print('OK')"
   ```

### ModuleNotFoundError: No module named 'dotenv'

If you see this error when running the bot:

```bash
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install --upgrade telegram-bot-stack
# Or reinstall project dependencies
pip install -e .
```

**Note:** `python-dotenv` is automatically included when you install `telegram-bot-stack`.

### BOT_TOKEN not found

Make sure you've created the `.env` file in the project root:

```bash
echo "BOT_TOKEN=your_token_here" > .env
```

## Documentation

- [telegram-bot-stack Documentation](https://github.com/sensiloles/telegram-bot-stack)
- [CLI Specification](https://github.com/sensiloles/telegram-bot-stack/blob/main/docs/cli-specification.md)
- [python-telegram-bot Documentation](https://docs.python-telegram-bot.org/)

## License

MIT
"""

    (project_path / "README.md").write_text(readme)

    # Get current telegram-bot-stack version
    from telegram_bot_stack.cli.utils.dependencies import (
        get_telegram_bot_stack_version,
    )

    current_version = get_telegram_bot_stack_version()

    # Create requirements.txt for Docker deployment
    requirements_content = f"""# Production dependencies
telegram-bot-stack>={current_version}

# Optional: Uncomment for specific storage backends
# redis>=4.5.0  # For Redis storage
# psycopg2-binary>=2.9.0  # For PostgreSQL storage
"""
    (project_path / "requirements.txt").write_text(requirements_content)

    click.secho(
        "  ✅ Created project files (bot.py, README.md, .env.example, requirements.txt)",
        fg="green",
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

    click.echo("\n⚠️  VS Code/Cursor users:")
    click.echo(
        "  • Select Python interpreter: Cmd+Shift+P → 'Python: Select Interpreter'"
    )
    click.echo("  • Choose the one with 'venv' in the path")
    click.echo(
        "  • If you see import errors, reload window: Cmd+Shift+P → 'Reload Window'"
    )

    click.echo("\n📚 Documentation:")
    click.echo("  https://github.com/sensiloles/telegram-bot-stack\n")
