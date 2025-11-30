#!/usr/bin/env python3
"""
Cross-platform task runner for telegram-bot-stack development.

This script provides an alternative to Makefile for Windows developers
while maintaining full compatibility with Unix systems.

Usage:
    python scripts/tasks.py help                  # Show all commands
    python scripts/tasks.py test                  # Run all tests
    python scripts/tasks.py test-fast             # Quick tests
    python scripts/tasks.py lint                  # Run linters
    python scripts/tasks.py format                # Format code
    python scripts/tasks.py dev                   # Setup dev environment

Requirements:
    - Python 3.9+
    - No additional dependencies (uses standard library)
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


# Terminal color codes (cross-platform via colorama not required)
class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"

    @classmethod
    def disable(cls) -> None:
        """Disable colors on Windows cmd (unless ANSICON is available)."""
        if platform.system() == "Windows" and "ANSICON" not in os.environ:
            cls.HEADER = cls.BLUE = cls.CYAN = ""
            cls.GREEN = cls.YELLOW = cls.RED = ""
            cls.BOLD = cls.UNDERLINE = cls.END = ""


# Detect Windows cmd and disable colors if needed
if platform.system() == "Windows" and "ANSICON" not in os.environ:
    # Windows Terminal and PowerShell support ANSI, cmd.exe doesn't
    # Keep colors enabled by default (most modern terminals support it)
    pass


def run(
    cmd: List[str],
    check: bool = True,
    cwd: Optional[Path] = None,
    env: Optional[dict] = None,
) -> subprocess.CompletedProcess:
    """
    Run a command and return the result.

    Args:
        cmd: Command to run as list of arguments
        check: Raise exception on non-zero exit code
        cwd: Working directory
        env: Environment variables

    Returns:
        CompletedProcess instance
    """
    print(f"{Colors.CYAN}▶ {' '.join(cmd)}{Colors.END}")
    return subprocess.run(cmd, check=check, cwd=cwd, env=env)


def print_header(text: str) -> None:
    """Print a formatted header."""
    width = 70
    print()
    print(f"{Colors.BOLD}{'━' * width}{Colors.END}")
    print(f"{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.BOLD}{'━' * width}{Colors.END}")
    print()


def print_section(emoji: str, text: str) -> None:
    """Print a section header with emoji."""
    print(f"{Colors.BOLD}{emoji} {text}{Colors.END}")


def print_success(text: str) -> None:
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_warning(text: str) -> None:
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_info(text: str) -> None:
    """Print info message."""
    print(f"{Colors.CYAN}   {text}{Colors.END}")


# ============================================================================
# Task Implementations
# ============================================================================


def task_help() -> None:
    """Show all available commands."""
    print_header("📦 telegram-bot-stack - Development Commands")

    print_section("🧪", "Testing Commands:")
    print_info(
        "python scripts/tasks.py test              - Run all tests (fast + unit + integration)"
    )
    print_info(
        "python scripts/tasks.py test-fast         - ⚡ Quick tests only (unit + basic integration, ~1min)"
    )
    print_info(
        "python scripts/tasks.py test-unit         - Unit tests only (no Docker, ~30s)"
    )
    print_info(
        "python scripts/tasks.py test-integration  - Basic integration tests (config, docker templates)"
    )
    print_info(
        "python scripts/tasks.py test-deploy       - Deployment integration tests (requires Mock VPS)"
    )
    print_info(
        "python scripts/tasks.py test-e2e          - Full E2E tests (Mock VPS + Docker-in-Docker, ~5-30min)"
    )
    print_info(
        "python scripts/tasks.py test-all-versions - Run tests on Python 3.9-3.12 (via tox)"
    )
    print()

    print_section("📊", "Coverage Commands:")
    print_info(
        "python scripts/tasks.py coverage          - Run tests with coverage report (HTML + terminal)"
    )
    print_info(
        "python scripts/tasks.py coverage-html     - Generate HTML coverage report only"
    )
    print_info(
        "python scripts/tasks.py coverage-unit     - Coverage for unit tests only (fast)"
    )
    print()

    print_section("🐳", "Docker Commands:")
    print_info(
        "python scripts/tasks.py build-mock-vps    - Build Mock VPS Docker image (required for E2E tests)"
    )
    print()

    print_section("🔧", "Development Commands:")
    print_info(
        "python scripts/tasks.py venv              - Create virtual environment (Python 3.9+)"
    )
    print_info("python scripts/tasks.py lint              - Run linters (ruff, mypy)")
    print_info("python scripts/tasks.py format            - Auto-format code with ruff")
    print_info(
        "python scripts/tasks.py clean             - Clean build artifacts, cache, venv, and .env"
    )
    print_info(
        "python scripts/tasks.py install           - Install package in dev mode (creates venv if missing)"
    )
    print_info(
        "python scripts/tasks.py dev               - Setup complete development environment"
    )
    print()

    print_section("💡", "Quick Start:")
    print_info(
        "python scripts/tasks.py dev               # First time setup (auto-creates venv)"
    )
    print_info(
        "python scripts/tasks.py test-fast         # Quick validation during development"
    )
    print_info(
        "python scripts/tasks.py test              # Full validation before commit"
    )
    print()
    print_info("⚠️  After 'clean', run 'dev' to recreate environment")

    print(f"{Colors.BOLD}{'━' * 70}{Colors.END}")
    print()


def task_test() -> subprocess.CompletedProcess:
    """Run all tests (unit + integration, skip E2E by default)."""
    print_section("🧪", "Running all tests (unit + integration)...")
    print_info("E2E tests skipped (use 'python scripts/tasks.py test-e2e' to run)")
    return run([sys.executable, "-m", "pytest", "--no-cov", "-q"])


def task_test_fast() -> subprocess.CompletedProcess:
    """Fast tests for development (unit + basic integration, no E2E)."""
    print_section("⚡", "Running fast tests (unit + basic integration)...")
    print_info(
        "Excluding: E2E deployment tests (use 'python scripts/tasks.py test-e2e' for those)"
    )
    return run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/unit/",
            "tests/integration/bot/",
            "tests/integration/deployment/test_config.py",
            "tests/integration/deployment/test_docker.py",
            "tests/integration/deployment/test_cli.py",
            "tests/integration/deployment/test_vps.py",
            "--no-cov",
            "-v",
        ]
    )


def task_test_unit() -> subprocess.CompletedProcess:
    """Run unit tests only (fastest)."""
    print_section("🔬", "Running unit tests...")
    return run([sys.executable, "-m", "pytest", "tests/unit/", "-v", "--no-cov"])


def task_test_integration() -> subprocess.CompletedProcess:
    """Run basic integration tests (no Mock VPS needed)."""
    print_section("🔗", "Running basic integration tests...")
    return run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/integration/bot/",
            "tests/integration/deployment/test_config.py",
            "tests/integration/deployment/test_docker.py",
            "tests/integration/deployment/test_cli.py",
            "-v",
            "--no-cov",
        ]
    )


def task_test_deploy() -> subprocess.CompletedProcess:
    """Run deployment E2E tests (requires Mock VPS)."""
    print_section("🚀", "Running deployment E2E tests...")
    print_warning(
        "Requires Mock VPS image (run 'python scripts/tasks.py build-mock-vps' first)"
    )
    return run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/e2e/deployment/",
            "-v",
            "--no-cov",
            "--run-e2e",
        ]
    )


def task_test_e2e() -> subprocess.CompletedProcess:
    """Run full E2E tests (slow, requires Mock VPS + Docker-in-Docker)."""
    print_section("🎯", "Running full E2E tests (this may take 5-30 minutes)...")
    print_warning("Requires Mock VPS image with Docker-in-Docker support")
    return run(
        [sys.executable, "-m", "pytest", "tests/e2e/", "-v", "--no-cov", "--run-e2e"]
    )


def task_test_all_versions() -> subprocess.CompletedProcess:
    """Run tests on all Python versions (3.9-3.12) using tox."""
    print_section("🐍", "Running tests on Python 3.9-3.12...")
    return run(["tox", "-p"])


def task_test_py39() -> subprocess.CompletedProcess:
    """Run tests on Python 3.9."""
    return run(["tox", "-e", "py39"])


def task_test_py310() -> subprocess.CompletedProcess:
    """Run tests on Python 3.10."""
    return run(["tox", "-e", "py310"])


def task_test_py311() -> subprocess.CompletedProcess:
    """Run tests on Python 3.11."""
    return run(["tox", "-e", "py311"])


def task_test_py312() -> subprocess.CompletedProcess:
    """Run tests on Python 3.12."""
    return run(["tox", "-e", "py312"])


def task_coverage() -> subprocess.CompletedProcess:
    """Run tests with coverage report."""
    print_section("📊", "Running tests with coverage...")
    result = run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--cov=telegram_bot_stack",
            "--cov-report=html",
            "--cov-report=term-missing:skip-covered",
        ]
    )
    print()
    print_success("Coverage report generated!")
    print_info("HTML: htmlcov/index.html")
    print_info("Terminal: see above")
    return result


def task_coverage_html() -> subprocess.CompletedProcess:
    """Generate HTML coverage report only."""
    print_section("📊", "Generating HTML coverage report...")
    result = run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--cov=telegram_bot_stack",
            "--cov-report=html",
            "--no-cov-on-fail",
            "-q",
        ]
    )
    print_success("Coverage report: htmlcov/index.html")
    return result


def task_coverage_unit() -> subprocess.CompletedProcess:
    """Run unit tests with coverage (fast)."""
    print_section("📊", "Running unit tests with coverage (fast)...")
    return run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/unit/",
            "--cov=telegram_bot_stack",
            "--cov-report=term-missing:skip-covered",
        ]
    )


def task_build_mock_vps() -> subprocess.CompletedProcess:
    """Build Mock VPS Docker image for E2E tests."""
    print_section("🐳", "Building Mock VPS Docker image...")
    print_info("This image is used for deployment integration tests")

    fixtures_dir = Path("tests/integration/fixtures")
    result = run(
        ["docker", "build", "-t", "mock-vps:latest", "-f", "Dockerfile.mock-vps", "."],
        cwd=fixtures_dir,
    )

    print_success("Mock VPS image built successfully!")
    print_info(
        "You can now run: python scripts/tasks.py test-deploy or python scripts/tasks.py test-e2e"
    )
    return result


def task_lint() -> None:
    """Run linters (ruff, mypy)."""
    print_section("🔍", "Running linters...")
    result1 = run(["ruff", "check", "."], check=False)

    print()
    print_section("🔍", "Running type checker...")
    result2 = run(["mypy", "telegram_bot_stack/"], check=False)

    if result1.returncode == 0 and result2.returncode == 0:
        print_success("Linting complete!")
    else:
        sys.exit(max(result1.returncode, result2.returncode))


def task_format() -> None:
    """Auto-format code with ruff."""
    print_section("✨", "Formatting code...")
    run(["ruff", "format", "."])
    run(["ruff", "check", "--fix", "."])
    print_success("Code formatted!")


def task_clean() -> None:
    """Clean build artifacts, cache, database files, venv, and .env."""
    print_section("🧹", "Cleaning build artifacts...")

    # Directories to remove
    dirs_to_remove = [
        "build",
        "dist",
        "htmlcov",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".tox",
    ]

    for dir_name in dirs_to_remove:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print_info(f"Removing {dir_name}/")
            shutil.rmtree(dir_path)

    # Files to remove
    files_to_remove = [".coverage", "coverage.xml"]
    for file_name in files_to_remove:
        file_path = Path(file_name)
        if file_path.exists():
            print_info(f"Removing {file_name}")
            file_path.unlink()

    # Remove __pycache__ directories
    for pycache in Path(".").rglob("__pycache__"):
        print_info(f"Removing {pycache}")
        shutil.rmtree(pycache)

    # Remove *.pyc files
    for pyc in Path(".").rglob("*.pyc"):
        print_info(f"Removing {pyc}")
        pyc.unlink()

    # Remove *.egg-info directories
    for egg_info in Path(".").glob("*.egg-info"):
        print_info(f"Removing {egg_info}")
        shutil.rmtree(egg_info)

    print_section("🧹", "Cleaning database files...")
    # Remove database files in root directory only
    for db_pattern in ["*.db", "*.sqlite", "*.sqlite3"]:
        for db_file in Path(".").glob(db_pattern):
            if db_file.is_file():
                print_info(f"Removing {db_file}")
                db_file.unlink()

    print_section("🧹", "Cleaning virtual environment and config...")
    # Remove venv directory
    venv_path = Path("venv")
    if venv_path.exists():
        print_info("Removing venv/")
        shutil.rmtree(venv_path)

    # Remove .env file
    env_file = Path(".env")
    if env_file.exists():
        print_info("Removing .env")
        env_file.unlink()

    print_success("Cleanup complete!")


def task_venv() -> None:
    """Create virtual environment if it doesn't exist."""
    venv_path = Path("venv")

    if venv_path.exists():
        print_success("Virtual environment already exists")
        return

    print_section("🔧", "Creating virtual environment...")

    # Create venv
    import venv as venv_module

    venv_module.create(venv_path, with_pip=True)

    # Upgrade pip, setuptools, and wheel
    print_section("⬆️ ", "Upgrading pip...")
    if platform.system() == "Windows":
        pip_executable = venv_path / "Scripts" / "pip.exe"
    else:
        pip_executable = venv_path / "bin" / "pip"

    run([str(pip_executable), "install", "--upgrade", "pip", "setuptools", "wheel"])

    print_success("Virtual environment created!")
    print()
    print_section("💡", "To activate:")
    if platform.system() == "Windows":
        print_info("   .\\venv\\Scripts\\activate")
    else:
        print_info("   source venv/bin/activate")


def task_install() -> subprocess.CompletedProcess:
    """Install package in development mode (creates venv if missing)."""
    # Ensure venv exists
    task_venv()

    print_section("📦", "Installing package in development mode...")

    # Determine pip path
    venv_path = Path("venv")
    if platform.system() == "Windows":
        pip_executable = venv_path / "Scripts" / "pip.exe"
    else:
        pip_executable = venv_path / "bin" / "pip"

    # Use venv pip if available, otherwise system pip
    if pip_executable.exists():
        result = run([str(pip_executable), "install", "-e", ".[dev]"])
    else:
        result = run([sys.executable, "-m", "pip", "install", "-e", ".[dev]"])

    print_success("Package installed!")
    return result


def task_dev() -> None:
    """Setup complete development environment."""
    print_section("🔧", "Setting up development environment...")

    # Install package
    task_install()

    # Install pre-commit hooks
    print()
    venv_path = Path("venv")
    if platform.system() == "Windows":
        precommit_executable = venv_path / "Scripts" / "pre-commit.exe"
    else:
        precommit_executable = venv_path / "bin" / "pre-commit"

    run([str(precommit_executable), "install"])

    print()
    print_header("✅ Development environment ready!")
    print()
    print_section("Next steps:", "")
    print_info("1. Run tests:         python scripts/tasks.py test-fast")
    print_info(
        "2. Build Mock VPS:    python scripts/tasks.py build-mock-vps  (for E2E tests)"
    )
    print_info("3. Run all tests:     python scripts/tasks.py test")
    print_info("4. Check coverage:    python scripts/tasks.py coverage")
    print()
    print_section("Development workflow:", "")
    print_info(
        "• python scripts/tasks.py test-fast      - Quick validation during development"
    )
    print_info("• python scripts/tasks.py format         - Auto-format before commit")
    print_info("• python scripts/tasks.py test           - Full validation before push")
    print(f"{Colors.BOLD}{'━' * 70}{Colors.END}")
    print()


# ============================================================================
# Main Entry Point
# ============================================================================

TASKS = {
    "help": task_help,
    "test": task_test,
    "test-fast": task_test_fast,
    "test-unit": task_test_unit,
    "test-integration": task_test_integration,
    "test-deploy": task_test_deploy,
    "test-e2e": task_test_e2e,
    "test-all-versions": task_test_all_versions,
    "test-py39": task_test_py39,
    "test-py310": task_test_py310,
    "test-py311": task_test_py311,
    "test-py312": task_test_py312,
    "coverage": task_coverage,
    "coverage-html": task_coverage_html,
    "coverage-unit": task_coverage_unit,
    "build-mock-vps": task_build_mock_vps,
    "lint": task_lint,
    "format": task_format,
    "clean": task_clean,
    "venv": task_venv,
    "install": task_install,
    "dev": task_dev,
}


def main() -> None:
    """Main entry point for the task runner."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "task",
        nargs="?",
        default="help",
        choices=TASKS.keys(),
        help="Task to run (default: help)",
    )

    args = parser.parse_args()

    # Run the task
    try:
        task_func = TASKS[args.task]
        result = task_func()

        # Exit with task's exit code if it returned a CompletedProcess
        if isinstance(result, subprocess.CompletedProcess):
            sys.exit(result.returncode)
        sys.exit(0)

    except KeyboardInterrupt:
        print()
        print(f"{Colors.YELLOW}⚠️  Task interrupted by user{Colors.END}")
        sys.exit(130)
    except subprocess.CalledProcessError as e:
        print()
        print(f"{Colors.RED}❌ Task failed with exit code {e.returncode}{Colors.END}")
        sys.exit(e.returncode)
    except Exception as e:
        print()
        print(f"{Colors.RED}❌ Error: {e}{Colors.END}")
        sys.exit(1)


if __name__ == "__main__":
    main()
