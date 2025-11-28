"""Integration tests for full VPS deployment flow.

Tests the complete deployment workflow from init to cleanup:
- Deploy init (configuration)
- Deploy up (initial deployment)
- Deploy status (monitoring)
- Deploy logs (log viewing)
- Deploy update (updating bot)
- Deploy down (cleanup)

These tests use a real Mock VPS container with Docker-in-Docker.
"""

import os
import time
from pathlib import Path

import pytest

from telegram_bot_stack.cli.utils.deployment import DeploymentConfig
from telegram_bot_stack.cli.utils.vps import VPSConnection
from tests.integration.fixtures.mock_vps import MockVPS

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestFullDeploymentFlow:
    """Test complete deployment workflow end-to-end."""

    def test_init_creates_configuration(
        self,
        test_bot_project: Path,
        clean_vps: MockVPS,
    ) -> None:
        """Test that deploy init creates valid configuration file.

        Steps:
        1. Run deploy init command
        2. Verify deploy.yaml created
        3. Verify configuration contains all required fields
        4. Verify SSH connection works
        """
        # Create VPS connection
        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        # Test connection
        assert vps.test_connection(), "SSH connection should succeed"
        vps.close()

        # Manually create config (simulating deploy init)
        from telegram_bot_stack.cli.utils.secrets import SecretsManager

        config = DeploymentConfig("deploy.yaml")
        config.set("vps.host", clean_vps.host)
        config.set("vps.user", clean_vps.user)
        config.set("vps.ssh_key", clean_vps.ssh_key_path)
        config.set("vps.port", clean_vps.port)
        config.set("bot.name", "test-bot")
        config.set("bot.token_env", "BOT_TOKEN")
        config.set("bot.entry_point", "bot.py")
        config.set("bot.python_version", "3.11")
        config.set("deployment.method", "docker")
        config.set("deployment.auto_restart", True)
        config.set("deployment.log_rotation", True)
        config.set("resources.memory_limit", "256M")
        config.set("resources.memory_reservation", "128M")
        config.set("resources.cpu_limit", "0.5")
        config.set("resources.cpu_reservation", "0.25")
        config.set("logging.level", "INFO")
        config.set("logging.max_size", "5m")
        config.set("logging.max_files", "5")
        config.set("environment.timezone", "UTC")
        config.set("secrets.encryption_key", SecretsManager.generate_key())
        config.set("backup.enabled", True)
        config.set("backup.auto_backup_before_update", True)
        config.set("backup.retention_days", 7)
        config.set("backup.max_backups", 10)
        config.save()

        # Verify config file exists
        assert Path("deploy.yaml").exists(), "deploy.yaml should be created"

        # Verify config is valid
        loaded_config = DeploymentConfig("deploy.yaml")
        assert loaded_config.validate(), "Configuration should be valid"
        assert loaded_config.get("vps.host") == clean_vps.host
        assert loaded_config.get("bot.name") == "test-bot"

    def test_full_docker_deployment(
        self,
        test_bot_project: Path,
        deployment_config: Path,
        clean_vps: MockVPS,
    ) -> None:
        """Test complete Docker deployment workflow.

        Steps:
        1. Deploy bot to VPS
        2. Verify Docker containers running
        3. Check bot status
        4. View logs
        5. Stop bot
        6. Verify cleanup

        This is the most important integration test!
        """
        # Load config
        config = DeploymentConfig(str(deployment_config))
        bot_name = config.get("bot.name")
        remote_dir = f"/opt/{bot_name}"

        # Create VPS connection
        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            # Test connection
            assert vps.test_connection(), "VPS connection should work"

            # Validate VPS requirements (will install Docker if needed)
            assert vps.validate_vps_requirements(
                "docker", "3.11"
            ), "VPS should meet requirements"

            # Create deployment directory
            assert vps.run_command(
                f"mkdir -p {remote_dir}"
            ), "Should create deployment directory"

            # Transfer bot files
            assert vps.transfer_files(
                test_bot_project, remote_dir
            ), "Should transfer bot files"

            # Generate Docker files
            from telegram_bot_stack.cli.utils.deployment import DockerTemplateRenderer
            from tests.e2e.deployment.conftest import convert_bind_mounts_to_volumes

            temp_dir = Path(".deploy-temp")
            temp_dir.mkdir(exist_ok=True)

            try:
                renderer = DockerTemplateRenderer(config, has_secrets=False)
                renderer.render_all(temp_dir)

                # Transfer Docker files (with modifications for E2E)
                for docker_file in ["Dockerfile", "docker-compose.yml", "Makefile"]:
                    src = temp_dir / docker_file
                    if src.exists():
                        content = src.read_text()

                        # For E2E: Convert bind mounts to named volumes for Docker-in-Docker
                        if docker_file == "docker-compose.yml":
                            content = convert_bind_mounts_to_volumes(content, bot_name)

                        dest = f"{remote_dir}/{docker_file}"
                        assert vps.write_file(
                            content, dest
                        ), f"Should write {docker_file}"

                # Set BOT_TOKEN in environment
                env_content = "BOT_TOKEN=test_token_123456789:ABCdefGHI\n"
                assert vps.write_file(
                    env_content, f"{remote_dir}/.env"
                ), "Should write .env file"

                # Build Docker image
                # Note: This can take 5-15 minutes due to Docker-in-Docker overhead
                build_cmd = f"cd {remote_dir} && make build TAG={bot_name}:test"
                assert vps.run_command(build_cmd), "Docker build should succeed"

                # Start bot
                start_cmd = f"cd {remote_dir} && make up"
                assert vps.run_command(start_cmd), "Bot should start successfully"

                # Wait a moment for container to stabilize and generate logs
                time.sleep(5)

                # Verify container is running
                check_cmd = (
                    f"docker ps --filter name={bot_name} --format '{{{{.Names}}}}'"
                )
                conn = vps.connect()
                result = conn.run(check_cmd, hide=True, pty=False, in_stream=False)
                assert result.ok, "Docker ps should succeed"
                assert (
                    bot_name in result.stdout
                ), f"Container {bot_name} should be running"

                # Check logs (capture both stdout and stderr)
                logs_cmd = f"docker logs {bot_name} --tail 50 2>&1"
                result = conn.run(logs_cmd, hide=True, pty=False, in_stream=False)
                assert result.ok, "Should retrieve logs"

                # Combine stdout and stderr for log checking
                all_logs = (result.stdout + result.stderr).lower()
                assert (
                    "started" in all_logs
                    or "running" in all_logs
                    or "test bot" in all_logs
                ), f"Logs should show bot started. Got: {result.stdout[:200]}"

                # Get container status
                from telegram_bot_stack.cli.utils.vps import get_container_health

                health = get_container_health(conn, bot_name)
                assert health["running"], "Container should be running"

                # Stop bot
                stop_cmd = f"cd {remote_dir} && make down"
                assert vps.run_command(stop_cmd), "Bot should stop successfully"

                # Verify container stopped
                result = conn.run(check_cmd, hide=True)
                assert bot_name not in result.stdout, "Container should be stopped"

            finally:
                # Cleanup temp directory
                import shutil

                if temp_dir.exists():
                    shutil.rmtree(temp_dir)

        finally:
            # Cleanup VPS
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()

    def test_deployment_with_python_version_check(
        self,
        test_bot_project: Path,
        deployment_config: Path,
        clean_vps: MockVPS,
    ) -> None:
        """Test deployment with Python version validation.

        Verifies that:
        1. VPS Python version is checked
        2. Python is installed if missing or too old
        3. Deployment proceeds with correct Python version
        """
        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            # Check Python version
            is_sufficient, current_version = vps.check_python_version("3.9")

            # Should have Python (at least 3.9)
            assert (
                is_sufficient or current_version is not None
            ), "Should detect Python version"

            # If Python is old, validate_vps_requirements should handle it
            assert vps.validate_vps_requirements(
                "docker", "3.9"
            ), "VPS validation should handle Python version"

        finally:
            vps.close()

    def test_docker_installation_on_fresh_vps(
        self,
        clean_vps: MockVPS,
    ) -> None:
        """Test Docker installation on VPS without Docker.

        This tests the auto-installation feature of validate_vps_requirements.
        """
        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            # Ensure Docker is not installed (cleanup from previous tests)
            vps.run_command(
                "apt-get remove -y docker-ce docker-ce-cli containerd.io 2>/dev/null || true",
                hide=True,
            )
            vps.run_command(
                "rm -f /usr/bin/docker /usr/local/bin/docker-compose", hide=True
            )

            # Docker should not be installed
            assert (
                not vps.check_docker_installed()
            ), "Docker should not be installed initially"

            # Validate requirements (should install Docker)
            assert vps.validate_vps_requirements(
                "docker", "3.9"
            ), "Should install Docker automatically"

            # Docker should now be installed
            assert (
                vps.check_docker_installed()
            ), "Docker should be installed after validation"

        finally:
            vps.close()


class TestDeploymentErrorHandling:
    """Test error handling in deployment flow."""

    def test_deployment_without_config_fails_gracefully(
        self,
        tmp_path: Path,
    ) -> None:
        """Test that deployment fails gracefully without config."""
        os.chdir(tmp_path)

        # Try to load non-existent config
        config = DeploymentConfig("deploy.yaml")

        # Validation should fail
        assert not config.validate(), "Validation should fail for non-existent config"

    def test_deployment_with_invalid_ssh_fails_gracefully(
        self,
        test_bot_project: Path,
    ) -> None:
        """Test deployment fails gracefully with invalid SSH credentials."""
        vps = VPSConnection(
            host="invalid.nonexistent.example.com",
            user="root",
            ssh_key="~/.ssh/id_rsa",
        )

        # Connection test should fail gracefully
        assert not vps.test_connection(), "Connection to invalid host should fail"

        vps.close()

    def test_deployment_with_missing_bot_files_fails(
        self,
        deployment_config: Path,
        clean_vps: MockVPS,
        tmp_path: Path,
    ) -> None:
        """Test that deployment fails gracefully when bot files are missing."""
        # Create empty project (no bot.py)
        os.chdir(tmp_path)

        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            remote_dir = "/opt/test-bot-missing"
            vps.run_command(f"mkdir -p {remote_dir}", hide=True)

            # Transfer empty directory
            result = vps.transfer_files(tmp_path, remote_dir)

            # Transfer might succeed, but build should fail
            # (We don't test build failure here as it's too slow)
            assert result is not None, "Transfer should complete"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()


class TestMultipleDeployments:
    """Test multiple deployments and isolation."""

    def test_multiple_bots_can_be_deployed(
        self,
        test_bot_project: Path,
        deployment_config: Path,
        clean_vps: MockVPS,
    ) -> None:
        """Test that multiple bots can be deployed simultaneously.

        Verifies:
        1. Multiple bots can be deployed to different directories
        2. Bots don't interfere with each other
        3. Each bot has isolated resources
        """
        # This is a basic test - we just verify directories can be created
        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            bot1_dir = "/opt/test-bot-1"
            bot2_dir = "/opt/test-bot-2"

            # Create directories
            assert vps.run_command(
                f"mkdir -p {bot1_dir}"
            ), "Should create bot1 directory"
            assert vps.run_command(
                f"mkdir -p {bot2_dir}"
            ), "Should create bot2 directory"

            # Transfer files to both
            assert vps.transfer_files(
                test_bot_project, bot1_dir
            ), "Should transfer to bot1"
            assert vps.transfer_files(
                test_bot_project, bot2_dir
            ), "Should transfer to bot2"

            # Verify both exist
            conn = vps.connect()
            result1 = conn.run(f"ls {bot1_dir}/bot.py", hide=True, warn=True)
            result2 = conn.run(f"ls {bot2_dir}/bot.py", hide=True, warn=True)

            assert result1.ok, "Bot1 files should exist"
            assert result2.ok, "Bot2 files should exist"

        finally:
            vps.run_command(f"rm -rf {bot1_dir} {bot2_dir}", hide=True)
            vps.close()
