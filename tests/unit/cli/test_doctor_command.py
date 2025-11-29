"""Tests for doctor command."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from telegram_bot_stack.cli.main import cli
from telegram_bot_stack.cli.utils.health_checks import (
    HealthChecker,
    HealthCheckResult,
    HealthReport,
)


class TestDoctorCommand:
    """Tests for doctor command."""

    def test_doctor_basic_run(self, tmp_path):
        """Test doctor runs basic health checks."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["doctor"])

            assert result.exit_code in [0, 1]  # May fail due to missing files
            assert "Running health checks" in result.output

    def test_doctor_with_verbose(self, tmp_path):
        """Test doctor with verbose flag shows all checks."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["doctor", "--verbose"])

            assert "Running health checks" in result.output
            # Verbose should show passed checks too
            assert "✓" in result.output or "✅" in result.output

    def test_doctor_specific_category(self, tmp_path):
        """Test doctor with specific check category."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["doctor", "--check", "python"])

            assert result.exit_code == 0
            assert "Running health checks" in result.output

    def test_doctor_multiple_categories(self, tmp_path):
        """Test doctor with multiple check categories."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                cli, ["doctor", "--check", "python", "--check", "dependencies"]
            )

            assert result.exit_code in [0, 1]
            assert "Running health checks" in result.output

    def test_doctor_strict_mode_with_errors(self, tmp_path):
        """Test doctor exits with error in strict mode when issues found."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Don't create bot.py - should trigger errors
            result = runner.invoke(cli, ["doctor", "--strict"])

            assert result.exit_code == 1

    def test_doctor_fix_flag(self, tmp_path):
        """Test doctor --fix attempts to fix issues."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["doctor", "--fix"])

            # Should run without crashing
            assert result.exit_code in [0, 1]
            assert "Running health checks" in result.output

    def test_doctor_dry_run(self, tmp_path):
        """Test doctor --fix --dry-run shows what would be fixed."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["doctor", "--fix", "--dry-run"])

            # Should run without crashing
            assert result.exit_code in [0, 1]
            assert "Running health checks" in result.output


class TestHealthChecker:
    """Tests for HealthChecker class."""

    def test_check_python_version(self):
        """Test Python version check."""
        checker = HealthChecker()
        result = checker.check_python_version()

        assert isinstance(result, HealthCheckResult)
        assert result.name == "Python version"
        # Should always pass as project requires Python >= 3.9
        assert result.passed is True

    def test_check_dependencies(self):
        """Test dependency checks."""
        checker = HealthChecker()
        results = checker.check_dependencies()

        assert isinstance(results, list)
        assert len(results) > 0
        assert all(isinstance(r, HealthCheckResult) for r in results)

        # Should find telegram-bot-stack installed
        stack_check = next((r for r in results if "telegram-bot-stack" in r.name), None)
        assert stack_check is not None

    def test_check_project_files(self, tmp_path):
        """Test project file checks."""
        checker = HealthChecker(project_path=tmp_path)
        results = checker.check_project_files()

        assert isinstance(results, list)
        assert len(results) > 0

        # bot.py check should fail
        bot_check = next((r for r in results if r.name == "bot.py"), None)
        assert bot_check is not None
        assert bot_check.passed is False

    def test_check_project_files_with_bot_py(self, tmp_path):
        """Test project file checks when bot.py exists."""
        bot_file = tmp_path / "bot.py"
        bot_file.write_text("# bot code")

        checker = HealthChecker(project_path=tmp_path)
        results = checker.check_project_files()

        bot_check = next((r for r in results if r.name == "bot.py"), None)
        assert bot_check is not None
        assert bot_check.passed is True

    def test_check_configuration(self, tmp_path, monkeypatch):
        """Test configuration checks."""
        checker = HealthChecker(project_path=tmp_path)

        # No token set
        monkeypatch.delenv("BOT_TOKEN", raising=False)
        results = checker.check_configuration()

        token_check = next((r for r in results if "BOT_TOKEN" in r.name), None)
        assert token_check is not None
        assert token_check.passed is False

    def test_check_configuration_with_valid_token(self, tmp_path, monkeypatch):
        """Test configuration checks with valid token."""
        checker = HealthChecker(project_path=tmp_path)

        # Set valid token format
        monkeypatch.setenv(
            "BOT_TOKEN", "123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567890"
        )
        results = checker.check_configuration()

        token_check = next((r for r in results if "BOT_TOKEN" in r.name), None)
        assert token_check is not None
        assert token_check.passed is True

    def test_check_security_gitignore_missing(self, tmp_path):
        """Test security check when .gitignore missing."""
        checker = HealthChecker(project_path=tmp_path)
        results = checker.check_security()

        gitignore_check = next((r for r in results if ".gitignore" in r.name), None)
        assert gitignore_check is not None
        assert gitignore_check.passed is False

    def test_check_security_env_not_ignored(self, tmp_path):
        """Test security check when .env not in .gitignore."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.pyc\n")

        checker = HealthChecker(project_path=tmp_path)
        results = checker.check_security()

        env_check = next((r for r in results if ".env in .gitignore" in r.name), None)
        assert env_check is not None
        assert env_check.passed is False
        assert env_check.fixable is True

    def test_check_security_env_properly_ignored(self, tmp_path):
        """Test security check when .env properly in .gitignore."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.pyc\n.env\n")

        checker = HealthChecker(project_path=tmp_path)
        results = checker.check_security()

        env_check = next((r for r in results if ".env in .gitignore" in r.name), None)
        assert env_check is not None
        assert env_check.passed is True

    @patch("shutil.which")
    def test_check_deployment_docker_available(self, mock_which, tmp_path):
        """Test deployment check when Docker available."""
        mock_which.side_effect = (
            lambda cmd: "/usr/bin/docker" if cmd == "docker" else None
        )

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "Docker version 24.0.0"
            mock_run.return_value = mock_result

            checker = HealthChecker(project_path=tmp_path)
            results = checker.check_deployment()

            docker_check = next((r for r in results if r.name == "Docker"), None)
            assert docker_check is not None
            assert docker_check.passed is True

    @patch("shutil.which")
    def test_check_deployment_docker_missing(self, mock_which, tmp_path):
        """Test deployment check when Docker missing."""
        mock_which.return_value = None

        checker = HealthChecker(project_path=tmp_path)
        results = checker.check_deployment()

        docker_check = next((r for r in results if r.name == "Docker"), None)
        assert docker_check is not None
        assert docker_check.passed is False

    def test_run_all_checks(self, tmp_path):
        """Test running all health checks."""
        checker = HealthChecker(project_path=tmp_path)
        report = checker.run_all_checks()

        assert isinstance(report, HealthReport)
        assert len(report.checks) > 0

    def test_run_specific_checks(self, tmp_path):
        """Test running specific check categories."""
        checker = HealthChecker(project_path=tmp_path)
        report = checker.run_all_checks(categories=["python", "dependencies"])

        assert isinstance(report, HealthReport)
        assert len(report.checks) > 0


class TestHealthReport:
    """Tests for HealthReport class."""

    def test_empty_report(self):
        """Test empty health report."""
        report = HealthReport()

        assert len(report.checks) == 0
        assert len(report.errors) == 0
        assert len(report.warnings) == 0
        assert len(report.passed) == 0
        assert report.has_errors is False

    def test_report_with_errors(self):
        """Test report with errors."""
        report = HealthReport()
        report.add(
            HealthCheckResult(
                name="test",
                passed=False,
                message="Error",
                severity="error",
            )
        )

        assert len(report.errors) == 1
        assert len(report.warnings) == 0
        assert len(report.passed) == 0
        assert report.has_errors is True

    def test_report_with_warnings(self):
        """Test report with warnings."""
        report = HealthReport()
        report.add(
            HealthCheckResult(
                name="test",
                passed=False,
                message="Warning",
                severity="warning",
            )
        )

        assert len(report.errors) == 0
        assert len(report.warnings) == 1
        assert len(report.passed) == 0
        assert report.has_errors is False

    def test_report_with_passed(self):
        """Test report with passed checks."""
        report = HealthReport()
        report.add(
            HealthCheckResult(
                name="test",
                passed=True,
                message="OK",
                severity="info",
            )
        )

        assert len(report.errors) == 0
        assert len(report.warnings) == 0
        assert len(report.passed) == 1
        assert report.has_errors is False

    def test_report_mixed_results(self):
        """Test report with mixed results."""
        report = HealthReport()
        report.add(
            HealthCheckResult(
                name="error",
                passed=False,
                message="Error",
                severity="error",
            )
        )
        report.add(
            HealthCheckResult(
                name="warning",
                passed=False,
                message="Warning",
                severity="warning",
            )
        )
        report.add(
            HealthCheckResult(
                name="passed",
                passed=True,
                message="OK",
                severity="info",
            )
        )

        assert len(report.errors) == 1
        assert len(report.warnings) == 1
        assert len(report.passed) == 1
        assert report.has_errors is True
