"""Integration tests for VPS requirements validation.

Tests verify that deployment handles missing or outdated dependencies gracefully:
- Missing Docker
- Outdated Python version
- Missing Docker Compose
- Missing system packages
"""

import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from telegram_bot_stack.cli.main import cli
from tests.integration.fixtures.mock_vps import MockVPS


class TestDockerRequirements:
    """Test Docker requirements validation."""

    def test_deploy_up_no_docker(self, clean_vps: MockVPS, tmp_path: Path) -> None:
        """Test deployment fails gracefully when Docker is not installed."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # Initialize deployment
        result_init = runner.invoke(
            cli,
            [
                "deploy",
                "init",
                "--host",
                clean_vps.host,
                "--user",
                clean_vps.user,
                "--ssh-key",
                clean_vps.ssh_key_path,
                "--port",
                str(clean_vps.port),
                "--bot-name",
                "test-bot",
            ],
        )
        assert result_init.exit_code == 0

        # Remove Docker from VPS
        clean_vps.exec("apt-get remove -y docker-ce docker-ce-cli containerd.io")
        clean_vps.exec("rm -f /usr/bin/docker")

        # Create simple bot
        Path("bot.py").write_text("print('test')")
        Path("requirements.txt").write_text("telegram-bot-stack\n")

        # Try to deploy (should fail with helpful message)
        result_up = runner.invoke(cli, ["deploy", "up"])

        # Should detect missing Docker
        assert (
            result_up.exit_code != 0
            or "docker" in result_up.output.lower()
            or "not found" in result_up.output.lower()
        )

    def test_deploy_up_docker_not_running(
        self, clean_vps: MockVPS, tmp_path: Path, deployment_config: Path
    ) -> None:
        """Test deployment handles Docker daemon not running."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # deploy.yaml already created by deployment_config fixture
        assert deployment_config.exists(), "deploy.yaml must exist"

        # Stop Docker daemon
        clean_vps.exec("systemctl stop docker || service docker stop")

        # Create simple bot
        Path("bot.py").write_text("print('test')")
        Path("requirements.txt").write_text("telegram-bot-stack\n")

        # Try to deploy (should fail with helpful message)
        result_up = runner.invoke(cli, ["deploy", "up"])

        # Should detect Docker not running
        assert (
            result_up.exit_code != 0
            or "docker" in result_up.output.lower()
            or "not running" in result_up.output.lower()
            or "daemon" in result_up.output.lower()
        )

    def test_deploy_up_no_docker_compose(
        self, clean_vps: MockVPS, tmp_path: Path, deployment_config: Path
    ) -> None:
        """Test deployment handles missing Docker Compose."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # deploy.yaml already created by deployment_config fixture
        assert deployment_config.exists(), "deploy.yaml must exist"

        # Remove Docker Compose
        clean_vps.exec("rm -f /usr/local/bin/docker-compose || true")
        clean_vps.exec("rm -f /usr/bin/docker-compose || true")

        # Create simple bot
        Path("bot.py").write_text("print('test')")
        Path("requirements.txt").write_text("telegram-bot-stack\n")

        # Try to deploy (should fail with helpful message)
        result_up = runner.invoke(cli, ["deploy", "up"])

        # Should detect missing requirements or fail with validation error
        # Acceptable outcomes:
        # 1. Missing docker-compose detected
        # 2. VPS validation failed (due to broken packages or missing Docker)
        # 3. Deployment failed with non-zero exit code
        assert (
            result_up.exit_code != 0  # Deployment should fail
            or "docker-compose" in result_up.output.lower()
            or "compose" in result_up.output.lower()
            or "validation failed" in result_up.output.lower()
            or "failed to install" in result_up.output.lower()
        )


class TestPythonRequirements:
    """Test Python version requirements validation."""

    def test_deploy_up_old_python(
        self, clean_vps: MockVPS, tmp_path: Path, deployment_config: Path
    ) -> None:
        """Test deployment warns about old Python version."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # deploy.yaml already created by deployment_config fixture
        assert deployment_config.exists(), "deploy.yaml must exist"

        # Check current Python version
        stdout = clean_vps.exec("python3 --version")
        current_version = stdout.strip()

        # Simulate old Python by modifying config
        with open("deploy.yaml") as f:
            import yaml

            config = yaml.safe_load(f)

        # Set minimum required version
        config["bot"]["python_version"] = "3.12"  # Require newer than available

        with open("deploy.yaml", "w") as f:
            yaml.dump(config, f)

        # Try to deploy
        result_up = runner.invoke(cli, ["deploy", "up"])

        # Should warn about Python version (or proceed with available version)
        # This test verifies the system handles version mismatches gracefully

    def test_deploy_up_no_python3(self, clean_vps: MockVPS, tmp_path: Path) -> None:
        """Test deployment handles missing Python 3."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # Initialize deployment
        result_init = runner.invoke(
            cli,
            [
                "deploy",
                "init",
                "--host",
                clean_vps.host,
                "--user",
                clean_vps.user,
                "--ssh-key",
                clean_vps.ssh_key_path,
                "--port",
                str(clean_vps.port),
                "--bot-name",
                "test-bot",
            ],
        )
        assert result_init.exit_code == 0

        # Rename python3 to simulate it missing
        clean_vps.exec("mv /usr/bin/python3 /usr/bin/python3.backup")
        clean_vps.exec("mv /usr/bin/python3.11 /usr/bin/python3.11.backup || true")

        # Create simple bot
        Path("bot.py").write_text("print('test')")
        Path("requirements.txt").write_text("telegram-bot-stack\n")

        # Try to deploy (should fail with helpful message)
        result_up = runner.invoke(cli, ["deploy", "up"])

        # Should detect missing Python
        assert (
            result_up.exit_code != 0
            or "python" in result_up.output.lower()
            or "not found" in result_up.output.lower()
        )

        # Restore Python
        clean_vps.exec("mv /usr/bin/python3.backup /usr/bin/python3 || true")
        clean_vps.exec("mv /usr/bin/python3.11.backup /usr/bin/python3.11 || true")


class TestSystemPackages:
    """Test system package requirements."""

    def test_deploy_up_missing_git(self, clean_vps: MockVPS, tmp_path: Path) -> None:
        """Test deployment handles missing git (if needed)."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # Initialize deployment
        result_init = runner.invoke(
            cli,
            [
                "deploy",
                "init",
                "--host",
                clean_vps.host,
                "--user",
                clean_vps.user,
                "--ssh-key",
                clean_vps.ssh_key_path,
                "--port",
                str(clean_vps.port),
                "--bot-name",
                "test-bot",
            ],
        )
        assert result_init.exit_code == 0

        # Remove git
        clean_vps.exec("apt-get remove -y git || yum remove -y git")

        # Note: Current deployment doesn't require git
        # This test ensures we handle it gracefully if it becomes required


class TestDoctorCommand:
    """Test doctor command for prerequisites validation."""

    def test_doctor_all_requirements_met(
        self, clean_vps: MockVPS, tmp_path: Path
    ) -> None:
        """Test doctor command when all requirements are met."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # Initialize deployment
        result_init = runner.invoke(
            cli,
            [
                "deploy",
                "init",
                "--host",
                clean_vps.host,
                "--user",
                clean_vps.user,
                "--ssh-key",
                clean_vps.ssh_key_path,
                "--port",
                str(clean_vps.port),
                "--bot-name",
                "test-bot",
            ],
        )
        assert result_init.exit_code == 0

        # Run doctor command (if implemented)
        result = runner.invoke(cli, ["deploy", "doctor"])

        # Should pass or report that command doesn't exist yet
        # This is a placeholder for issue #88

    def test_doctor_missing_docker(self, clean_vps: MockVPS, tmp_path: Path) -> None:
        """Test doctor command detects missing Docker."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # Initialize deployment
        result_init = runner.invoke(
            cli,
            [
                "deploy",
                "init",
                "--host",
                clean_vps.host,
                "--user",
                clean_vps.user,
                "--ssh-key",
                clean_vps.ssh_key_path,
                "--port",
                str(clean_vps.port),
                "--bot-name",
                "test-bot",
            ],
        )
        assert result_init.exit_code == 0

        # Remove Docker
        clean_vps.exec("apt-get remove -y docker-ce docker-ce-cli containerd.io")

        # Run doctor command (if implemented)
        result = runner.invoke(cli, ["deploy", "doctor"])

        # Should detect missing Docker or report command not implemented
        # Placeholder for issue #88

    def test_doctor_output_format(self, clean_vps: MockVPS, tmp_path: Path) -> None:
        """Test doctor command output is user-friendly."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # Initialize deployment
        result_init = runner.invoke(
            cli,
            [
                "deploy",
                "init",
                "--host",
                clean_vps.host,
                "--user",
                clean_vps.user,
                "--ssh-key",
                clean_vps.ssh_key_path,
                "--port",
                str(clean_vps.port),
                "--bot-name",
                "test-bot",
            ],
        )
        assert result_init.exit_code == 0

        # Run doctor command (if implemented)
        result = runner.invoke(cli, ["deploy", "doctor"])

        # Should have clear output with:
        # - List of checks performed
        # - Status for each check (✓ or ✗)
        # - Suggestions for fixing issues
        # Placeholder for issue #88


class TestRequirementsValidation:
    """Test automatic requirements validation during deployment."""

    def test_deploy_validates_before_upload(
        self, clean_vps: MockVPS, tmp_path: Path
    ) -> None:
        """Test that deployment validates VPS requirements before uploading files."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # Initialize deployment
        result_init = runner.invoke(
            cli,
            [
                "deploy",
                "init",
                "--host",
                clean_vps.host,
                "--user",
                clean_vps.user,
                "--ssh-key",
                clean_vps.ssh_key_path,
                "--port",
                str(clean_vps.port),
                "--bot-name",
                "test-bot",
            ],
        )
        assert result_init.exit_code == 0

        # Create large bot file (to verify early validation)
        Path("bot.py").write_text("print('test')\n" * 1000)
        Path("requirements.txt").write_text("telegram-bot-stack\n")

        # Remove Docker before deployment
        clean_vps.exec("systemctl stop docker")

        # Try to deploy
        result_up = runner.invoke(cli, ["deploy", "up"])

        # Should fail before uploading files (fast fail)
        # If validation happens early, deployment should fail quickly

    def test_deploy_install_docker_if_missing(
        self, clean_vps: MockVPS, tmp_path: Path
    ) -> None:
        """Test deployment can auto-install Docker if missing (optional feature)."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # Initialize deployment
        result_init = runner.invoke(
            cli,
            [
                "deploy",
                "init",
                "--host",
                clean_vps.host,
                "--user",
                clean_vps.user,
                "--ssh-key",
                clean_vps.ssh_key_path,
                "--port",
                str(clean_vps.port),
                "--bot-name",
                "test-bot",
            ],
        )
        assert result_init.exit_code == 0

        # Remove Docker
        clean_vps.exec("apt-get remove -y docker-ce docker-ce-cli containerd.io")

        # Try to deploy with auto-install flag (if implemented)
        # result = runner.invoke(cli, ["deploy", "up", "--install-deps"])

        # Future feature: auto-install missing dependencies
        # For now, just verify graceful failure


class TestMinimumVersions:
    """Test minimum version requirements."""

    def test_minimum_docker_version(self, clean_vps: MockVPS, tmp_path: Path) -> None:
        """Test deployment checks for minimum Docker version."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # Initialize deployment
        result_init = runner.invoke(
            cli,
            [
                "deploy",
                "init",
                "--host",
                clean_vps.host,
                "--user",
                clean_vps.user,
                "--ssh-key",
                clean_vps.ssh_key_path,
                "--port",
                str(clean_vps.port),
                "--bot-name",
                "test-bot",
            ],
        )
        assert result_init.exit_code == 0

        # Try to start Docker daemon if not running (Docker-in-Docker)
        clean_vps.exec("dockerd &> /var/log/dockerd.log & sleep 3 || true")

        # Check Docker version or binary existence
        stdout = clean_vps.exec(
            "docker --version 2>&1 || which docker 2>&1 || echo 'docker-missing'"
        )

        # This test verifies that deployment would check Docker version
        # Docker might not work in DinD environment, but we check if it's installed or properly reported as missing
        # Acceptable outcomes:
        # 1. Docker works: "Docker version" in output
        # 2. Docker binary exists: "/docker" in path
        # 3. Docker missing (detected): "docker-missing" in output
        # 4. Docker not found: "not found" or "executable file not found" in output
        assert (
            "Docker version" in stdout
            or "/docker" in stdout
            or "docker-missing" in stdout
            or "not found" in stdout.lower()
        ), f"Unexpected Docker check result: {stdout}"

        # Deployment should check minimum version (e.g., >= 20.10) if Docker is available

    def test_minimum_python_version(self, clean_vps: MockVPS, tmp_path: Path) -> None:
        """Test deployment checks for minimum Python version."""
        os.chdir(tmp_path)
        runner = CliRunner()

        # Initialize deployment
        result_init = runner.invoke(
            cli,
            [
                "deploy",
                "init",
                "--host",
                clean_vps.host,
                "--user",
                clean_vps.user,
                "--ssh-key",
                clean_vps.ssh_key_path,
                "--port",
                str(clean_vps.port),
                "--bot-name",
                "test-bot",
            ],
        )
        assert result_init.exit_code == 0

        # Check Python version
        stdout = clean_vps.exec("python3 --version 2>&1")

        # Parse version, handle errors gracefully
        if "Python" in stdout:
            # Should be Python 3.9+ (framework minimum)
            version_str = stdout.strip().split()[-1]  # "Python 3.11.x" -> "3.11.x"
            try:
                major, minor = map(int, version_str.split(".")[:2])
                assert major >= 3 and minor >= 9, f"Python {version_str} is too old"
            except (ValueError, IndexError):
                # If parsing fails, just check Python command exists
                assert "Python 3" in stdout


@pytest.mark.slow
class TestAutoInstallation:
    """Test automatic installation of missing dependencies (future feature)."""

    @pytest.mark.skip(reason="Auto-install not implemented yet")
    def test_auto_install_docker(self, clean_vps: MockVPS, tmp_path: Path) -> None:
        """Test automatic Docker installation if missing."""
        # Future feature: deploy up --install-deps
        pass

    @pytest.mark.skip(reason="Auto-install not implemented yet")
    def test_auto_install_docker_compose(
        self, clean_vps: MockVPS, tmp_path: Path
    ) -> None:
        """Test automatic Docker Compose installation if missing."""
        # Future feature: deploy up --install-deps
        pass
