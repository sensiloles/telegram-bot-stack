#!/bin/bash
# Quick script to run integration tests
#
# Usage:
#   ./run_integration_tests.sh              # Run all tests
#   ./run_integration_tests.sh deployment   # Run deployment tests only
#   ./run_integration_tests.sh requirements # Run requirements tests only
#   ./run_integration_tests.sh full-flow    # Run full flow tests only

set -e

echo "🚀 Starting Integration Tests..."
echo ""

# Check if Docker is running
if ! docker ps >/dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "   Please start Docker and try again"
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Check if Python dependencies are installed
if ! python -c "import pytest" >/dev/null 2>&1; then
    echo "❌ Error: pytest not installed"
    echo "   Run: pip install -e '.[dev]'"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Run tests
echo "Running integration tests..."
echo ""

# Parse command line arguments
TEST_SUITE="${1:-all}"

case "$TEST_SUITE" in
    "all")
        echo "Running all integration tests..."
        TEST_PATH="tests/integration/"
        ;;
    "deployment")
        echo "Running deployment tests only..."
        TEST_PATH="tests/integration/test_deployment.py"
        ;;
    "requirements")
        echo "Running VPS requirements tests only..."
        TEST_PATH="tests/integration/test_vps_requirements.py"
        ;;
    "full-flow")
        echo "Running full flow tests only..."
        TEST_PATH="tests/integration/test_full_flow.py"
        ;;
    *)
        echo "Running custom test path: $TEST_SUITE"
        TEST_PATH="$TEST_SUITE"
        ;;
esac

echo ""

# Run with coverage
pytest "$TEST_PATH" \
    -v \
    --tb=short \
    --cov=telegram_bot_stack \
    --cov-report=term \
    --cov-report=html \
    -m "not slow"

# Cleanup
echo ""
echo "Cleaning up Docker resources..."
docker compose -f tests/integration/fixtures/docker-compose.mock-vps.yml down -v 2>/dev/null || true

echo ""
echo "✅ Integration tests complete!"
echo "   Coverage report: htmlcov/index.html"
echo ""
echo "💡 Test suites available:"
echo "   ./run_integration_tests.sh all          # All tests"
echo "   ./run_integration_tests.sh deployment   # Deployment tests"
echo "   ./run_integration_tests.sh requirements # Requirements tests"
echo "   ./run_integration_tests.sh full-flow    # Full flow tests"
