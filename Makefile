.PHONY: help test test-fast test-unit test-integration test-deploy test-e2e test-all \
        coverage coverage-html coverage-unit build-mock-vps lint format clean install dev venv

help:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "📦 telegram-bot-stack - Development Commands"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "🧪 Testing Commands:"
	@echo "  make test              - Run all tests (fast + unit + integration)"
	@echo "  make test-fast         - ⚡ Quick tests only (unit + basic integration, ~1min)"
	@echo "  make test-unit         - Unit tests only (no Docker, ~30s)"
	@echo "  make test-integration  - Basic integration tests (config, docker templates)"
	@echo "  make test-deploy       - Deployment integration tests (requires Mock VPS)"
	@echo "  make test-e2e          - Full E2E tests (Mock VPS + Docker-in-Docker, ~5-30min)"
	@echo "  make test-all-versions - Run tests on Python 3.9-3.12 (via tox)"
	@echo ""
	@echo "📊 Coverage Commands:"
	@echo "  make coverage          - Run tests with coverage report (HTML + terminal)"
	@echo "  make coverage-html     - Generate HTML coverage report only"
	@echo "  make coverage-unit     - Coverage for unit tests only (fast)"
	@echo ""
	@echo "🐳 Docker Commands:"
	@echo "  make build-mock-vps    - Build Mock VPS Docker image (required for E2E tests)"
	@echo ""
	@echo "🔧 Development Commands:"
	@echo "  make venv              - Create virtual environment (Python 3.9+)"
	@echo "  make lint              - Run linters (ruff, mypy)"
	@echo "  make format            - Auto-format code with ruff"
	@echo "  make clean             - Clean build artifacts, cache, venv, and .env"
	@echo "  make install           - Install package in dev mode (creates venv if missing)"
	@echo "  make dev               - Setup complete development environment"
	@echo ""
	@echo "💡 Quick Start:"
	@echo "  make dev               # First time setup (auto-creates venv)"
	@echo "  make test-fast         # Quick validation during development"
	@echo "  make test              # Full validation before commit"
	@echo ""
	@echo "⚠️  After 'make clean', run 'make dev' to recreate environment"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Run all tests (unit + integration, skip E2E by default)
test:
	@echo "🧪 Running all tests (unit + integration)..."
	@echo "   E2E tests skipped (use 'make test-e2e' to run)"
	./venv/bin/pytest --no-cov -q

# Fast tests for development (unit + basic integration, no E2E)
test-fast:
	@echo "⚡ Running fast tests (unit + basic integration)..."
	@echo "   Excluding: E2E deployment tests (use 'make test-e2e' for those)"
	./venv/bin/pytest tests/unit/ tests/integration/bot/ \
		tests/integration/deployment/test_config.py \
		tests/integration/deployment/test_docker.py \
		tests/integration/deployment/test_cli.py \
		tests/integration/deployment/test_vps.py \
		--no-cov -v

# Unit tests only (fastest)
test-unit:
	@echo "🔬 Running unit tests..."
	./venv/bin/pytest tests/unit/ -v --no-cov

# Basic integration tests (no Mock VPS needed)
test-integration:
	@echo "🔗 Running basic integration tests..."
	./venv/bin/pytest tests/integration/bot/ \
		tests/integration/deployment/test_config.py \
		tests/integration/deployment/test_docker.py \
		tests/integration/deployment/test_cli.py \
		-v --no-cov

# Deployment E2E tests (requires Mock VPS)
test-deploy:
	@echo "🚀 Running deployment E2E tests..."
	@echo "⚠️  Requires Mock VPS image (run 'make build-mock-vps' first)"
	./venv/bin/pytest tests/e2e/deployment/ -v --no-cov --run-e2e

# Full E2E tests (slow, requires Mock VPS + Docker-in-Docker)
test-e2e:
	@echo "🎯 Running full E2E tests (this may take 5-30 minutes)..."
	@echo "⚠️  Requires Mock VPS image with Docker-in-Docker support"
	./venv/bin/pytest tests/e2e/ -v --no-cov --run-e2e

test-all-versions:
	./venv/bin/tox -p

test-py39:
	./venv/bin/tox -e py39

test-py310:
	./venv/bin/tox -e py310

test-py311:
	./venv/bin/tox -e py311

test-py312:
	./venv/bin/tox -e py312

# Coverage reports
coverage:
	@echo "📊 Running tests with coverage..."
	./venv/bin/pytest --cov=telegram_bot_stack --cov-report=html --cov-report=term-missing:skip-covered
	@echo ""
	@echo "✅ Coverage report generated!"
	@echo "   HTML: htmlcov/index.html"
	@echo "   Terminal: see above"

coverage-html:
	@echo "📊 Generating HTML coverage report..."
	./venv/bin/pytest --cov=telegram_bot_stack --cov-report=html --no-cov-on-fail -q
	@echo "✅ Coverage report: htmlcov/index.html"

coverage-unit:
	@echo "📊 Running unit tests with coverage (fast)..."
	./venv/bin/pytest tests/unit/ --cov=telegram_bot_stack --cov-report=term-missing:skip-covered

# Build Mock VPS Docker image for E2E tests
build-mock-vps:
	@echo "🐳 Building Mock VPS Docker image..."
	@echo "   This image is used for deployment integration tests"
	cd tests/integration/fixtures && docker build -t mock-vps:latest -f Dockerfile.mock-vps .
	@echo "✅ Mock VPS image built successfully!"
	@echo "   You can now run: make test-deploy or make test-e2e"

# Linting and formatting
lint:
	@echo "🔍 Running linters..."
	./venv/bin/ruff check .
	@echo ""
	@echo "🔍 Running type checker..."
	./venv/bin/mypy telegram_bot_stack/
	@echo "✅ Linting complete!"

format:
	@echo "✨ Formatting code..."
	./venv/bin/ruff format .
	./venv/bin/ruff check --fix .
	@echo "✅ Code formatted!"

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info htmlcov/ .coverage coverage.xml .tox/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "🧹 Cleaning database files..."
	find . -maxdepth 1 -type f -name "*.db" -delete
	find . -maxdepth 1 -type f -name "*.sqlite" -delete
	find . -maxdepth 1 -type f -name "*.sqlite3" -delete
	@echo "🧹 Cleaning virtual environment and config..."
	rm -rf venv/
	rm -f .env
	@echo "✅ Cleanup complete!"

# Create virtual environment
venv:
	@if [ -d "venv" ]; then \
		echo "✅ Virtual environment already exists"; \
	else \
		echo "🔧 Creating virtual environment..."; \
		python3 -m venv venv; \
		echo "⬆️  Upgrading pip..."; \
		./venv/bin/pip install --upgrade pip setuptools wheel; \
		echo "✅ Virtual environment created!"; \
		echo ""; \
		echo "💡 To activate:"; \
		echo "   source venv/bin/activate"; \
	fi

install: venv
	@echo "📦 Installing package in development mode..."
	@echo "   Installing with all dependencies (dev + database support)"
	@if [ -d "venv" ]; then \
		./venv/bin/pip install -e ".[dev]"; \
	else \
		pip install -e ".[dev]"; \
	fi
	@echo "✅ Package installed!"

dev: install
	@echo "🔧 Setting up development environment..."
	./venv/bin/pre-commit install
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "✅ Development environment ready!"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Run tests:         make test-fast"
	@echo "  2. Build Mock VPS:    make build-mock-vps  (for E2E tests)"
	@echo "  3. Run all tests:     make test"
	@echo "  4. Check coverage:    make coverage"
	@echo ""
	@echo "Development workflow:"
	@echo "  • make test-fast      - Quick validation during development"
	@echo "  • make format         - Auto-format before commit"
	@echo "  • make test           - Full validation before push"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
