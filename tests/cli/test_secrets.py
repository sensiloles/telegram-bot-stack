"""Tests for secrets management utilities."""

from unittest.mock import MagicMock, patch

from telegram_bot_stack.cli.utils.secrets import SecretsManager


class TestSecretsManager:
    """Test SecretsManager class."""

    def test_generate_key(self):
        """Test encryption key generation."""
        key = SecretsManager.generate_key()
        assert isinstance(key, str)
        assert len(key) > 0

    def test_derive_key_from_password(self):
        """Test key derivation from password."""
        password = "test-password"
        salt = b"test-salt-1234"
        key = SecretsManager.derive_key_from_password(password, salt)
        assert isinstance(key, bytes)
        assert len(key) > 0

    def test_set_and_get_secret(self):
        """Test setting and getting a secret."""
        bot_name = "test-bot"
        remote_dir = "/opt/test-bot"
        encryption_key = SecretsManager.generate_key()
        secrets_manager = SecretsManager(bot_name, remote_dir, encryption_key)

        # Mock VPS connection
        mock_vps = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_conn.run.return_value = mock_result
        mock_vps.connect.return_value = mock_conn
        mock_vps.write_file.return_value = True

        # Mock list_secrets to return empty initially
        with patch.object(secrets_manager, "list_secrets", return_value={}):
            # Set secret
            result = secrets_manager.set_secret("BOT_TOKEN", "test-token-123", mock_vps)
            assert result is True

        # Mock list_secrets to return the encrypted secret
        encrypted_value = (
            secrets_manager._get_fernet().encrypt(b"test-token-123").decode()
        )
        with patch.object(
            secrets_manager, "list_secrets", return_value={"BOT_TOKEN": encrypted_value}
        ):
            # Get secret
            value = secrets_manager.get_secret("BOT_TOKEN", mock_vps)
            assert value == "test-token-123"

    def test_list_secrets(self):
        """Test listing secrets."""
        bot_name = "test-bot"
        remote_dir = "/opt/test-bot"
        encryption_key = SecretsManager.generate_key()
        secrets_manager = SecretsManager(bot_name, remote_dir, encryption_key)

        # Mock VPS connection
        mock_vps = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()
        encrypted_value = secrets_manager._get_fernet().encrypt(b"test-token").decode()
        mock_result.stdout = (
            f"BOT_TOKEN={encrypted_value}\nDB_PASSWORD={encrypted_value}"
        )
        mock_conn.run.return_value = mock_result
        mock_vps.connect.return_value = mock_conn

        # List secrets (names only)
        secrets = secrets_manager.list_secrets(mock_vps, return_values=False)
        assert "BOT_TOKEN" in secrets
        assert "DB_PASSWORD" in secrets
        assert secrets["BOT_TOKEN"] == "***"

        # List secrets (with values)
        secrets = secrets_manager.list_secrets(mock_vps, return_values=True)
        assert "BOT_TOKEN" in secrets
        assert secrets["BOT_TOKEN"] == encrypted_value

    def test_remove_secret(self):
        """Test removing a secret."""
        bot_name = "test-bot"
        remote_dir = "/opt/test-bot"
        encryption_key = SecretsManager.generate_key()
        secrets_manager = SecretsManager(bot_name, remote_dir, encryption_key)

        # Mock VPS connection
        mock_vps = MagicMock()
        encrypted_value = secrets_manager._get_fernet().encrypt(b"test-token").decode()

        # Mock list_secrets to return existing secrets
        with patch.object(
            secrets_manager,
            "list_secrets",
            return_value={"BOT_TOKEN": encrypted_value, "OTHER": encrypted_value},
        ):
            with patch.object(
                secrets_manager, "_write_secrets_file", return_value=True
            ):
                # Remove secret
                result = secrets_manager.remove_secret("BOT_TOKEN", mock_vps)
                assert result is True

    def test_load_secrets_to_env(self):
        """Test loading secrets for environment."""
        bot_name = "test-bot"
        remote_dir = "/opt/test-bot"
        encryption_key = SecretsManager.generate_key()
        secrets_manager = SecretsManager(bot_name, remote_dir, encryption_key)

        # Mock VPS connection
        mock_vps = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()
        encrypted_token = secrets_manager._get_fernet().encrypt(b"test-token").decode()
        encrypted_password = (
            secrets_manager._get_fernet().encrypt(b"test-pass").decode()
        )
        mock_result.stdout = (
            f"BOT_TOKEN={encrypted_token}\nDB_PASSWORD={encrypted_password}"
        )
        mock_conn.run.return_value = mock_result
        mock_vps.connect.return_value = mock_conn

        # Load secrets
        secrets = secrets_manager.load_secrets_to_env(mock_vps)
        assert "BOT_TOKEN" in secrets
        assert secrets["BOT_TOKEN"] == "test-token"
        assert "DB_PASSWORD" in secrets
        assert secrets["DB_PASSWORD"] == "test-pass"

    def test_get_secret_not_found(self):
        """Test getting a non-existent secret."""
        bot_name = "test-bot"
        remote_dir = "/opt/test-bot"
        encryption_key = SecretsManager.generate_key()
        secrets_manager = SecretsManager(bot_name, remote_dir, encryption_key)

        # Mock VPS connection
        mock_vps = MagicMock()

        # Mock list_secrets to return empty
        with patch.object(secrets_manager, "list_secrets", return_value={}):
            value = secrets_manager.get_secret("NON_EXISTENT", mock_vps)
            assert value is None

    def test_list_secrets_empty_file(self):
        """Test listing secrets from empty file."""
        bot_name = "test-bot"
        remote_dir = "/opt/test-bot"
        encryption_key = SecretsManager.generate_key()
        secrets_manager = SecretsManager(bot_name, remote_dir, encryption_key)

        # Mock VPS connection
        mock_vps = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_conn.run.return_value = mock_result
        mock_vps.connect.return_value = mock_conn

        # List secrets
        secrets = secrets_manager.list_secrets(mock_vps)
        assert secrets == {}
