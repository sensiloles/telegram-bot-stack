"""Tests for CLI utility modules."""

import subprocess

import pytest

from telegram_bot_stack.cli.utils import dependencies, git, venv


class TestVenvUtils:
    """Tests for venv utilities."""

    def test_create_virtualenv(self, tmp_path):
        """Test virtual environment creation."""
        venv_path = venv.create_virtualenv(tmp_path)

        assert venv_path.exists()
        assert (venv_path / "bin" / "python").exists() or (
            venv_path / "Scripts" / "python.exe"
        ).exists()

    def test_get_venv_python(self, tmp_path):
        """Test getting Python executable path."""
        venv_path = tmp_path / "venv"
        python_path = venv.get_venv_python(venv_path)

        assert "python" in str(python_path).lower()

    def test_get_venv_pip(self, tmp_path):
        """Test getting pip executable path."""
        venv_path = tmp_path / "venv"
        pip_path = venv.get_venv_pip(venv_path)

        assert "pip" in str(pip_path).lower()

    def test_get_activation_command(self, tmp_path):
        """Test getting activation command."""
        venv_path = tmp_path / "venv"
        cmd = venv.get_activation_command(venv_path)

        assert "venv" in cmd
        assert "activate" in cmd


class TestDependenciesUtils:
    """Tests for dependencies utilities."""

    def test_create_requirements_file(self, tmp_path):
        """Test requirements.txt creation."""
        req_file = dependencies.create_requirements_file(
            tmp_path,
            packages=["telegram-bot-stack>=2.0.0"],
            dev_packages=["pytest>=8.0.0"],
        )

        assert req_file.exists()
        content = req_file.read_text()
        assert "telegram-bot-stack" in content
        assert "pytest" in content

    def test_create_pyproject_toml(self, tmp_path):
        """Test pyproject.toml creation."""
        pyproject_file = dependencies.create_pyproject_toml(
            tmp_path, "test-bot", "3.11"
        )

        assert pyproject_file.exists()
        content = pyproject_file.read_text()
        assert "test-bot" in content
        assert "telegram-bot-stack" in content
        assert "[tool.ruff]" in content
        assert "[tool.mypy]" in content


class TestGitUtils:
    """Tests for Git utilities."""

    def test_create_gitignore(self, tmp_path):
        """Test .gitignore creation."""
        gitignore = git.create_gitignore(tmp_path)

        assert gitignore.exists()
        content = gitignore.read_text()
        assert ".env" in content
        assert "venv/" in content
        assert "__pycache__/" in content

    def test_init_git(self, tmp_path):
        """Test Git initialization."""
        # Check if git is available
        try:
            subprocess.run(
                ["git", "--version"],
                check=True,
                capture_output=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Git not available")

        # Create a dummy file first
        (tmp_path / "test.txt").write_text("test")

        git.init_git(tmp_path, initial_commit=False)

        assert (tmp_path / ".git").exists()

    def test_init_git_with_commit(self, tmp_path):
        """Test Git initialization with initial commit."""
        try:
            subprocess.run(
                ["git", "--version"],
                check=True,
                capture_output=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Git not available")

        # Create files
        (tmp_path / "test.txt").write_text("test")
        git.create_gitignore(tmp_path)

        git.init_git(tmp_path, initial_commit=True)

        assert (tmp_path / ".git").exists()
