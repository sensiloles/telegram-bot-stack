@echo off
REM Cross-platform wrapper for scripts/tasks.py on Windows
REM Usage: make.bat <command>
REM
REM This allows Windows users to use "make test" syntax
REM instead of "python scripts/tasks.py test"

python scripts\tasks.py %*
