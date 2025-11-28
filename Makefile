.PHONY: help test test-unit test-integration test-all coverage lint format clean install dev

help:
	@echo "Available commands:"
	@echo "  make test              - Run all tests (unit + integration)"
	@echo "  make test-unit         - Run unit tests only (fast, no Docker)"
	@echo "  make test-integration  - Run integration tests (requires Docker)"
	@echo "  make test-all-versions - Run tests on Python 3.9-3.12 (via tox)"
	@echo "  make coverage          - Run tests with coverage report"
	@echo "  make lint              - Run linters (ruff, mypy)"
	@echo "  make format            - Auto-format code"
	@echo "  make clean             - Clean build artifacts"
	@echo "  make install           - Install package in dev mode"
	@echo "  make dev               - Setup development environment"

test:
	pytest

test-unit:
	pytest tests/unit/ -v

test-integration:
	@echo "Running integration tests (requires Docker)..."
	@./tests/integration/run_integration_tests.sh

test-all-versions:
	tox -p

test-py39:
	tox -e py39

test-py310:
	tox -e py310

test-py311:
	tox -e py311

test-py312:
	tox -e py312

coverage:
	pytest --cov=telegram_bot_stack --cov-report=html --cov-report=term

lint:
	ruff check .
	mypy telegram_bot_stack/

format:
	ruff format .
	ruff check --fix .

clean:
	rm -rf build/ dist/ *.egg-info htmlcov/ .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

install:
	pip install -e ".[dev]"

dev: install
	pre-commit install
	@echo "Development environment ready!"
