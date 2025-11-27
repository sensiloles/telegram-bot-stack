"""
Version tracking for deployments (rollback support).

Tracks deployment history with git commits and Docker image tags.
"""

import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from rich.console import Console

console = Console()


class DeploymentVersion:
    """Represents a single deployment version."""

    def __init__(
        self,
        timestamp: str,
        git_commit: str,
        docker_tag: str,
        status: str = "active",
        deployed_at: Optional[str] = None,
    ):
        """Initialize deployment version.

        Args:
            timestamp: Unix timestamp of deployment
            git_commit: Git commit hash (short)
            docker_tag: Docker image tag
            status: Deployment status (active, failed, rolled_back)
            deployed_at: Human-readable deployment time
        """
        self.timestamp = timestamp
        self.git_commit = git_commit
        self.docker_tag = docker_tag
        self.status = status
        self.deployed_at = deployed_at or datetime.fromtimestamp(
            float(timestamp)
        ).strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation
        """
        return {
            "timestamp": self.timestamp,
            "git_commit": self.git_commit,
            "docker_tag": self.docker_tag,
            "status": self.status,
            "deployed_at": self.deployed_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeploymentVersion":
        """Create from dictionary.

        Args:
            data: Dictionary with version data

        Returns:
            DeploymentVersion instance
        """
        return cls(
            timestamp=data["timestamp"],
            git_commit=data["git_commit"],
            docker_tag=data["docker_tag"],
            status=data.get("status", "active"),
            deployed_at=data.get("deployed_at"),
        )


class VersionTracker:
    """Manages deployment version history."""

    def __init__(self, bot_name: str, remote_dir: str, max_versions: int = 5):
        """Initialize version tracker.

        Args:
            bot_name: Name of the bot
            remote_dir: Remote directory on VPS
            max_versions: Maximum number of versions to keep (default: 5)
        """
        self.bot_name = bot_name
        self.remote_dir = remote_dir
        self.max_versions = max_versions
        self.history_file = f"{remote_dir}/.deploy-history.json"

    def get_current_git_commit(self) -> str:
        """Get current git commit hash (short).

        Returns:
            Short commit hash or 'unknown' if not a git repo
        """
        try:
            import subprocess

            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except Exception:
            return "unknown"

    def generate_docker_tag(self, git_commit: str) -> str:
        """Generate Docker image tag.

        Args:
            git_commit: Git commit hash

        Returns:
            Docker tag in format: {bot_name}:v{timestamp}-{commit}
        """
        timestamp = str(int(time.time()))
        return f"{self.bot_name}:v{timestamp}-{git_commit}"

    def load_history(self, vps_connection: Any) -> List[DeploymentVersion]:
        """Load deployment history from VPS.

        Args:
            vps_connection: VPSConnection instance

        Returns:
            List of DeploymentVersion objects
        """
        try:
            conn = vps_connection.connect()
            result = conn.run(f"cat {self.history_file}", hide=True, warn=True)

            if result.ok and result.stdout:
                data = json.loads(result.stdout)
                return [
                    DeploymentVersion.from_dict(version)
                    for version in data.get("versions", [])
                ]
        except Exception as e:
            console.print(
                f"[yellow]Warning: Could not load deployment history: {e}[/yellow]"
            )

        return []

    def save_history(
        self, vps_connection: Any, versions: List[DeploymentVersion]
    ) -> bool:
        """Save deployment history to VPS.

        Args:
            vps_connection: VPSConnection instance
            versions: List of DeploymentVersion objects

        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                "bot_name": self.bot_name,
                "versions": [v.to_dict() for v in versions],
            }
            content = json.dumps(data, indent=2)

            result = vps_connection.write_file(content, self.history_file, mode="644")
            return bool(result)
        except Exception as e:
            console.print(f"[red]Failed to save deployment history: {e}[/red]")
            return False

    def add_deployment(
        self, vps_connection: Any, docker_tag: str, status: str = "active"
    ) -> bool:
        """Add new deployment to history.

        Args:
            vps_connection: VPSConnection instance
            docker_tag: Docker image tag
            status: Deployment status

        Returns:
            True if successful, False otherwise
        """
        # Load existing history
        versions = self.load_history(vps_connection)

        # Mark previous active deployments as old
        for version in versions:
            if version.status == "active":
                version.status = "old"

        # Extract timestamp and commit from docker tag
        # Format: {bot_name}:v{timestamp}-{commit}
        try:
            tag_parts = docker_tag.split(":")[-1]  # Get version part
            version_info = tag_parts.replace("v", "").split("-")
            timestamp = version_info[0]
            git_commit = version_info[1] if len(version_info) > 1 else "unknown"
        except Exception:
            timestamp = str(int(time.time()))
            git_commit = self.get_current_git_commit()

        # Create new version
        new_version = DeploymentVersion(
            timestamp=timestamp,
            git_commit=git_commit,
            docker_tag=docker_tag,
            status=status,
        )

        # Add to history
        versions.insert(0, new_version)

        # Keep only max_versions
        versions = versions[: self.max_versions]

        # Save history
        return self.save_history(vps_connection, versions)

    def get_version_by_tag(
        self, vps_connection: Any, docker_tag: str
    ) -> Optional[DeploymentVersion]:
        """Get version by Docker tag.

        Args:
            vps_connection: VPSConnection instance
            docker_tag: Docker image tag to find

        Returns:
            DeploymentVersion if found, None otherwise
        """
        versions = self.load_history(vps_connection)

        for version in versions:
            if version.docker_tag == docker_tag:
                return version

        return None

    def get_previous_version(self, vps_connection: Any) -> Optional[DeploymentVersion]:
        """Get previous active deployment (for rollback).

        Args:
            vps_connection: VPSConnection instance

        Returns:
            Previous DeploymentVersion if found, None otherwise
        """
        versions = self.load_history(vps_connection)

        # Skip current active version, return next one
        found_active = False
        for version in versions:
            if version.status == "active" and not found_active:
                found_active = True
                continue

            if version.status in ["old", "rolled_back"]:
                return version

        return None

    def mark_version_status(
        self, vps_connection: Any, docker_tag: str, status: str
    ) -> bool:
        """Update version status.

        Args:
            vps_connection: VPSConnection instance
            docker_tag: Docker image tag
            status: New status

        Returns:
            True if successful, False otherwise
        """
        versions = self.load_history(vps_connection)

        for version in versions:
            if version.docker_tag == docker_tag:
                version.status = status
                return self.save_history(vps_connection, versions)

        console.print(f"[yellow]Warning: Version {docker_tag} not found[/yellow]")
        return False

    def cleanup_old_images(self, vps_connection: Any) -> int:
        """Remove old Docker images not in history.

        Args:
            vps_connection: VPSConnection instance

        Returns:
            Number of images removed
        """
        versions = self.load_history(vps_connection)
        kept_tags = {v.docker_tag for v in versions}

        try:
            conn = vps_connection.connect()

            # List all images for this bot
            result = conn.run(
                f"docker images {self.bot_name} --format '{{{{.Repository}}}}:{{{{.Tag}}}}'",
                hide=True,
                warn=True,
            )

            if not result.ok:
                return 0

            all_images = result.stdout.strip().split("\n")
            removed = 0

            for image in all_images:
                image = image.strip()
                if (
                    image
                    and image not in kept_tags
                    and image != f"{self.bot_name}:latest"
                ):
                    # Remove image
                    conn.run(f"docker rmi {image}", hide=True, warn=True)
                    removed += 1

            return removed

        except Exception as e:
            console.print(f"[yellow]Warning: Could not cleanup images: {e}[/yellow]")
            return 0
