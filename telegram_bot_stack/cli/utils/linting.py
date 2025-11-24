"""Linting and formatting setup utilities."""

import subprocess
from pathlib import Path

import click


def create_precommit_config(project_path: Path) -> Path:
    """Create a .pre-commit-config.yaml file.

    Args:
        project_path: Path to the project directory

    Returns:
        Path to the created .pre-commit-config.yaml
    """
    precommit_file = project_path / ".pre-commit-config.yaml"

    content = """repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.17.0
    hooks:
      - id: mypy
        additional_dependencies: [telegram-bot-stack>=2.0.0]
        args: [--ignore-missing-imports]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
"""

    precommit_file.write_text(content)
    click.secho("  ✅ Created .pre-commit-config.yaml", fg="green")
    return precommit_file


def install_precommit_hooks(project_path: Path, venv_path: Path) -> None:
    """Install pre-commit hooks.

    Args:
        project_path: Path to the project directory
        venv_path: Path to the virtual environment

    Raises:
        RuntimeError: If installation fails
    """
    from telegram_bot_stack.cli.utils.venv import get_venv_python

    python = get_venv_python(venv_path)

    try:
        # Install pre-commit package
        subprocess.run(
            [str(python), "-m", "pip", "install", "pre-commit", "--quiet"],
            check=True,
            capture_output=True,
            text=True,
        )

        # Install hooks
        subprocess.run(
            [str(python), "-m", "pre_commit", "install"],
            cwd=project_path,
            check=True,
            capture_output=True,
            text=True,
        )
        click.secho("  ✅ Pre-commit hooks installed", fg="green")

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to install pre-commit hooks: {e.stderr}") from e
