"""Tests for init command."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from telegram_bot_stack.cli.main import cli


def test_init_basic(tmp_path):
    """Test basic project initialization."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(
            cli,
            ["init", "test-bot", "--no-install-deps", "--no-git"],
        )

        assert result.exit_code == 0
        assert "Success!" in result.output

        # Check project structure
        project_path = Path("test-bot")
        assert project_path.exists()
        assert (project_path / "bot.py").exists()
        assert (project_path / "README.md").exists()
        assert (project_path / ".env.example").exists()
        assert (project_path / "pyproject.toml").exists()
        assert (project_path / "Makefile").exists()
        assert (project_path / "venv").exists()


def test_init_with_linting(tmp_path):
    """Test project initialization with linting."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(
            cli,
            ["init", "test-bot", "--with-linting", "--no-install-deps", "--no-git"],
        )

        assert result.exit_code == 0

        project_path = Path("test-bot")
        assert (project_path / ".pre-commit-config.yaml").exists()


def test_init_with_testing(tmp_path):
    """Test project initialization with testing."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(
            cli,
            ["init", "test-bot", "--with-testing", "--no-install-deps", "--no-git"],
        )

        assert result.exit_code == 0

        project_path = Path("test-bot")
        assert (project_path / "tests").exists()
        assert (project_path / "tests" / "conftest.py").exists()
        assert (project_path / "tests" / "test_bot.py").exists()


def test_init_with_vscode(tmp_path):
    """Test project initialization with VS Code config."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(
            cli,
            ["init", "test-bot", "--ide", "vscode", "--no-install-deps", "--no-git"],
        )

        assert result.exit_code == 0

        project_path = Path("test-bot")
        assert (project_path / ".vscode").exists()
        assert (project_path / ".vscode" / "settings.json").exists()
        assert (project_path / ".vscode" / "extensions.json").exists()


def test_init_with_pycharm(tmp_path):
    """Test project initialization with PyCharm config."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(
            cli,
            ["init", "test-bot", "--ide", "pycharm", "--no-install-deps", "--no-git"],
        )

        assert result.exit_code == 0

        project_path = Path("test-bot")
        assert (project_path / ".idea").exists()
        assert (project_path / ".idea" / "misc.xml").exists()


def test_init_with_git(tmp_path):
    """Test project initialization with Git."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(
            cli,
            ["init", "test-bot", "--git", "--no-install-deps"],
        )

        assert result.exit_code == 0

        project_path = Path("test-bot")
        assert (project_path / ".gitignore").exists()
        assert (project_path / ".git").exists()


def test_init_pyproject_toml(tmp_path):
    """Test project initialization creates pyproject.toml (always)."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(
            cli,
            [
                "init",
                "test-bot",
                "--no-install-deps",
                "--no-git",
            ],
        )

        assert result.exit_code == 0

        project_path = Path("test-bot")
        assert (project_path / "pyproject.toml").exists()

        # Check pyproject.toml content
        content = (project_path / "pyproject.toml").read_text()
        assert "telegram-bot-stack" in content
        assert "[project]" in content
        assert "[tool.ruff]" in content
        assert "[tool.mypy]" in content
        assert "[tool.pytest.ini_options]" in content


def test_init_existing_directory(tmp_path):
    """Test init fails if directory exists."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Create directory first
        Path("test-bot").mkdir()

        result = runner.invoke(
            cli,
            ["init", "test-bot"],
        )

        assert result.exit_code == 1
        assert "already exists" in result.output


def test_init_minimal(tmp_path):
    """Test minimal project initialization (no extras)."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(
            cli,
            [
                "init",
                "test-bot",
                "--no-linting",
                "--no-testing",
                "--ide",
                "none",
                "--no-git",
                "--no-install-deps",
            ],
        )

        assert result.exit_code == 0

        project_path = Path("test-bot")
        assert (project_path / "bot.py").exists()
        assert (project_path / "venv").exists()

        # Should have pyproject.toml and Makefile (always created)
        assert (project_path / "pyproject.toml").exists()
        assert (project_path / "Makefile").exists()

        # Should not have extras
        assert not (project_path / ".pre-commit-config.yaml").exists()
        assert not (project_path / "tests").exists()
        assert not (project_path / ".vscode").exists()
        assert not (project_path / ".idea").exists()

        # .gitignore is ALWAYS created for security (prevent committing secrets)
        assert (project_path / ".gitignore").exists()


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="subprocess mocking behaves differently in Python 3.9",
)
def test_init_with_install_deps_success(tmp_path):
    """Test project initialization with dependency installation (mocked)."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Mock subprocess.run at module level to catch all calls
        with patch("subprocess.run") as mock_subprocess:
            # Mock successful subprocess calls (venv creation, pip install, etc.)
            mock_result = MagicMock(returncode=0, stderr="", stdout="")
            mock_subprocess.return_value = mock_result

            result = runner.invoke(
                cli,
                ["init", "test-bot", "--no-git"],
            )

            # Should succeed
            assert result.exit_code == 0
            project_path = Path("test-bot")
            assert project_path.exists()


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="subprocess mocking behaves differently in Python 3.9",
)
def test_init_with_install_deps_failure(tmp_path):
    """Test project initialization handles dependency installation failure."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Mock subprocess.run at module level
        with patch("subprocess.run") as mock_subprocess:
            # Make subprocess raise CalledProcessError for pip install
            def side_effect_func(*args, **kwargs):
                # Check if this is a pip install command
                if args and len(args[0]) > 2 and "pip" in str(args[0]):
                    raise subprocess.CalledProcessError(
                        1,
                        args[0],
                        stderr="ERROR: Could not find a version that satisfies the requirement telegram-bot-stack",
                    )
                # Otherwise return success (for venv creation, etc.)
                return MagicMock(returncode=0, stderr="", stdout="")

            mock_subprocess.side_effect = side_effect_func

            result = runner.invoke(
                cli,
                ["init", "test-bot", "--no-git"],
            )

            # Should still succeed but show warning
            assert result.exit_code == 0
            project_path = Path("test-bot")
            assert project_path.exists()
            # Should show warning about installation failure
            assert (
                "Warning" in result.output
                or "install dependencies later" in result.output
            )


def test_init_with_package_manager_poetry(tmp_path):
    """Test project initialization with poetry package manager."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Mock subprocess.run at module level
        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value = MagicMock(returncode=0, stderr="", stdout="")

            result = runner.invoke(
                cli,
                [
                    "init",
                    "test-bot",
                    "--package-manager",
                    "poetry",
                    "--no-git",
                ],
            )

            assert result.exit_code == 0
            project_path = Path("test-bot")
            assert project_path.exists()


def test_init_with_package_manager_pdm(tmp_path):
    """Test project initialization with pdm package manager."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Mock subprocess.run at module level
        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value = MagicMock(returncode=0, stderr="", stdout="")

            result = runner.invoke(
                cli,
                [
                    "init",
                    "test-bot",
                    "--package-manager",
                    "pdm",
                    "--no-git",
                ],
            )

            assert result.exit_code == 0
            project_path = Path("test-bot")
            assert project_path.exists()


def test_init_creates_requirements_txt(tmp_path):
    """Test that init creates requirements.txt for Docker deployment."""
    from telegram_bot_stack.cli.utils.dependencies import (
        get_telegram_bot_stack_version,
    )

    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(
            cli,
            ["init", "test-bot", "--no-install-deps", "--no-git"],
        )

        assert result.exit_code == 0

        # Verify requirements.txt was created
        requirements_file = Path("test-bot") / "requirements.txt"
        assert requirements_file.exists()

        # Verify content includes current version
        content = requirements_file.read_text()
        current_version = get_telegram_bot_stack_version()
        assert f"telegram-bot-stack>={current_version}" in content
        assert "Production dependencies" in content


def test_requirements_txt_content_valid(tmp_path):
    """Verify requirements.txt has valid pip package format."""
    from telegram_bot_stack.cli.commands.init import _create_project_structure

    project_path = tmp_path / "test-bot"
    project_path.mkdir()

    _create_project_structure(project_path, "Test Bot")

    requirements_file = project_path / "requirements.txt"
    assert requirements_file.exists()

    content = requirements_file.read_text()

    # Verify format
    lines = [line.strip() for line in content.split("\n") if line.strip()]
    package_lines = [line for line in lines if not line.startswith("#")]

    # Should have at least one package
    assert len(package_lines) >= 1

    # Main package should have version constraint
    main_package = package_lines[0]
    assert "telegram-bot-stack" in main_package
    assert ">=" in main_package
