"""Makefile creation utilities."""

from pathlib import Path

import click


def create_makefile(project_path: Path) -> Path:
    """Create Makefile for the project.

    Args:
        project_path: Path to the project directory

    Returns:
        Path to the created Makefile
    """
    makefile_content = """# Makefile for bot development

.PHONY: help test lint format type-check dev validate install clean

help: ## Show help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \\033[36m%-15s\\033[0m %s\\n", $$1, $$2}'

test: ## Run tests
	@venv/bin/pytest

test-cov: ## Run tests with coverage
	@venv/bin/pytest --cov=. --cov-report=term --cov-report=html

lint: ## Run linter
	@venv/bin/ruff check .

lint-fix: ## Run linter and auto-fix issues
	@venv/bin/ruff check --fix .

format: ## Format code
	@venv/bin/ruff format .

format-check: ## Check code formatting
	@venv/bin/ruff format --check .

type-check: ## Type checking
	@venv/bin/mypy .

dev: ## Run bot in development mode
	@telegram-bot-stack dev

validate: ## Validate project configuration
	@telegram-bot-stack validate

install: ## Install dependencies
	@venv/bin/pip install -e .[dev]

clean: ## Clean cache files
	@rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage

ci: lint type-check test ## Run all CI checks
"""

    makefile_path = project_path / "Makefile"
    makefile_path.write_text(makefile_content)
    click.secho("  ✅ Created Makefile", fg="green")
    return makefile_path
