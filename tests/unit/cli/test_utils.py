"""Tests for CLI utility modules."""

import subprocess

import pytest

from telegram_bot_stack.cli.utils import dependencies, git, ide, linting, testing, venv


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

    def test_install_package(self, tmp_path, mocker):
        """Test package installation."""
        venv_path = tmp_path / "venv"
        venv_path.mkdir()

        mock_run = mocker.patch("subprocess.run")
        dependencies.install_package(venv_path, "test-package")

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "install" in args
        assert "test-package" in args

    def test_install_package_with_upgrade(self, tmp_path, mocker):
        """Test package installation with upgrade flag."""
        venv_path = tmp_path / "venv"
        venv_path.mkdir()

        mock_run = mocker.patch("subprocess.run")
        dependencies.install_package(venv_path, "test-package", upgrade=True)

        args = mock_run.call_args[0][0]
        assert "--upgrade" in args

    def test_install_package_quiet(self, tmp_path, mocker):
        """Test package installation in quiet mode."""
        venv_path = tmp_path / "venv"
        venv_path.mkdir()

        mock_run = mocker.patch("subprocess.run")
        dependencies.install_package(venv_path, "test-package", quiet=True)

        args = mock_run.call_args[0][0]
        assert "--quiet" in args

    def test_install_package_failure(self, tmp_path, mocker):
        """Test package installation failure."""
        venv_path = tmp_path / "venv"
        venv_path.mkdir()

        mock_run = mocker.patch(
            "subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "pip", stderr="Error"),
        )

        with pytest.raises(RuntimeError, match="Failed to install"):
            dependencies.install_package(venv_path, "test-package")

    def test_install_requirements(self, tmp_path, mocker):
        """Test requirements installation."""
        venv_path = tmp_path / "venv"
        venv_path.mkdir()

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("test-package>=1.0.0\n")

        mock_run = mocker.patch("subprocess.run")
        dependencies.install_requirements(venv_path, req_file)

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "install" in args
        assert "-r" in args

    def test_install_requirements_failure(self, tmp_path, mocker):
        """Test requirements installation failure."""
        venv_path = tmp_path / "venv"
        venv_path.mkdir()

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("test-package>=1.0.0\n")

        mock_run = mocker.patch(
            "subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "pip", stderr="Error"),
        )

        with pytest.raises(RuntimeError, match="Failed to install requirements"):
            dependencies.install_requirements(venv_path, req_file)


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


class TestIdeUtils:
    """Tests for IDE utilities."""

    def test_create_vscode_settings(self, tmp_path):
        """Test VS Code settings creation."""
        ide.create_vscode_settings(tmp_path, python_version="3.11")

        vscode_dir = tmp_path / ".vscode"
        assert vscode_dir.exists()

        settings_file = vscode_dir / "settings.json"
        assert settings_file.exists()
        content = settings_file.read_text()
        assert "python.defaultInterpreterPath" in content
        assert "ruff" in content

        extensions_file = vscode_dir / "extensions.json"
        assert extensions_file.exists()

    def test_create_pycharm_settings(self, tmp_path):
        """Test PyCharm settings creation."""
        ide.create_pycharm_settings(tmp_path)

        idea_dir = tmp_path / ".idea"
        assert idea_dir.exists()
        assert idea_dir.is_dir()

        misc_file = idea_dir / "misc.xml"
        assert misc_file.exists()

        profiles_dir = idea_dir / "inspectionProfiles"
        assert profiles_dir.exists()
        assert (profiles_dir / "profiles_settings.xml").exists()


class TestLintingUtils:
    """Tests for linting utilities."""

    def test_create_precommit_config(self, tmp_path):
        """Test pre-commit config creation."""
        precommit_file = linting.create_precommit_config(tmp_path)

        assert precommit_file.exists()
        content = precommit_file.read_text()
        assert "ruff-pre-commit" in content
        assert "mypy" in content

    def test_install_precommit_hooks(self, tmp_path, mocker):
        """Test pre-commit hooks installation."""
        venv_path = tmp_path / "venv"
        venv_path.mkdir()

        mock_run = mocker.patch("subprocess.run")
        linting.install_precommit_hooks(tmp_path, venv_path)

        # Should be called twice: once for pip install, once for hooks install
        assert mock_run.call_count == 2

    def test_install_precommit_hooks_failure(self, tmp_path, mocker):
        """Test pre-commit hooks installation failure."""
        venv_path = tmp_path / "venv"
        venv_path.mkdir()

        mock_run = mocker.patch(
            "subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "pre-commit", stderr="Error"),
        )

        with pytest.raises(RuntimeError, match="Failed to install pre-commit"):
            linting.install_precommit_hooks(tmp_path, venv_path)


class TestTestingUtils:
    """Tests for testing utilities."""

    def test_create_test_structure(self, tmp_path):
        """Test test structure creation."""
        testing.create_test_structure(tmp_path, "test-bot")

        tests_dir = tmp_path / "tests"
        assert tests_dir.exists()
        assert (tests_dir / "__init__.py").exists()
        assert (tests_dir / "conftest.py").exists()
        assert (tests_dir / "test_bot.py").exists()
        assert (tmp_path / "pytest.ini").exists()

        # Check conftest.py content
        conftest_content = (tests_dir / "conftest.py").read_text()
        assert "pytest" in conftest_content
        assert "test-bot" in conftest_content.lower() or "bot" in conftest_content
