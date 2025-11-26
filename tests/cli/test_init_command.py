"""Tests for init command."""

from pathlib import Path

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
        assert not (project_path / ".gitignore").exists()
