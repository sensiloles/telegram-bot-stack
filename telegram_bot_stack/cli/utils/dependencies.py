"""Dependency management utilities."""

import subprocess
from pathlib import Path
from typing import List, Optional

import click


def install_package(
    venv_path: Path,
    package: str,
    upgrade: bool = False,
    quiet: bool = False,
) -> None:
    """Install a Python package in the virtual environment.

    Args:
        venv_path: Path to the virtual environment
        package: Package name (e.g., "telegram-bot-stack>=2.0.0")
        upgrade: Whether to upgrade if already installed
        quiet: Whether to suppress output

    Raises:
        RuntimeError: If installation fails
    """
    from telegram_bot_stack.cli.utils.venv import get_venv_pip

    pip = get_venv_pip(venv_path)

    cmd = [str(pip), "install"]
    if upgrade:
        cmd.append("--upgrade")
    if quiet:
        cmd.append("--quiet")
    cmd.append(package)

    try:
        subprocess.run(cmd, check=True, capture_output=quiet, text=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to install {package}: {e.stderr}") from e


def install_requirements(
    venv_path: Path,
    requirements_file: Path,
    quiet: bool = False,
) -> None:
    """Install packages from a requirements file.

    Args:
        venv_path: Path to the virtual environment
        requirements_file: Path to requirements.txt
        quiet: Whether to suppress output

    Raises:
        RuntimeError: If installation fails
    """
    from telegram_bot_stack.cli.utils.venv import get_venv_pip

    pip = get_venv_pip(venv_path)

    cmd = [str(pip), "install", "-r", str(requirements_file)]
    if quiet:
        cmd.append("--quiet")

    try:
        subprocess.run(cmd, check=True, capture_output=quiet, text=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Failed to install requirements from {requirements_file}: {e.stderr}"
        ) from e


def create_requirements_file(
    project_path: Path,
    packages: Optional[List[str]] = None,
    dev_packages: Optional[List[str]] = None,
) -> Path:
    """Create a requirements.txt file.

    Args:
        project_path: Path to the project directory
        packages: List of production packages
        dev_packages: List of development packages

    Returns:
        Path to the created requirements.txt
    """
    requirements_file = project_path / "requirements.txt"

    if packages is None:
        packages = ["telegram-bot-stack>=2.0.0"]

    content = "# Production dependencies\n"
    content += "\n".join(packages)

    if dev_packages:
        content += "\n\n# Development dependencies\n"
        content += "\n".join(dev_packages)

    requirements_file.write_text(content)
    return requirements_file


def create_pyproject_toml(
    project_path: Path,
    project_name: str,
    python_version: str = "3.9",
) -> Path:
    """Create a pyproject.toml file with modern Python packaging.

    Args:
        project_path: Path to the project directory
        project_name: Name of the project
        python_version: Minimum Python version

    Returns:
        Path to the created pyproject.toml
    """
    pyproject_file = project_path / "pyproject.toml"

    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
description = "A Telegram bot built with telegram-bot-stack"
readme = "README.md"
requires-python = ">={python_version}"
dependencies = [
    "telegram-bot-stack>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.8.0",
    "mypy>=1.17.0",
]

[tool.ruff]
line-length = 100
target-version = "py{python_version.replace(".", "")}"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = []

[tool.mypy]
python_version = "{python_version}"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
asyncio_mode = "auto"

[tool.coverage.run]
source = ["."]
omit = ["tests/*", "venv/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
'''

    pyproject_file.write_text(content)
    click.secho("  ✅ Created pyproject.toml", fg="green")
    return pyproject_file
