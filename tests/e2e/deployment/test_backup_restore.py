"""Integration tests for backup and restore functionality.

Tests bot data backup and restoration:
- Creating backups
- Listing backups
- Restoring from backup
- Automatic backups before updates
- Backup retention policies
- Download backups to local machine
"""

import time
from pathlib import Path

import pytest

from telegram_bot_stack.cli.utils.backup import BackupManager
from telegram_bot_stack.cli.utils.deployment import DeploymentConfig
from telegram_bot_stack.cli.utils.vps import VPSConnection
from tests.integration.fixtures.mock_vps import MockVPS

pytestmark = pytest.mark.integration


class TestBackupCreation:
    """Test creating backups of bot data."""

    def test_create_backup_with_data(
        self,
        clean_vps: MockVPS,
        deployment_config: Path,
    ) -> None:
        """Test creating a backup when data exists.

        Steps:
        1. Create bot directory with data
        2. Create backup
        3. Verify backup file exists
        4. Verify backup contains data
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
            # Create directory structure
            vps.run_command(f"mkdir -p {remote_dir}/data", hide=True)

            # Create some test data
            test_data = "test data content\n"
            vps.write_file(test_data, f"{remote_dir}/data/test.db", mode="644")
            vps.write_file("BOT_TOKEN=test_token", f"{remote_dir}/.env", mode="600")

            # Create backup
            backup_mgr = BackupManager(bot_name, remote_dir)
            backup_filename = backup_mgr.create_backup(vps, auto_backup=False)

            assert backup_filename is not None, "Should create backup"
            assert backup_filename.startswith(
                "backup-"
            ), "Backup filename should have correct format"
            assert backup_filename.endswith(".tar.gz"), "Backup should be tarball"

            # Verify backup file exists
            backup_path = f"{remote_dir}/backups/{backup_filename}"
            conn = vps.connect()
            result = conn.run(f"test -f {backup_path}", hide=True)
            assert result.ok, "Backup file should exist"

            # Verify backup contains data
            result = conn.run(f"tar -tzf {backup_path}", hide=True)
            assert result.ok, "Should list backup contents"
            assert "data/test.db" in result.stdout, "Backup should contain data file"
            assert ".env" in result.stdout, "Backup should contain .env file"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()

    def test_create_backup_without_data(
        self,
        clean_vps: MockVPS,
        deployment_config: Path,
    ) -> None:
        """Test creating backup when no data exists.

        Should handle gracefully (return None or create empty backup).
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
            # Create directory without data
            vps.run_command(f"mkdir -p {remote_dir}", hide=True)

            # Try to create backup
            backup_mgr = BackupManager(bot_name, remote_dir)
            backup_filename = backup_mgr.create_backup(vps, auto_backup=False)

            # Should return None (no data to backup)
            assert backup_filename is None, "Should return None when no data to backup"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()

    def test_auto_backup_flag(
        self,
        clean_vps: MockVPS,
        deployment_config: Path,
    ) -> None:
        """Test auto_backup flag reduces verbosity."""
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
            # Create data
            vps.run_command(f"mkdir -p {remote_dir}/data", hide=True)
            vps.write_file("test", f"{remote_dir}/data/test.txt", mode="644")

            # Create auto backup (should be less verbose)
            backup_mgr = BackupManager(bot_name, remote_dir)
            backup_filename = backup_mgr.create_backup(vps, auto_backup=True)

            assert backup_filename is not None, "Should create auto backup"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()


class TestBackupListing:
    """Test listing available backups."""

    def test_list_backups(
        self,
        clean_vps: MockVPS,
        deployment_config: Path,
    ) -> None:
        """Test listing all available backups."""
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
            # Create data
            vps.run_command(f"mkdir -p {remote_dir}/data", hide=True)
            vps.write_file("test", f"{remote_dir}/data/test.txt", mode="644")

            backup_mgr = BackupManager(bot_name, remote_dir)

            # Create multiple backups
            backup1 = backup_mgr.create_backup(vps, auto_backup=True)
            time.sleep(1.1)  # Ensure different timestamps
            backup2 = backup_mgr.create_backup(vps, auto_backup=True)
            time.sleep(1.1)
            backup3 = backup_mgr.create_backup(vps, auto_backup=True)

            assert backup1 is not None
            assert backup2 is not None
            assert backup3 is not None

            # List backups
            backups = backup_mgr.list_backups(vps)

            assert len(backups) == 3, "Should list all backups"

            # Verify backup info
            for backup in backups:
                assert "filename" in backup
                assert "size" in backup
                assert "date" in backup
                assert backup["filename"].startswith("backup-")

            # Verify sorted by date (newest first)
            # backup3 should be first
            assert backups[0]["filename"] == backup3

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()

    def test_list_backups_when_none_exist(
        self,
        clean_vps: MockVPS,
        deployment_config: Path,
    ) -> None:
        """Test listing backups when no backups exist."""
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

            backup_mgr = BackupManager(bot_name, remote_dir)
            backups = backup_mgr.list_backups(vps)

            assert isinstance(backups, list), "Should return list"
            assert len(backups) == 0, "Should return empty list"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()


class TestBackupRestore:
    """Test restoring from backups."""

    def test_restore_backup(
        self,
        clean_vps: MockVPS,
        deployment_config: Path,
    ) -> None:
        """Test restoring bot data from backup.

        Steps:
        1. Create data
        2. Create backup
        3. Modify data
        4. Restore backup
        5. Verify original data restored
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
            # Create original data
            vps.run_command(f"mkdir -p {remote_dir}/data", hide=True)
            original_data = "original data content"
            vps.write_file(original_data, f"{remote_dir}/data/test.db", mode="644")

            # Create backup
            backup_mgr = BackupManager(bot_name, remote_dir)
            backup_filename = backup_mgr.create_backup(vps, auto_backup=True)
            assert backup_filename is not None

            # Modify data
            modified_data = "modified data content"
            vps.write_file(modified_data, f"{remote_dir}/data/test.db", mode="644")

            # Verify data was modified
            conn = vps.connect()
            result = conn.run(f"cat {remote_dir}/data/test.db", hide=True)
            assert modified_data in result.stdout

            # Restore backup (without confirmation)
            success = backup_mgr.restore_backup(vps, backup_filename, confirm=False)
            assert success, "Restore should succeed"

            # Verify original data restored
            result = conn.run(f"cat {remote_dir}/data/test.db", hide=True)
            assert original_data in result.stdout, "Original data should be restored"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()

    def test_restore_nonexistent_backup(
        self,
        clean_vps: MockVPS,
        deployment_config: Path,
    ) -> None:
        """Test restoring from a backup that doesn't exist."""
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

            backup_mgr = BackupManager(bot_name, remote_dir)
            success = backup_mgr.restore_backup(
                vps,
                "nonexistent-backup.tar.gz",
                confirm=False,
            )

            assert not success, "Should fail to restore non-existent backup"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()


class TestBackupRetention:
    """Test backup retention policies."""

    def test_cleanup_old_backups_by_count(
        self,
        clean_vps: MockVPS,
        deployment_config: Path,
    ) -> None:
        """Test cleaning up backups exceeding max_backups limit."""
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
            # Create data
            vps.run_command(f"mkdir -p {remote_dir}/data", hide=True)
            vps.write_file("test", f"{remote_dir}/data/test.txt", mode="644")

            backup_mgr = BackupManager(bot_name, remote_dir)

            # Create 5 backups
            for _i in range(5):
                backup_mgr.create_backup(vps, auto_backup=True)
                time.sleep(1.1)  # Ensure different timestamps

            # Verify all 5 exist
            backups = backup_mgr.list_backups(vps)
            assert len(backups) == 5

            # Cleanup with max_backups=3
            deleted = backup_mgr.cleanup_old_backups(
                vps,
                retention_days=365,  # Keep all by age
                max_backups=3,  # But only keep 3 total
            )

            assert deleted == 2, "Should delete 2 oldest backups"

            # Verify only 3 remain
            backups = backup_mgr.list_backups(vps)
            assert len(backups) == 3

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()


class TestBackupDownload:
    """Test downloading backups to local machine."""

    def test_download_backup(
        self,
        clean_vps: MockVPS,
        deployment_config: Path,
        tmp_path: Path,
    ) -> None:
        """Test downloading a backup from VPS to local machine."""
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
            # Create data and backup
            vps.run_command(f"mkdir -p {remote_dir}/data", hide=True)
            vps.write_file("test data", f"{remote_dir}/data/test.db", mode="644")

            backup_mgr = BackupManager(bot_name, remote_dir)
            backup_filename = backup_mgr.create_backup(vps, auto_backup=True)
            assert backup_filename is not None

            # Download backup
            download_dir = tmp_path / "downloads"
            success = backup_mgr.download_backup(vps, backup_filename, download_dir)

            assert success, "Download should succeed"

            # Verify file was downloaded
            local_file = download_dir / backup_filename
            assert local_file.exists(), "Downloaded file should exist"
            assert local_file.stat().st_size > 0, "Downloaded file should not be empty"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()

    def test_download_nonexistent_backup(
        self,
        clean_vps: MockVPS,
        deployment_config: Path,
        tmp_path: Path,
    ) -> None:
        """Test downloading a backup that doesn't exist."""
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

            backup_mgr = BackupManager(bot_name, remote_dir)
            download_dir = tmp_path / "downloads"

            success = backup_mgr.download_backup(
                vps,
                "nonexistent-backup.tar.gz",
                download_dir,
            )

            assert not success, "Should fail to download non-existent backup"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()


class TestBackupWithSecrets:
    """Test that backups include encrypted secrets."""

    def test_backup_includes_encrypted_secrets(
        self,
        clean_vps: MockVPS,
        deployment_config: Path,
    ) -> None:
        """Test that backups include encrypted secrets file."""
        config = DeploymentConfig(str(deployment_config))
        bot_name = config.get("bot.name")
        remote_dir = f"/opt/{bot_name}"
        encryption_key = config.get("secrets.encryption_key")

        vps = VPSConnection(
            host=clean_vps.host,
            user=clean_vps.user,
            ssh_key=clean_vps.ssh_key_path,
            port=clean_vps.port,
        )

        try:
            # Create data and secrets
            vps.run_command(f"mkdir -p {remote_dir}/data", hide=True)
            vps.write_file("data", f"{remote_dir}/data/test.db", mode="644")

            from telegram_bot_stack.cli.utils.secrets import SecretsManager

            secrets = SecretsManager(bot_name, remote_dir, encryption_key)
            secrets.set_secret("BOT_TOKEN", "secret_value_123", vps)

            # Create backup
            backup_mgr = BackupManager(bot_name, remote_dir)
            backup_filename = backup_mgr.create_backup(vps, auto_backup=True)
            assert backup_filename is not None

            # Verify backup contains encrypted secrets file
            backup_path = f"{remote_dir}/backups/{backup_filename}"
            conn = vps.connect()
            result = conn.run(f"tar -tzf {backup_path}", hide=True)

            assert result.ok, "Should list backup contents"
            assert (
                ".secrets.env.encrypted" in result.stdout
            ), "Backup should include encrypted secrets"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()
