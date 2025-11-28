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

# Start Docker monitoring in background
echo "Starting Docker monitoring..."
(
    while true; do
        sleep 30
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🐳 Docker Status at $(date '+%H:%M:%S')"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}" 2>/dev/null || true

        # Show recent logs from mock VPS if it exists
        CONTAINER=$(docker ps --filter "name=mock-vps" --format "{{.Names}}" 2>/dev/null | head -1)
        if [ -n "$CONTAINER" ]; then
            echo ""
            echo "📋 Recent Mock VPS logs:"
            docker logs --tail 5 "$CONTAINER" 2>&1 || true
        fi
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
    done
) &
MONITOR_PID=$!

# Cleanup function
cleanup_monitor() {
    if [ -n "$MONITOR_PID" ]; then
        kill $MONITOR_PID 2>/dev/null || true
    fi
}
trap cleanup_monitor EXIT

echo "🚀 Starting integration tests at $(date '+%Y-%m-%d %H:%M:%S')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run with coverage and parallel execution
pytest "$TEST_PATH" \
    -v \
    -n auto \
    --tb=short \
    --log-cli-level=INFO \
    --log-cli-format="%(asctime)s [%(levelname)s] %(message)s" \
    --log-cli-date-format="%H:%M:%S" \
    --cov=telegram_bot_stack \
    --cov-report=term \
    --cov-report=html \
    -m "not slow"

TEST_EXIT_CODE=$?

# Stop monitoring
cleanup_monitor

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ Tests completed at $(date '+%Y-%m-%d %H:%M:%S')"
else
    echo "❌ Tests failed at $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    echo "🔍 Docker container logs:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    for container in $(docker ps -a --format "{{.Names}}" 2>/dev/null); do
        echo ""
        echo "📋 Container: $container"
        docker logs --tail 50 "$container" 2>&1 || true
    done
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Cleanup
echo "🧹 Cleaning up Docker resources..."
docker compose -f tests/integration/fixtures/docker-compose.mock-vps.yml down -v 2>/dev/null || true

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Integration tests complete!"
    echo "   Coverage report: htmlcov/index.html"
else
    echo ""
    echo "❌ Integration tests failed!"
    echo "   Exit code: $TEST_EXIT_CODE"
fi

echo ""
echo "💡 Test suites available:"
echo "   ./run_integration_tests.sh all          # All tests"
echo "   ./run_integration_tests.sh deployment   # Deployment tests"
echo "   ./run_integration_tests.sh requirements # Requirements tests"
echo "   ./run_integration_tests.sh full-flow    # Full flow tests"

exit $TEST_EXIT_CODE
