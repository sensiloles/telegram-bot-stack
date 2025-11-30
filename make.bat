@echo off
REM Cross-platform wrapper for scripts/tasks.py on Windows
REM Usage: make.bat <command>
REM
REM This allows Windows users to use "make test" syntax
REM instead of "python scripts/tasks.py test"
REM
REM Common commands:
REM   make.bat help      - Show all available commands
REM   make.bat dev       - Setup development environment (auto-creates venv)
REM   make.bat venv      - Create virtual environment only
REM   make.bat install   - Install package (creates venv if missing)
REM   make.bat test-fast - Quick tests during development
REM   make.bat test      - Full test suite
REM   make.bat lint      - Run linters
REM   make.bat format    - Auto-format code
REM   make.bat clean     - Clean build artifacts and venv
REM
REM Note: After 'clean', run 'make.bat dev' to recreate environment

python scripts\tasks.py %*
