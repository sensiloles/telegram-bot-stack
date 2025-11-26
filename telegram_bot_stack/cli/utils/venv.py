"""Virtual environment management utilities."""

import subprocess
import sys
from pathlib import Path
from typing import Optional

import click


def create_virtualenv(project_path: Path, python_version: Optional[str] = None) -> Path:
    """Create a virtual environment in the project directory.

    Args:
        project_path: Path to the project directory
        python_version: Optional Python version (e.g., "3.11")

    Returns:
        Path to the created virtual environment

    Raises:
        RuntimeError: If venv creation fails
    """
    venv_path = project_path / "venv"

    if venv_path.exists():
        click.echo(f"  ℹ️  Virtual environment already exists: {venv_path}")
        return venv_path

    click.echo("  📦 Creating virtual environment...")

    # Determine Python executable
    if python_version:
        python_cmd = f"python{python_version}"
    else:
        python_cmd = sys.executable

    try:
        subprocess.run(
            [python_cmd, "-m", "venv", str(venv_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        click.secho(f"  ✅ Virtual environment created: {venv_path}", fg="green")
        return venv_path
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to create virtual environment: {e.stderr}") from e


def get_venv_python(venv_path: Path) -> Path:
    """Get the path to the Python executable in the virtual environment.

    Args:
        venv_path: Path to the virtual environment

    Returns:
        Path to the Python executable
    """
    if sys.platform == "win32":
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"


def get_venv_pip(venv_path: Path) -> Path:
    """Get the path to the pip executable in the virtual environment.

    Args:
        venv_path: Path to the virtual environment

    Returns:
        Path to the pip executable
    """
    if sys.platform == "win32":
        return venv_path / "Scripts" / "pip.exe"
    return venv_path / "bin" / "pip"


def get_activation_command(venv_path: Path) -> str:
    """Get the command to activate the virtual environment.

    Args:
        venv_path: Path to the virtual environment

    Returns:
        Activation command string
    """
    if sys.platform == "win32":
        return f"{venv_path}\\Scripts\\activate"
    return f"source {venv_path}/bin/activate"


def find_venv(project_path: Optional[Path] = None) -> Optional[Path]:
    """Find virtual environment in current directory or parent directories.

    Searches for venv in:
    1. Current directory (venv/)
    2. Parent directories (up to 3 levels)

    Args:
        project_path: Optional starting path. Defaults to current directory.

    Returns:
        Path to venv if found, None otherwise
    """
    if project_path is None:
        project_path = Path.cwd()

    # Check current directory
    venv_path = project_path / "venv"
    if venv_path.exists() and _is_valid_venv(venv_path):
        return venv_path

    # Check parent directories (up to 3 levels)
    for _ in range(3):
        project_path = project_path.parent
        venv_path = project_path / "venv"
        if venv_path.exists() and _is_valid_venv(venv_path):
            return venv_path

    return None


def _is_valid_venv(venv_path: Path) -> bool:
    """Check if path is a valid virtual environment.

    Args:
        venv_path: Path to check

    Returns:
        True if valid venv, False otherwise
    """
    if sys.platform == "win32":
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        python_exe = venv_path / "bin" / "python"

    return python_exe.exists()
