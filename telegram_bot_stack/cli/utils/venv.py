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
