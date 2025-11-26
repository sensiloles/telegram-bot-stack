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
    """Create a comprehensive .gitignore file for Python/Telegram bot projects.

    Args:
        project_path: Path to the project directory

    Returns:
        Path to the created .gitignore
    """
    gitignore_file = project_path / ".gitignore"

    content = """# Telegram Bot - Environment & Secrets
.env
.env.local
.env.*.local
*.key
*.pem

# Telegram Bot - Data & Storage
*.db
*.sqlite
*.sqlite3
bot_data/
data/
logs/
backups/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environments
venv/
env/
ENV/
env.bak/
venv.bak/

# Testing
.pytest_cache/
.coverage
.coverage.*
coverage.xml
coverage.json
htmlcov/
.tox/
.nox/
.hypothesis/

# Linting & Type Checking
.mypy_cache/
.dmypy.json
dmypy.json
.ruff_cache/
.pytype/
.pyre/

# IDE - VS Code (keep useful config, ignore generated)
.vscode/tasks.json
.vscode/c_cpp_properties.json
.vscode/*.code-workspace
.vscode/.ropeproject

# IDE - PyCharm
.idea/
*.iml
*.iws
*.ipr

# IDE - Other
*.swp
*.swo
*~
.project
.pydevproject
.settings/

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
desktop.ini

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# Celery
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# Project specific
*.log
*.log.*
temp/
tmp/
"""
    gitignore_file.write_text(content)
    click.secho("  ✅ Created .gitignore", fg="green")
    return gitignore_file
