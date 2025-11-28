"""Tests for VPS connection functionality."""

from telegram_bot_stack.cli.utils.vps import VPSConnection


class TestVPSConnectionCreation:
    """Test VPS connection object creation and configuration."""

    def test_connection_object_creation(self) -> None:
        """Test VPS connection object can be created."""
        vps = VPSConnection(
            host="test.example.com",
            user="root",
            ssh_key="~/.ssh/id_rsa",
            port=22,
        )

        assert vps.host == "test.example.com"
        assert vps.user == "root"
        assert vps.port == 22
        vps.close()

    def test_connection_custom_port(self) -> None:
        """Test VPS connection with custom SSH port."""
        vps = VPSConnection(
            host="test.example.com",
            user="deploy",
            ssh_key="~/.ssh/deploy_key",
            port=2222,
        )

        assert vps.port == 2222
        assert vps.user == "deploy"
        vps.close()


class TestVPSConnectionValidation:
    """Test VPS connection validation."""

    def test_invalid_host_connection(self) -> None:
        """Test connection to invalid host fails gracefully."""
        vps = VPSConnection(
            host="invalid.nonexistent.host.example.com",
            user="root",
            ssh_key="~/.ssh/id_rsa",
        )

        try:
            # Should fail gracefully without raising exception
            result = vps.test_connection()
            assert not result, "Connection to invalid host should fail"
        finally:
            vps.close()

    def test_connection_with_context_manager(self) -> None:
        """Test VPS connection works as context manager."""
        with VPSConnection(
            host="test.example.com",
            user="root",
            ssh_key="~/.ssh/id_rsa",
        ) as vps:
            assert vps.host == "test.example.com"
            # Context manager automatically closes connection
