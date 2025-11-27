"""
Secrets management utilities for secure token storage.

Uses Fernet symmetric encryption to store secrets securely on VPS.
"""

import base64
from typing import Any, Dict, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from rich.console import Console

console = Console()


class SecretsManager:
    """Manages encrypted secrets storage on VPS."""

    def __init__(
        self, bot_name: str, remote_dir: str, encryption_key: Optional[str] = None
    ):
        """Initialize secrets manager.

        Args:
            bot_name: Bot name (for file paths)
            remote_dir: Remote directory on VPS (e.g., /opt/bot_name)
            encryption_key: Encryption key (if None, will generate or load from config)
        """
        self.bot_name = bot_name
        self.remote_dir = remote_dir
        self.secrets_file = f"{remote_dir}/.secrets.env"
        self.encryption_key = encryption_key

    @staticmethod
    def generate_key() -> str:
        """Generate a new encryption key.

        Returns:
            Base64-encoded encryption key
        """
        return Fernet.generate_key().decode()

    @staticmethod
    def derive_key_from_password(password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2.

        Args:
            password: Password string
            salt: Salt bytes

        Returns:
            Encryption key bytes
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def _get_fernet(self) -> Fernet:
        """Get Fernet cipher instance.

        Returns:
            Fernet cipher instance

        Raises:
            ValueError: If encryption key is not set
        """
        if not self.encryption_key:
            raise ValueError("Encryption key not set")

        # If key is a password, derive key (for future use)
        # For now, assume key is already a Fernet key
        try:
            return Fernet(self.encryption_key.encode())
        except Exception:
            # If key is not valid Fernet key, treat as password
            # Use bot_name as salt for consistency
            salt = self.bot_name.encode()[:16].ljust(16, b"0")
            key = self.derive_key_from_password(self.encryption_key, salt)
            return Fernet(key)

    def set_secret(self, key: str, value: str, vps_connection: Any) -> bool:
        """Set a secret value on VPS.

        Args:
            key: Secret key name
            value: Secret value
            vps_connection: VPSConnection instance

        Returns:
            True if successful, False otherwise
        """
        try:
            fernet = self._get_fernet()

            # Read existing secrets
            secrets = self.list_secrets(vps_connection, return_values=True)

            # Encrypt and store new secret
            encrypted_value = fernet.encrypt(value.encode()).decode()

            # Update secrets dict
            secrets[key] = encrypted_value

            # Write encrypted secrets file
            return self._write_secrets_file(secrets, vps_connection)

        except Exception as e:
            console.print(f"[red]Failed to set secret: {e}[/red]")
            return False

    def get_secret(self, key: str, vps_connection: Any) -> Optional[str]:
        """Get a secret value from VPS.

        Args:
            key: Secret key name
            vps_connection: VPSConnection instance

        Returns:
            Decrypted secret value or None if not found
        """
        try:
            fernet = self._get_fernet()
            secrets = self.list_secrets(vps_connection, return_values=True)

            if key not in secrets:
                return None

            encrypted_value = secrets[key]
            decrypted_value = fernet.decrypt(encrypted_value.encode()).decode()
            return decrypted_value

        except Exception as e:
            console.print(f"[red]Failed to get secret: {e}[/red]")
            return None

    def list_secrets(
        self, vps_connection: Any, return_values: bool = False
    ) -> Dict[str, str]:
        """List all secrets (names only by default).

        Args:
            vps_connection: VPSConnection instance
            return_values: If True, return encrypted values (for internal use)

        Returns:
            Dictionary of secret names (and optionally encrypted values)
        """
        try:
            # Read secrets file from VPS
            conn = vps_connection.connect()
            result = conn.run(
                f"cat {self.secrets_file} 2>/dev/null || echo ''", hide=True
            )

            if not result.stdout.strip():
                return {}

            secrets: Dict[str, str] = {}
            for line in result.stdout.strip().split("\n"):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if "=" in line:
                    key, value = line.split("=", 1)
                    secrets[key.strip()] = value.strip()

            if return_values:
                return secrets
            else:
                # Return only keys
                return {k: "***" for k in secrets.keys()}

        except Exception as e:
            console.print(f"[yellow]Warning: Could not read secrets file: {e}[/yellow]")
            return {}

    def remove_secret(self, key: str, vps_connection: Any) -> bool:
        """Remove a secret from VPS.

        Args:
            key: Secret key name
            vps_connection: VPSConnection instance

        Returns:
            True if successful, False otherwise
        """
        try:
            secrets = self.list_secrets(vps_connection, return_values=True)

            if key not in secrets:
                console.print(f"[yellow]Secret '{key}' not found[/yellow]")
                return False

            del secrets[key]
            return self._write_secrets_file(secrets, vps_connection)

        except Exception as e:
            console.print(f"[red]Failed to remove secret: {e}[/red]")
            return False

    def _write_secrets_file(self, secrets: Dict[str, str], vps_connection: Any) -> bool:
        """Write encrypted secrets file to VPS.

        Args:
            secrets: Dictionary of encrypted secrets
            vps_connection: VPSConnection instance

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create secrets file content
            content_lines = [
                "# Encrypted secrets file",
                "# Generated by telegram-bot-stack",
                "# DO NOT EDIT MANUALLY",
                "",
            ]

            for key, encrypted_value in sorted(secrets.items()):
                # Store as KEY=ENCRYPTED_VALUE (no quotes needed, base64 handles it)
                content_lines.append(f"{key}={encrypted_value}")

            content = "\n".join(content_lines)

            # Use VPSConnection's write_file method
            result: bool = vps_connection.write_file(
                content, self.secrets_file, mode="600"
            )
            return result

        except Exception as e:
            console.print(f"[red]Failed to write secrets file: {e}[/red]")
            return False

    def load_secrets_to_env(self, vps_connection: Any) -> Dict[str, str]:
        """Load and decrypt all secrets for use in environment.

        Args:
            vps_connection: VPSConnection instance

        Returns:
            Dictionary of decrypted secrets (key -> value)
        """
        try:
            fernet = self._get_fernet()
            encrypted_secrets = self.list_secrets(vps_connection, return_values=True)

            decrypted_secrets: Dict[str, str] = {}
            for key, encrypted_value in encrypted_secrets.items():
                try:
                    decrypted_value = fernet.decrypt(encrypted_value.encode()).decode()
                    decrypted_secrets[key] = decrypted_value
                except Exception as e:
                    console.print(
                        f"[yellow]Warning: Failed to decrypt secret '{key}': {e}[/yellow]"
                    )

            return decrypted_secrets

        except Exception as e:
            console.print(f"[red]Failed to load secrets: {e}[/red]")
            return {}
