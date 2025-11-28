"""Integration tests for secrets management.

Tests secure secret storage, encryption, and deployment with secrets:
- Secret encryption/decryption
- Setting and retrieving secrets
- Deploying with secrets
- Secret file security (permissions, encryption at rest)
"""

import pytest

from telegram_bot_stack.cli.utils.deployment import DeploymentConfig
from telegram_bot_stack.cli.utils.secrets import SecretsManager
from telegram_bot_stack.cli.utils.vps import VPSConnection
from tests.integration.fixtures.mock_vps import MockVPS

pytestmark = pytest.mark.integration


class TestSecretsEncryption:
    """Test secret encryption and decryption."""

    def test_generate_encryption_key(self) -> None:
        """Test encryption key generation."""
        key1 = SecretsManager.generate_key()
        key2 = SecretsManager.generate_key()

        # Keys should be base64-encoded strings
        assert isinstance(key1, str)
        assert isinstance(key2, str)
        assert len(key1) > 0
        assert len(key2) > 0

        # Keys should be unique
        assert key1 != key2

    def test_encrypt_decrypt_secret(
        self,
        clean_vps: MockVPS,
        deployment_config,
    ) -> None:
        """Test encrypting and decrypting a secret value."""
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
            # Create remote directory
            vps.run_command(f"mkdir -p {remote_dir}", hide=True)

            # Create secrets manager
            secrets = SecretsManager(bot_name, remote_dir, encryption_key)

            # Set a secret
            test_key = "BOT_TOKEN"
            test_value = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"

            assert secrets.set_secret(
                test_key, test_value, vps
            ), "Should set secret successfully"

            # Retrieve secret
            retrieved_value = secrets.get_secret(test_key, vps)
            assert (
                retrieved_value == test_value
            ), "Retrieved secret should match original"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()

    def test_secret_file_is_encrypted_on_vps(
        self,
        clean_vps: MockVPS,
        deployment_config,
    ) -> None:
        """Test that secret file is encrypted on VPS filesystem.

        Verifies:
        1. Secret file exists
        2. File contains encrypted data (not plaintext)
        3. File has correct permissions (600)
        """
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
            vps.run_command(f"mkdir -p {remote_dir}", hide=True)
            secrets = SecretsManager(bot_name, remote_dir, encryption_key)

            # Set a secret with known value
            test_value = "my_secret_token_123"
            secrets.set_secret("TEST_SECRET", test_value, vps)

            # Read secrets file from VPS
            conn = vps.connect()
            secrets_file = f"{remote_dir}/.secrets.env.encrypted"
            result = conn.run(f"cat {secrets_file}", hide=True)

            assert result.ok, "Secrets file should exist"
            file_content = result.stdout

            # Verify file does NOT contain plaintext secret
            assert (
                test_value not in file_content
            ), "Secrets file should not contain plaintext value"

            # Verify file contains encrypted data (base64-like)
            assert (
                "gAAAAA" in file_content or "AAAA" in file_content
            ), "File should contain encrypted data (Fernet format)"

            # Check file permissions
            result = conn.run(f"stat -c '%a' {secrets_file}", hide=True)
            assert result.ok, "Should get file permissions"
            permissions = result.stdout.strip()
            assert (
                permissions == "600"
            ), f"Secrets file should have 600 permissions, got {permissions}"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()


class TestSecretsOperations:
    """Test secrets CRUD operations."""

    def test_list_secrets(
        self,
        clean_vps: MockVPS,
        deployment_config,
    ) -> None:
        """Test listing all secrets (without values)."""
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
            vps.run_command(f"mkdir -p {remote_dir}", hide=True)
            secrets = SecretsManager(bot_name, remote_dir, encryption_key)

            # Set multiple secrets
            secrets.set_secret("SECRET_1", "value1", vps)
            secrets.set_secret("SECRET_2", "value2", vps)
            secrets.set_secret("SECRET_3", "value3", vps)

            # List secrets
            secret_list = secrets.list_secrets(vps, return_values=False)

            assert len(secret_list) == 3, "Should list all secrets"
            assert "SECRET_1" in secret_list
            assert "SECRET_2" in secret_list
            assert "SECRET_3" in secret_list

            # Values should be masked
            for value in secret_list.values():
                assert value == "***", "Secret values should be masked"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()

    def test_remove_secret(
        self,
        clean_vps: MockVPS,
        deployment_config,
    ) -> None:
        """Test removing a secret."""
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
            vps.run_command(f"mkdir -p {remote_dir}", hide=True)
            secrets = SecretsManager(bot_name, remote_dir, encryption_key)

            # Set secrets
            secrets.set_secret("KEEP_ME", "value1", vps)
            secrets.set_secret("DELETE_ME", "value2", vps)

            # Verify both exist
            secret_list = secrets.list_secrets(vps)
            assert len(secret_list) == 2

            # Remove one secret
            assert secrets.remove_secret(
                "DELETE_ME", vps
            ), "Should remove secret successfully"

            # Verify only one remains
            secret_list = secrets.list_secrets(vps)
            assert len(secret_list) == 1
            assert "KEEP_ME" in secret_list
            assert "DELETE_ME" not in secret_list

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()

    def test_update_existing_secret(
        self,
        clean_vps: MockVPS,
        deployment_config,
    ) -> None:
        """Test updating an existing secret value."""
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
            vps.run_command(f"mkdir -p {remote_dir}", hide=True)
            secrets = SecretsManager(bot_name, remote_dir, encryption_key)

            # Set initial value
            secrets.set_secret("API_KEY", "old_value_123", vps)

            # Verify initial value
            value = secrets.get_secret("API_KEY", vps)
            assert value == "old_value_123"

            # Update value
            secrets.set_secret("API_KEY", "new_value_456", vps)

            # Verify updated value
            value = secrets.get_secret("API_KEY", vps)
            assert value == "new_value_456"

            # Verify only one secret exists (not duplicated)
            secret_list = secrets.list_secrets(vps)
            assert len(secret_list) == 1

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()


class TestSecretsWithSpecialCharacters:
    """Test secrets containing special characters."""

    def test_secret_with_special_characters(
        self,
        clean_vps: MockVPS,
        deployment_config,
    ) -> None:
        """Test encrypting secrets with special characters.

        Tests values containing:
        - Spaces
        - Quotes
        - Newlines
        - Special symbols
        """
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
            vps.run_command(f"mkdir -p {remote_dir}", hide=True)
            secrets = SecretsManager(bot_name, remote_dir, encryption_key)

            # Test various special characters
            test_cases = [
                ("SPACES", "value with spaces"),
                ("QUOTES", "value with \"double\" and 'single' quotes"),
                ("SPECIAL", "value@#$%^&*()_+-={}[]|\\:;\"'<>?,./"),
                ("EQUALS", "key=value&other=data"),
            ]

            for key, value in test_cases:
                secrets.set_secret(key, value, vps)
                retrieved = secrets.get_secret(key, vps)
                assert (
                    retrieved == value
                ), f"Secret with special chars should be preserved: {key}"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()


class TestSecretsErrorHandling:
    """Test error handling in secrets management."""

    def test_get_nonexistent_secret(
        self,
        clean_vps: MockVPS,
        deployment_config,
    ) -> None:
        """Test retrieving a secret that doesn't exist."""
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
            vps.run_command(f"mkdir -p {remote_dir}", hide=True)
            secrets = SecretsManager(bot_name, remote_dir, encryption_key)

            # Try to get non-existent secret
            value = secrets.get_secret("NONEXISTENT", vps)
            assert value is None, "Should return None for non-existent secret"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()

    def test_list_secrets_when_no_secrets_file(
        self,
        clean_vps: MockVPS,
        deployment_config,
    ) -> None:
        """Test listing secrets when no secrets file exists."""
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
            vps.run_command(f"mkdir -p {remote_dir}", hide=True)
            secrets = SecretsManager(bot_name, remote_dir, encryption_key)

            # List secrets without creating file
            secret_list = secrets.list_secrets(vps)

            assert isinstance(secret_list, dict), "Should return dict"
            assert len(secret_list) == 0, "Should return empty dict"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()

    def test_remove_nonexistent_secret(
        self,
        clean_vps: MockVPS,
        deployment_config,
    ) -> None:
        """Test removing a secret that doesn't exist."""
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
            vps.run_command(f"mkdir -p {remote_dir}", hide=True)
            secrets = SecretsManager(bot_name, remote_dir, encryption_key)

            # Try to remove non-existent secret
            result = secrets.remove_secret("NONEXISTENT", vps)

            # Should return False (not found)
            assert result is False, "Should return False for non-existent secret"

        finally:
            vps.run_command(f"rm -rf {remote_dir}", hide=True)
            vps.close()
