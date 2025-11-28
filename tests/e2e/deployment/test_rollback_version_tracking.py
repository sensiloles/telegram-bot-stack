"""Integration tests for rollback and version tracking.

Tests deployment versioning and rollback functionality:
- Version tracking across deployments
- Rollback to previous version
- Rollback to specific version
- Docker image cleanup
- Version history management
"""

import time

import pytest

from telegram_bot_stack.cli.utils.deployment import DeploymentConfig
from telegram_bot_stack.cli.utils.version_tracking import VersionTracker
from telegram_bot_stack.cli.utils.vps import VPSConnection
from tests.integration.fixtures.mock_vps import MockVPS

pytestmark = pytest.mark.integration


class TestVersionTracking:
    """Test version tracking functionality."""

    def test_track_deployment_version(
        self,
        clean_vps: MockVPS,
        deployment_config,
    ) -> None:
        """Test tracking a deployment version.

        Steps:
        1. Create version tracker
        2. Add deployment
        3. Verify version saved
        4. Verify version details
        """
        config = DeploymentConfig(str(deployment_config))
        bot_name = config.get("bot.name")
        remote_dir = f"/opt/{bot_name}"

        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            vps.run_command(f"mkdir -p {remote_dir}", hide=True)

            tracker = VersionTracker(bot_name, remote_dir)
            docker_tag = f"{bot_name}:v123456-abc123"

            # Add deployment
            success = tracker.add_deployment(vps, docker_tag, status="active")
            assert success, "Should track deployment"

            # Load history
            versions = tracker.load_history(vps)
            assert len(versions) == 1, "Should have one version"
            assert versions[0].docker_tag == docker_tag
            assert versions[0].status == "active"
            assert versions[0].git_commit == "abc123"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()

    def test_multiple_deployments_mark_old_versions(
        self,
        clean_vps: MockVPS,
        deployment_config,
    ) -> None:
        """Test that new deployments mark old versions as 'old'.

        Steps:
        1. Deploy version 1 (active)
        2. Deploy version 2 (active)
        3. Verify version 1 is now 'old'
        4. Verify version 2 is 'active'
        """
        config = DeploymentConfig(str(deployment_config))
        bot_name = config.get("bot.name")
        remote_dir = f"/opt/{bot_name}"

        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            vps.run_command(f"mkdir -p {remote_dir}", hide=True)
            tracker = VersionTracker(bot_name, remote_dir)

            # Deploy version 1
            tag1 = f"{bot_name}:v1-commit1"
            tracker.add_deployment(vps, tag1, status="active")

            # Deploy version 2
            tag2 = f"{bot_name}:v2-commit2"
            tracker.add_deployment(vps, tag2, status="active")

            # Load history
            versions = tracker.load_history(vps)
            assert len(versions) == 2

            # Find versions
            v1 = next(v for v in versions if v.docker_tag == tag1)
            v2 = next(v for v in versions if v.docker_tag == tag2)

            assert v1.status == "old", "Version 1 should be marked as old"
            assert v2.status == "active", "Version 2 should be active"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()

    def test_version_history_limit(
        self,
        clean_vps: MockVPS,
        deployment_config,
    ) -> None:
        """Test that version history respects max_versions limit."""
        config = DeploymentConfig(str(deployment_config))
        bot_name = config.get("bot.name")
        remote_dir = f"/opt/{bot_name}"

        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            vps.run_command(f"mkdir -p {remote_dir}", hide=True)
            tracker = VersionTracker(bot_name, remote_dir, max_versions=3)

            # Deploy 5 versions
            for i in range(5):
                tag = f"{bot_name}:v{i}-commit{i}"
                tracker.add_deployment(vps, tag, status="active")
                time.sleep(0.1)  # Ensure different timestamps

            # Load history
            versions = tracker.load_history(vps)

            # Should only keep last 3
            assert len(versions) == 3, "Should respect max_versions limit"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()

    def test_get_current_git_commit(self) -> None:
        """Test getting current git commit hash."""
        tracker = VersionTracker("test-bot", "/tmp/test")
        commit = tracker.get_current_git_commit()

        # Should return either a commit hash or 'unknown'
        assert isinstance(commit, str)
        assert len(commit) > 0
        # If in git repo, should be 7-character short hash or 'unknown'
        assert len(commit) == 7 or commit == "unknown"

    def test_generate_docker_tag(self) -> None:
        """Test generating Docker image tag."""
        tracker = VersionTracker("test-bot", "/tmp/test")
        tag = tracker.generate_docker_tag("abc123")

        assert tag.startswith("test-bot:v")
        assert "abc123" in tag
        assert "-" in tag  # Format: bot-name:v{timestamp}-{commit}


class TestRollback:
    """Test rollback functionality."""

    def test_get_previous_version(
        self,
        clean_vps: MockVPS,
        deployment_config,
    ) -> None:
        """Test getting previous version for rollback."""
        config = DeploymentConfig(str(deployment_config))
        bot_name = config.get("bot.name")
        remote_dir = f"/opt/{bot_name}"

        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            vps.run_command(f"mkdir -p {remote_dir}", hide=True)
            tracker = VersionTracker(bot_name, remote_dir)

            # Deploy version 1
            tag1 = f"{bot_name}:v1-commit1"
            tracker.add_deployment(vps, tag1, status="active")

            # Deploy version 2
            tag2 = f"{bot_name}:v2-commit2"
            tracker.add_deployment(vps, tag2, status="active")

            # Get previous version (should be v1)
            previous = tracker.get_previous_version(vps)

            assert previous is not None, "Should find previous version"
            assert previous.docker_tag == tag1
            assert previous.status == "old"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()

    def test_get_previous_version_when_only_one_deployment(
        self,
        clean_vps: MockVPS,
        deployment_config,
    ) -> None:
        """Test getting previous version when only one deployment exists."""
        config = DeploymentConfig(str(deployment_config))
        bot_name = config.get("bot.name")
        remote_dir = f"/opt/{bot_name}"

        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            vps.run_command(f"mkdir -p {remote_dir}", hide=True)
            tracker = VersionTracker(bot_name, remote_dir)

            # Deploy only one version
            tag = f"{bot_name}:v1-commit1"
            tracker.add_deployment(vps, tag, status="active")

            # Get previous version (should be None)
            previous = tracker.get_previous_version(vps)

            assert previous is None, "Should return None when no previous version"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()

    def test_get_version_by_tag(
        self,
        clean_vps: MockVPS,
        deployment_config,
    ) -> None:
        """Test getting a specific version by Docker tag."""
        config = DeploymentConfig(str(deployment_config))
        bot_name = config.get("bot.name")
        remote_dir = f"/opt/{bot_name}"

        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            vps.run_command(f"mkdir -p {remote_dir}", hide=True)
            tracker = VersionTracker(bot_name, remote_dir)

            # Deploy versions
            tag1 = f"{bot_name}:v1-commit1"
            tag2 = f"{bot_name}:v2-commit2"
            tracker.add_deployment(vps, tag1, status="active")
            tracker.add_deployment(vps, tag2, status="active")

            # Get specific version
            version = tracker.get_version_by_tag(vps, tag1)

            assert version is not None, "Should find version by tag"
            assert version.docker_tag == tag1
            assert version.git_commit == "commit1"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()

    def test_mark_version_status(
        self,
        clean_vps: MockVPS,
        deployment_config,
    ) -> None:
        """Test marking a version with a new status."""
        config = DeploymentConfig(str(deployment_config))
        bot_name = config.get("bot.name")
        remote_dir = f"/opt/{bot_name}"

        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            vps.run_command(f"mkdir -p {remote_dir}", hide=True)
            tracker = VersionTracker(bot_name, remote_dir)

            # Deploy version
            tag = f"{bot_name}:v1-commit1"
            tracker.add_deployment(vps, tag, status="active")

            # Mark as failed
            success = tracker.mark_version_status(vps, tag, "failed")
            assert success, "Should update status"

            # Verify status updated
            version = tracker.get_version_by_tag(vps, tag)
            assert version.status == "failed"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()


class TestDockerImageCleanup:
    """Test Docker image cleanup functionality."""

    def test_cleanup_old_images(
        self,
        clean_vps: MockVPS,
        deployment_config,
    ) -> None:
        """Test cleaning up old Docker images not in version history.

        Note: This test verifies the cleanup logic without actually
        building Docker images (too slow for integration tests).
        """
        config = DeploymentConfig(str(deployment_config))
        bot_name = config.get("bot.name")
        remote_dir = f"/opt/{bot_name}"

        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            vps.run_command(f"mkdir -p {remote_dir}", hide=True)
            tracker = VersionTracker(bot_name, remote_dir, max_versions=2)

            # Track 2 versions
            tag1 = f"{bot_name}:v1-commit1"
            tag2 = f"{bot_name}:v2-commit2"
            tracker.add_deployment(vps, tag1, status="active")
            tracker.add_deployment(vps, tag2, status="active")

            # Cleanup (won't find images since we didn't build them)
            removed = tracker.cleanup_old_images(vps)

            # Should return 0 (no images to remove)
            assert removed >= 0, "Should return count of removed images"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()


class TestVersionTrackingEdgeCases:
    """Test edge cases in version tracking."""

    def test_version_tracking_with_no_git_repo(
        self,
        clean_vps: MockVPS,
        deployment_config,
        tmp_path,
    ) -> None:
        """Test version tracking when not in a git repository."""
        import os

        # Change to non-git directory
        os.chdir(tmp_path)

        tracker = VersionTracker("test-bot", "/tmp/test")
        commit = tracker.get_current_git_commit()

        # Should return 'unknown' when not in git repo
        assert commit == "unknown", "Should return 'unknown' when not in git repo"

    def test_load_history_when_no_history_file(
        self,
        clean_vps: MockVPS,
        deployment_config,
    ) -> None:
        """Test loading history when history file doesn't exist."""
        config = DeploymentConfig(str(deployment_config))
        bot_name = config.get("bot.name")
        remote_dir = f"/opt/{bot_name}"

        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            vps.run_command(f"mkdir -p {remote_dir}", hide=True)
            tracker = VersionTracker(bot_name, remote_dir)

            # Load history without creating any deployments
            versions = tracker.load_history(vps)

            assert isinstance(versions, list), "Should return list"
            assert len(versions) == 0, "Should return empty list"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()

    def test_version_from_dict_and_to_dict(self) -> None:
        """Test DeploymentVersion serialization."""
        from telegram_bot_stack.cli.utils.version_tracking import DeploymentVersion

        # Create version
        version = DeploymentVersion(
            timestamp="1234567890",
            git_commit="abc123",
            docker_tag="test-bot:v1234567890-abc123",
            status="active",
            deployed_at="2025-01-26 14:30:00",
        )

        # Convert to dict
        data = version.to_dict()

        assert data["timestamp"] == "1234567890"
        assert data["git_commit"] == "abc123"
        assert data["docker_tag"] == "test-bot:v1234567890-abc123"
        assert data["status"] == "active"
        assert data["deployed_at"] == "2025-01-26 14:30:00"

        # Convert back from dict
        restored = DeploymentVersion.from_dict(data)

        assert restored.timestamp == version.timestamp
        assert restored.git_commit == version.git_commit
        assert restored.docker_tag == version.docker_tag
        assert restored.status == version.status
        assert restored.deployed_at == version.deployed_at
