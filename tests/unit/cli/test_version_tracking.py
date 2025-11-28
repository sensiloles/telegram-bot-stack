"""Tests for version tracking module."""

import json
from unittest.mock import MagicMock, patch

import pytest

from telegram_bot_stack.cli.utils.version_tracking import (
    DeploymentVersion,
    VersionTracker,
)


class TestDeploymentVersion:
    """Tests for DeploymentVersion class."""

    def test_create_version(self):
        """Test creating a deployment version."""
        version = DeploymentVersion(
            timestamp="1234567890",
            git_commit="abc123",
            docker_tag="test-bot:v1234567890-abc123",
            status="active",
        )

        assert version.timestamp == "1234567890"
        assert version.git_commit == "abc123"
        assert version.docker_tag == "test-bot:v1234567890-abc123"
        assert version.status == "active"
        assert version.deployed_at is not None

    def test_to_dict(self):
        """Test converting version to dictionary."""
        version = DeploymentVersion(
            timestamp="1234567890",
            git_commit="abc123",
            docker_tag="test-bot:v1234567890-abc123",
            status="active",
            deployed_at="2025-01-26 14:30:00",
        )

        data = version.to_dict()

        assert data["timestamp"] == "1234567890"
        assert data["git_commit"] == "abc123"
        assert data["docker_tag"] == "test-bot:v1234567890-abc123"
        assert data["status"] == "active"
        assert data["deployed_at"] == "2025-01-26 14:30:00"

    def test_from_dict(self):
        """Test creating version from dictionary."""
        data = {
            "timestamp": "1234567890",
            "git_commit": "abc123",
            "docker_tag": "test-bot:v1234567890-abc123",
            "status": "active",
            "deployed_at": "2025-01-26 14:30:00",
        }

        version = DeploymentVersion.from_dict(data)

        assert version.timestamp == "1234567890"
        assert version.git_commit == "abc123"
        assert version.docker_tag == "test-bot:v1234567890-abc123"
        assert version.status == "active"


class TestVersionTracker:
    """Tests for VersionTracker class."""

    @pytest.fixture
    def tracker(self):
        """Create version tracker instance."""
        return VersionTracker("test-bot", "/opt/test-bot", max_versions=5)

    @pytest.fixture
    def mock_vps(self):
        """Create mock VPS connection."""
        vps = MagicMock()
        vps.connect.return_value = MagicMock()
        return vps

    def test_generate_docker_tag(self, tracker):
        """Test generating Docker tag."""
        tag = tracker.generate_docker_tag("abc123")

        assert tag.startswith("test-bot:v")
        assert tag.endswith("-abc123")

    @patch("subprocess.run")
    def test_get_current_git_commit(self, mock_run, tracker):
        """Test getting current git commit."""
        mock_result = MagicMock()
        mock_result.stdout = "abc123\n"
        mock_run.return_value = mock_result

        commit = tracker.get_current_git_commit()

        assert commit == "abc123"
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_get_current_git_commit_no_git(self, mock_run, tracker):
        """Test getting commit when not in git repo."""
        mock_run.side_effect = Exception("Not a git repository")

        commit = tracker.get_current_git_commit()

        assert commit == "unknown"

    def test_load_history_empty(self, tracker, mock_vps):
        """Test loading empty history."""
        mock_conn = mock_vps.connect.return_value
        mock_conn.run.return_value.ok = False

        versions = tracker.load_history(mock_vps)

        assert versions == []

    def test_load_history_with_versions(self, tracker, mock_vps):
        """Test loading history with versions."""
        history_data = {
            "bot_name": "test-bot",
            "versions": [
                {
                    "timestamp": "1234567890",
                    "git_commit": "abc123",
                    "docker_tag": "test-bot:v1234567890-abc123",
                    "status": "active",
                    "deployed_at": "2025-01-26 14:30:00",
                },
                {
                    "timestamp": "1234567880",
                    "git_commit": "def456",
                    "docker_tag": "test-bot:v1234567880-def456",
                    "status": "old",
                    "deployed_at": "2025-01-26 14:20:00",
                },
            ],
        }

        mock_conn = mock_vps.connect.return_value
        mock_conn.run.return_value.ok = True
        mock_conn.run.return_value.stdout = json.dumps(history_data)

        versions = tracker.load_history(mock_vps)

        assert len(versions) == 2
        assert versions[0].git_commit == "abc123"
        assert versions[0].status == "active"
        assert versions[1].git_commit == "def456"
        assert versions[1].status == "old"

    def test_save_history(self, tracker, mock_vps):
        """Test saving deployment history."""
        versions = [
            DeploymentVersion(
                timestamp="1234567890",
                git_commit="abc123",
                docker_tag="test-bot:v1234567890-abc123",
                status="active",
            )
        ]

        mock_vps.write_file.return_value = True

        result = tracker.save_history(mock_vps, versions)

        assert result is True
        mock_vps.write_file.assert_called_once()
        call_args = mock_vps.write_file.call_args
        assert "/opt/test-bot/.deploy-history.json" in call_args[0]

    def test_add_deployment(self, tracker, mock_vps):
        """Test adding new deployment."""
        mock_conn = mock_vps.connect.return_value
        mock_conn.run.return_value.ok = False  # No existing history

        mock_vps.write_file.return_value = True

        result = tracker.add_deployment(
            mock_vps, "test-bot:v1234567890-abc123", status="active"
        )

        assert result is True
        mock_vps.write_file.assert_called_once()

    def test_add_deployment_marks_old_as_inactive(self, tracker, mock_vps):
        """Test that adding deployment marks previous as old."""
        # Setup existing history
        history_data = {
            "bot_name": "test-bot",
            "versions": [
                {
                    "timestamp": "1234567880",
                    "git_commit": "def456",
                    "docker_tag": "test-bot:v1234567880-def456",
                    "status": "active",
                    "deployed_at": "2025-01-26 14:20:00",
                }
            ],
        }

        mock_conn = mock_vps.connect.return_value
        mock_conn.run.return_value.ok = True
        mock_conn.run.return_value.stdout = json.dumps(history_data)

        mock_vps.write_file.return_value = True

        tracker.add_deployment(mock_vps, "test-bot:v1234567890-abc123", status="active")

        # Check that write_file was called
        assert mock_vps.write_file.called
        call_args = mock_vps.write_file.call_args
        saved_data = json.loads(call_args[0][0])

        # Old active version should now be marked as "old"
        old_version = [v for v in saved_data["versions"] if v["git_commit"] == "def456"]
        assert len(old_version) == 1
        assert old_version[0]["status"] == "old"

    def test_get_version_by_tag(self, tracker, mock_vps):
        """Test getting version by Docker tag."""
        history_data = {
            "bot_name": "test-bot",
            "versions": [
                {
                    "timestamp": "1234567890",
                    "git_commit": "abc123",
                    "docker_tag": "test-bot:v1234567890-abc123",
                    "status": "active",
                    "deployed_at": "2025-01-26 14:30:00",
                }
            ],
        }

        mock_conn = mock_vps.connect.return_value
        mock_conn.run.return_value.ok = True
        mock_conn.run.return_value.stdout = json.dumps(history_data)

        version = tracker.get_version_by_tag(mock_vps, "test-bot:v1234567890-abc123")

        assert version is not None
        assert version.git_commit == "abc123"
        assert version.status == "active"

    def test_get_version_by_tag_not_found(self, tracker, mock_vps):
        """Test getting non-existent version."""
        mock_conn = mock_vps.connect.return_value
        mock_conn.run.return_value.ok = False

        version = tracker.get_version_by_tag(mock_vps, "test-bot:v9999999999-xyz")

        assert version is None

    def test_get_previous_version(self, tracker, mock_vps):
        """Test getting previous version for rollback."""
        history_data = {
            "bot_name": "test-bot",
            "versions": [
                {
                    "timestamp": "1234567890",
                    "git_commit": "abc123",
                    "docker_tag": "test-bot:v1234567890-abc123",
                    "status": "active",
                    "deployed_at": "2025-01-26 14:30:00",
                },
                {
                    "timestamp": "1234567880",
                    "git_commit": "def456",
                    "docker_tag": "test-bot:v1234567880-def456",
                    "status": "old",
                    "deployed_at": "2025-01-26 14:20:00",
                },
            ],
        }

        mock_conn = mock_vps.connect.return_value
        mock_conn.run.return_value.ok = True
        mock_conn.run.return_value.stdout = json.dumps(history_data)

        version = tracker.get_previous_version(mock_vps)

        assert version is not None
        assert version.git_commit == "def456"
        assert version.status == "old"

    def test_get_previous_version_none(self, tracker, mock_vps):
        """Test getting previous version when only one exists."""
        history_data = {
            "bot_name": "test-bot",
            "versions": [
                {
                    "timestamp": "1234567890",
                    "git_commit": "abc123",
                    "docker_tag": "test-bot:v1234567890-abc123",
                    "status": "active",
                    "deployed_at": "2025-01-26 14:30:00",
                }
            ],
        }

        mock_conn = mock_vps.connect.return_value
        mock_conn.run.return_value.ok = True
        mock_conn.run.return_value.stdout = json.dumps(history_data)

        version = tracker.get_previous_version(mock_vps)

        assert version is None

    def test_mark_version_status(self, tracker, mock_vps):
        """Test updating version status."""
        history_data = {
            "bot_name": "test-bot",
            "versions": [
                {
                    "timestamp": "1234567890",
                    "git_commit": "abc123",
                    "docker_tag": "test-bot:v1234567890-abc123",
                    "status": "active",
                    "deployed_at": "2025-01-26 14:30:00",
                }
            ],
        }

        mock_conn = mock_vps.connect.return_value
        mock_conn.run.return_value.ok = True
        mock_conn.run.return_value.stdout = json.dumps(history_data)

        mock_vps.write_file.return_value = True

        result = tracker.mark_version_status(
            mock_vps, "test-bot:v1234567890-abc123", "rolled_back"
        )

        assert result is True
        # Check that status was updated
        call_args = mock_vps.write_file.call_args
        saved_data = json.loads(call_args[0][0])
        assert saved_data["versions"][0]["status"] == "rolled_back"

    def test_cleanup_old_images(self, tracker, mock_vps):
        """Test cleanup of old Docker images."""
        # Mock history with 2 versions
        history_data = {
            "bot_name": "test-bot",
            "versions": [
                {
                    "timestamp": "1234567890",
                    "git_commit": "abc123",
                    "docker_tag": "test-bot:v1234567890-abc123",
                    "status": "active",
                    "deployed_at": "2025-01-26 14:30:00",
                },
                {
                    "timestamp": "1234567880",
                    "git_commit": "def456",
                    "docker_tag": "test-bot:v1234567880-def456",
                    "status": "old",
                    "deployed_at": "2025-01-26 14:20:00",
                },
            ],
        }

        mock_conn = mock_vps.connect.return_value
        mock_conn.run.return_value.ok = True
        mock_conn.run.return_value.stdout = json.dumps(history_data)

        # Mock docker images command - returns 3 images (1 should be cleaned)
        docker_images_output = """test-bot:v1234567890-abc123
test-bot:v1234567880-def456
test-bot:v1234567870-old999"""

        def side_effect(*args, **kwargs):
            if "docker images" in args[0]:
                result = MagicMock()
                result.ok = True
                result.stdout = docker_images_output
                return result
            else:
                # For cat command (history file)
                result = MagicMock()
                result.ok = True
                result.stdout = json.dumps(history_data)
                return result

        mock_conn.run.side_effect = side_effect

        removed = tracker.cleanup_old_images(mock_vps)

        assert removed == 1  # One old image should be removed
