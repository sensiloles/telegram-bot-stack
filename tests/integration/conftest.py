"""Pytest configuration for integration tests."""

# Import fixtures to make them available
from tests.integration.fixtures.mock_vps import clean_vps, mock_vps  # noqa: F401
