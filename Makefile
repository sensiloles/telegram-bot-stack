.PHONY: help setup install test test-fast test-cov lint format type-check ci clean status pr-check pr-create pr-merge pr-merge-cleanup branch-check branch-create commit push issue-list issue-read flow dev-shell

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

branch-check: ## Check if current branch is not main (required before commits)
	@CURRENT_BRANCH=$$(git branch --show-current); \
	if [ "$$CURRENT_BRANCH" = "main" ]; then \
		echo "$(RED)Error: Cannot commit directly to main branch$(NC)"; \
		echo "$(YELLOW)Create a feature branch first:$(NC) make branch-create BRANCH=feature/name"; \
		exit 1; \
	else \
		echo "$(GREEN)✓ On branch: $$CURRENT_BRANCH$(NC)"; \
	fi

branch-create: ## Create feature branch (usage: make branch-create BRANCH=feature/name)
	@if [ -z "$(BRANCH)" ]; then \
		echo "$(RED)Error: Please specify branch name$(NC)"; \
		echo "Usage: make branch-create BRANCH=feature/name"; \
		echo "Examples: feature/add-storage, fix/auth-bug, docs/update-readme"; \
		exit 1; \
	fi
	@CURRENT_BRANCH=$$(git branch --show-current); \
	if [ "$$CURRENT_BRANCH" != "main" ]; then \
		echo "$(YELLOW)Warning: Not on main branch (current: $$CURRENT_BRANCH)$(NC)"; \
		echo "$(YELLOW)Creating branch from current branch...$(NC)"; \
	fi
	@git checkout -b $(BRANCH)
	@echo "$(GREEN)✓ Created and switched to branch: $(BRANCH)$(NC)"

commit: branch-check ## Commit changes with conventional commit format (usage: make commit MSG='type(scope): description')
	@if [ -z "$(MSG)" ]; then \
		echo "$(RED)Error: Please specify commit message$(NC)"; \
		echo "Usage: make commit MSG='type(scope): description'"; \
		echo "Examples:"; \
		echo "  make commit MSG='feat(storage): add Redis backend'"; \
		echo "  make commit MSG='fix(auth): resolve token validation'"; \
		echo "  make commit MSG='docs(readme): update quickstart'"; \
		exit 1; \
	fi
	@git add .
	@git commit -m "$(MSG)"
	@echo "$(GREEN)✓ Committed: $(MSG)$(NC)"

push: ## Push current branch to remote
	@CURRENT_BRANCH=$$(git branch --show-current); \
	if [ "$$CURRENT_BRANCH" = "main" ]; then \
		echo "$(RED)Error: Cannot push directly to main$(NC)"; \
		exit 1; \
	fi
	@git push -u origin $$(git branch --show-current)
	@echo "$(GREEN)✓ Pushed branch to remote$(NC)"

pr-create: ## Create Pull Request (usage: make pr-create TITLE='type(scope): description' [CLOSES=42])
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

pr-merge: ## Merge current branch's PR (auto-detects PR)
	@python3 .github/workflows/scripts/merge_pr.py

pr-merge-cleanup: ## Merge PR and cleanup branches (local + remote)
	@python3 .github/workflows/scripts/merge_pr.py --cleanup

issue-list: ## List open issues
	@python3 .github/workflows/scripts/read_issues.py --list --state open

issue-read: ## Read specific issue (usage: make issue-read ISSUE=4)
	@if [ -z "$(ISSUE)" ]; then \
		echo "$(RED)Error: Please specify issue number$(NC)"; \
		echo "Usage: make issue-read ISSUE=4"; \
		exit 1; \
	fi
	@python3 .github/workflows/scripts/read_issues.py $(ISSUE)

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

##@ GitHub Flow (Complete Workflow)

flow: ## Show GitHub Flow workflow steps
	@echo "$(GREEN)GitHub Flow Workflow:$(NC)"
	@echo ""
	@echo "1. $(BLUE)Check branch:$(NC) make branch-check"
	@echo "2. $(BLUE)Create branch:$(NC) make branch-create BRANCH=feature/name"
	@echo "3. $(BLUE)Make changes:$(NC) edit files..."
	@echo "4. $(BLUE)Commit:$(NC) make commit MSG='type(scope): description'"
	@echo "5. $(BLUE)Push:$(NC) make push"
	@echo "6. $(BLUE)Create PR:$(NC) make pr-create TITLE='type(scope): description'"
	@echo "7. $(BLUE)Merge:$(NC) make pr-merge-cleanup"
	@echo ""
	@echo "$(YELLOW)Conventional Commits:$(NC)"
	@echo "  feat: → MINOR version bump"
	@echo "  fix: → PATCH version bump"
	@echo "  feat! or BREAKING CHANGE: → MAJOR version bump"
	@echo "  docs:, chore:, test:, refactor: → No version bump"

##@ Shortcuts

t: test ## Shortcut for test
tc: test-cov ## Shortcut for test-cov
tf: test-fast ## Shortcut for test-fast
l: lint ## Shortcut for lint
f: format ## Shortcut for format
s: status ## Shortcut for status
