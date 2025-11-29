"""Dependency management utilities."""

import re
import subprocess
from importlib.metadata import version as get_version
from pathlib import Path
from typing import List, Optional

import click


def get_telegram_bot_stack_version() -> str:
    """Get current telegram-bot-stack version dynamically.

    Returns:
        Current version string (e.g., "1.34.0")

    Raises:
        RuntimeError: If version cannot be determined
    """
    try:
        # Try to get installed version
        return str(get_version("telegram-bot-stack"))
    except Exception:
        # Fallback: try to read from pyproject.toml (for development)
        try:
            # Python 3.11+ has tomllib built-in, otherwise use tomli
            try:
                import tomllib
            except ImportError:
                import tomli as tomllib  # type: ignore[import-not-found,no-redef]
            from pathlib import Path

            # Find project root
            current = Path(__file__).resolve()
            for parent in [current.parent] + list(current.parents[:5]):
                pyproject = parent / "pyproject.toml"
                if pyproject.exists():
                    with open(pyproject, "rb") as f:
                        data = tomllib.load(f)
                        if data.get("project", {}).get("name") == "telegram-bot-stack":
                            return str(data["project"]["version"])
        except Exception:
            pass

        # Last resort fallback
        raise RuntimeError(
            "Could not determine telegram-bot-stack version. "
            "Package may not be installed correctly."
        )


def install_package(
    venv_path: Path,
    package: str,
    upgrade: bool = False,
    quiet: bool = False,
) -> None:
    """Install a Python package in the virtual environment.

    Args:
        venv_path: Path to the virtual environment
        package: Package name (e.g., "telegram-bot-stack>=1.15.0")
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
        current_version = get_telegram_bot_stack_version()
        packages = [f"telegram-bot-stack>={current_version}"]

    content = "# Production dependencies\n"
    content += "\n".join(packages)

    if dev_packages:
        content += "\n\n# Development dependencies\n"
        content += "\n".join(dev_packages)

    requirements_file.write_text(content)
    return requirements_file


def _normalize_package_name(name: str) -> str:
    """Normalize package name to be PEP 508 compliant.

    PEP 508 requires package names to:
    - Start with a letter or number
    - Contain only letters, numbers, hyphens, underscores, and dots
    - Not start or end with special characters

    Args:
        name: Raw package name (e.g., ".test-bot", "my_bot")

    Returns:
        Normalized package name (e.g., "test-bot", "my-bot")
    """
    # Remove leading dots and special characters
    normalized = name.lstrip("._-")

    # If name is empty after stripping, use default
    if not normalized:
        normalized = "bot-project"

    # Replace underscores with hyphens (PEP 8 recommendation)
    normalized = normalized.replace("_", "-")

    # Remove any characters that aren't alphanumeric, hyphens, or dots
    normalized = re.sub(r"[^a-zA-Z0-9.-]", "-", normalized)

    # Remove consecutive hyphens
    normalized = re.sub(r"-+", "-", normalized)

    # Remove trailing dots and hyphens
    normalized = normalized.rstrip(".-")

    # Ensure it starts with alphanumeric
    if normalized and not normalized[0].isalnum():
        normalized = "bot-" + normalized.lstrip(".-")

    return normalized or "bot-project"


def create_pyproject_toml(
    project_path: Path,
    project_name: str,
    python_version: str = "3.9",
    with_linting: bool = True,
    with_testing: bool = True,
) -> Path:
    """Create a pyproject.toml file with modern Python packaging (PEP 621).

    Args:
        project_path: Path to the project directory
        project_name: Name of the project (will be normalized for PEP 508)
        python_version: Minimum Python version
        with_linting: Whether to include linting tools
        with_testing: Whether to include testing tools

    Returns:
        Path to the created pyproject.toml
    """
    pyproject_file = project_path / "pyproject.toml"

    # Normalize package name for PEP 508 compliance
    package_name = _normalize_package_name(project_name)

    # Build dev dependencies list
    dev_deps = []
    if with_testing:
        dev_deps.extend(
            [
                "pytest>=8.0.0",
                "pytest-asyncio>=0.23.0",
                "pytest-mock>=3.12.0",
                "pytest-cov>=4.1.0",
            ]
        )
    if with_linting:
        dev_deps.extend(
            [
                "ruff>=0.8.0",
                "mypy>=1.17.0",
            ]
        )

    dev_deps_str = ",\n    ".join(f'"{dep}"' for dep in dev_deps) if dev_deps else ""

    # Get current telegram-bot-stack version
    current_version = get_telegram_bot_stack_version()

    content = f"""[project]
name = "{package_name}"
version = "0.1.0"
description = "A Telegram bot built with telegram-bot-stack"
readme = "README.md"
requires-python = ">={python_version}"
dependencies = [
    "telegram-bot-stack>={current_version}",
]
"""

    if dev_deps:
        content += f"""
[project.optional-dependencies]
dev = [
    {dev_deps_str},
]
"""

    content += f"""
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.ruff]
line-length = 100
target-version = "py{python_version.replace(".", "")}"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = []

[tool.ruff.lint.isort]
known-first-party = ["telegram_bot_stack"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.mypy]
python_version = "{python_version}"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
ignore_missing_imports = true
exclude = [
    "build/",
    "dist/",
    ".*egg-info/",
    "venv/",
]

[[tool.mypy.overrides]]
module = "telegram.*"
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = "-v --strict-markers"
"""

    pyproject_file.write_text(content)
    click.secho("  ✅ Created pyproject.toml", fg="green")
    return pyproject_file
