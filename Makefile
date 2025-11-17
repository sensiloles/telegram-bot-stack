.PHONY: help setup install test test-fast test-cov lint format type-check ci clean status pr-check pr-create issue-list dev-shell

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ General

help: ## Show this help message
	@echo '$(GREEN)telegram-bot-stack - Development Commands$(NC)'
	@echo ''
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make $(YELLOW)<target>$(NC)\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(GREEN)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Setup & Installation

setup: ## Complete development environment setup
	@echo "$(GREEN)Setting up development environment...$(NC)"
	python3 -m pip install --upgrade pip
	pip install -e ".[dev,github-actions]"
	pre-commit install
	@echo "$(GREEN)✓ Setup complete!$(NC)"

install: ## Install package in development mode
	@echo "$(GREEN)Installing package...$(NC)"
	pip install -e .
	@echo "$(GREEN)✓ Package installed!$(NC)"

install-dev: ## Install with all development dependencies
	@echo "$(GREEN)Installing with dev dependencies...$(NC)"
	pip install -e ".[dev,github-actions,release]"
	@echo "$(GREEN)✓ Dev dependencies installed!$(NC)"

##@ Testing

test: ## Run all tests
	@echo "$(GREEN)Running all tests...$(NC)"
	pytest

test-fast: ## Run tests without coverage (faster)
	@echo "$(GREEN)Running fast tests...$(NC)"
	pytest -v --no-cov

test-cov: ## Run tests with coverage report
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	pytest --cov=telegram_bot_stack --cov-report=term --cov-report=html
	@echo "$(YELLOW)Coverage report: htmlcov/index.html$(NC)"

test-watch: ## Run tests in watch mode (requires pytest-watch)
	@echo "$(GREEN)Running tests in watch mode...$(NC)"
	ptw -- --no-cov

test-unit: ## Run only unit tests
	@echo "$(GREEN)Running unit tests...$(NC)"
	pytest tests/core/ -v

test-integration: ## Run only integration tests
	@echo "$(GREEN)Running integration tests...$(NC)"
	pytest tests/integration/ -v

##@ Code Quality

lint: ## Run linter (ruff)
	@echo "$(GREEN)Running linter...$(NC)"
	ruff check .

lint-fix: ## Run linter and auto-fix issues
	@echo "$(GREEN)Running linter with auto-fix...$(NC)"
	ruff check --fix .

format: ## Format code with ruff
	@echo "$(GREEN)Formatting code...$(NC)"
	ruff format .

format-check: ## Check code formatting without changes
	@echo "$(GREEN)Checking code format...$(NC)"
	ruff format --check .

type-check: ## Run type checker (mypy)
	@echo "$(GREEN)Running type checker...$(NC)"
	mypy telegram_bot_stack

pre-commit: ## Run all pre-commit hooks
	@echo "$(GREEN)Running pre-commit hooks...$(NC)"
	pre-commit run --all-files

##@ CI/CD

ci: ## Run all CI checks locally (lint, type-check, test)
	@echo "$(GREEN)Running CI checks locally...$(NC)"
	@make lint
	@make type-check
	@make test
	@echo "$(GREEN)✓ All CI checks passed!$(NC)"

ci-check: ## Check CI status for current branch
	@echo "$(GREEN)Checking CI status...$(NC)"
	@python3 .github/workflows/scripts/check_ci.py --branch $$(git branch --show-current)

pr-check: ## Check CI status for a PR (usage: make pr-check PR=5)
	@if [ -z "$(PR)" ]; then \
		echo "$(RED)Error: Please specify PR number$(NC)"; \
		echo "Usage: make pr-check PR=5"; \
		exit 1; \
	fi
	@echo "$(GREEN)Checking PR #$(PR) status...$(NC)"
	@python3 .github/workflows/scripts/check_ci.py --pr $(PR)

##@ Git & GitHub

status: ## Show project status (open issues, current phase)
	@echo "$(GREEN)Project Status:$(NC)"
	@echo ""
	@python3 .github/workflows/scripts/read_issues.py --list --state open 2>/dev/null || echo "$(YELLOW)Install PyGithub to see issues: pip install PyGithub$(NC)"
	@echo ""
	@echo "$(GREEN)Current branch:$(NC) $$(git branch --show-current)"
	@echo "$(GREEN)Last commit:$(NC) $$(git log -1 --oneline)"

issue-list: ## List open issues
	@python3 .github/workflows/scripts/read_issues.py --list --state open

issue-read: ## Read specific issue (usage: make issue-read ISSUE=4)
	@if [ -z "$(ISSUE)" ]; then \
		echo "$(RED)Error: Please specify issue number$(NC)"; \
		echo "Usage: make issue-read ISSUE=4"; \
		exit 1; \
	fi
	@python3 .github/workflows/scripts/read_issues.py $(ISSUE)

pr-create: ## Create Pull Request (auto-detects branch, validates title)
	@if [ -z "$(TITLE)" ]; then \
		echo "$(RED)Error: Please specify PR title$(NC)"; \
		echo "Usage: make pr-create TITLE='feat(scope): description' [CLOSES=42]"; \
		exit 1; \
	fi
	@if [ ! -z "$(CLOSES)" ]; then \
		python3 .github/workflows/scripts/create_pr.py --title "$(TITLE)" --closes $(CLOSES); \
	else \
		python3 .github/workflows/scripts/create_pr.py --title "$(TITLE)"; \
	fi

##@ Development

dev-shell: ## Start development Python shell with imports
	@echo "$(GREEN)Starting dev shell...$(NC)"
	@python3 -i -c "from telegram_bot_stack import *; print('✓ telegram_bot_stack imported')"

clean: ## Clean build artifacts and cache files
	@echo "$(GREEN)Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Cleaned!$(NC)"

clean-all: clean ## Clean everything including venv
	@echo "$(YELLOW)Removing virtual environment...$(NC)"
	rm -rf venv/
	@echo "$(GREEN)✓ Everything cleaned!$(NC)"

##@ Documentation

docs-serve: ## Serve documentation locally (if using mkdocs)
	@echo "$(YELLOW)Documentation server not configured yet$(NC)"

##@ Shortcuts

t: test ## Shortcut for test
tc: test-cov ## Shortcut for test-cov
tf: test-fast ## Shortcut for test-fast
l: lint ## Shortcut for lint
f: format ## Shortcut for format
s: status ## Shortcut for status
