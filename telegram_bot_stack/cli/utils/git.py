"""Git initialization utilities."""

import subprocess
from pathlib import Path

import click


def init_git(project_path: Path, initial_commit: bool = True) -> None:
    """Initialize a Git repository in the project directory.

    Args:
        project_path: Path to the project directory
        initial_commit: Whether to create an initial commit

    Raises:
        RuntimeError: If git initialization fails
    """
    try:
        # Check if git is available
        subprocess.run(
            ["git", "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        click.secho("  ⚠️  Git not found. Skipping git initialization.", fg="yellow")
        return

    # Check if already a git repo
    if (project_path / ".git").exists():
        click.echo("  ℹ️  Git repository already initialized")
        return

    try:
        # Initialize git
        subprocess.run(
            ["git", "init"],
            cwd=project_path,
            check=True,
            capture_output=True,
            text=True,
        )
        click.secho("  ✅ Git repository initialized", fg="green")

        # Create initial commit
        if initial_commit:
            subprocess.run(
                ["git", "add", "."],
                cwd=project_path,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [
                    "git",
                    "commit",
                    "-m",
                    "Initial commit: bot project scaffolding",
                ],
                cwd=project_path,
                check=True,
                capture_output=True,
                text=True,
            )
            click.secho("  ✅ Initial commit created", fg="green")

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to initialize git: {e.stderr}") from e


def create_gitignore(project_path: Path) -> Path:
    """Create a .gitignore file for Python/Telegram bot projects.

    Args:
        project_path: Path to the project directory

    Returns:
        Path to the created .gitignore
    """
    gitignore_file = project_path / ".gitignore"

    content = """# Telegram bot
.env
*.db
bot_data/
logs/
data/

# Python
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
.ruff_cache/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
desktop.ini

# Environment
.env.local
.env.*.local
"""

    gitignore_file.write_text(content)
    click.secho("  ✅ Created .gitignore", fg="green")
    return gitignore_file
