"""Pytest configuration for E2E tests.

E2E tests require Mock VPS Docker container and test full deployment workflows.
These tests are slower but provide comprehensive coverage of deployment features.
"""

# Import common fixtures from integration tests
import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import integration test fixtures
from tests.integration.conftest import *  # noqa: F401, F403
from tests.integration.fixtures.mock_vps import *  # noqa: F401, F403
