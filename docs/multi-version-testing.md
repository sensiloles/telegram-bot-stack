# Multi-Version Testing with Tox

This guide explains how to test the package locally on multiple Python versions (3.9, 3.10, 3.11, 3.12) using **tox**.

## Prerequisites

### 1. Install Multiple Python Versions

You need to have all Python versions installed on your system. The easiest way is using **pyenv**:

#### macOS/Linux:

```bash
# Install pyenv
curl https://pyenv.run | bash

# Or via Homebrew (macOS)
brew install pyenv

# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"

# Install Python versions
pyenv install 3.9.21
pyenv install 3.10.17
pyenv install 3.11.11
pyenv install 3.12.8

# Make all versions available globally
pyenv global 3.12.8 3.11.11 3.10.17 3.9.21

# Verify installations
python3.9 --version
python3.10 --version
python3.11 --version
python3.12 --version
```

#### Windows:

Download and install Python versions from [python.org](https://www.python.org/downloads/):

- Python 3.9.x
- Python 3.10.x
- Python 3.11.x
- Python 3.12.x

Make sure to check "Add Python to PATH" during installation.

### 2. Install Tox

```bash
# If you installed dev dependencies, tox is already available:
pip install -e ".[dev]"

# Or install tox separately:
pip install tox
```

## Running Tests

### Test on All Python Versions (Parallel)

Run tests on all Python versions simultaneously:

```bash
make test-all-versions
# or
tox -p auto
```

This will:

- Run tests in parallel on Python 3.9, 3.10, 3.11, and 3.12
- Skip versions not installed on your system
- Show combined results

### Test on Specific Python Version

```bash
# Python 3.9
make test-py39
# or
tox -e py39

# Python 3.10
make test-py310
# or
tox -e py310

# Python 3.11
make test-py311
# or
tox -e py311

# Python 3.12
make test-py312
# or
tox -e py312
```

### Run Linting and Type Checking

```bash
# Linting only
tox -e lint

# Format check only
tox -e format

# Type checking only
tox -e type

# All checks at once
tox -e all
```

## Tox Configuration

The `tox.ini` file defines the testing environments:

- **py39, py310, py311, py312**: Test on each Python version
- **lint**: Run ruff linter
- **format**: Check code formatting
- **type**: Run mypy type checker
- **all**: Run all checks (lint + format + type + tests)

## Troubleshooting

### "Python version not found"

If tox can't find a Python version:

1. **Check if installed:**

   ```bash
   python3.9 --version
   ```

2. **Install missing version with pyenv:**

   ```bash
   pyenv install 3.9.21
   pyenv rehash
   ```

3. **Add to pyenv global:**
   ```bash
   pyenv global 3.12.8 3.11.11 3.10.17 3.9.21
   ```

### Skip Missing Interpreters

Tox is configured with `skip_missing_interpreters = True`, so it will skip versions you don't have installed without failing.

### Clean Tox Environments

If you encounter issues, clean and rebuild:

```bash
# Remove all tox environments
rm -rf .tox

# Rebuild and run
tox -p auto
```

## CI/CD Comparison

**Local (tox):**

```bash
make test-all-versions
```

**GitHub Actions (automatic on PR):**

- Runs on push to any branch
- Tests all Python versions in parallel
- Same test commands as tox

This ensures your local tests match CI behavior exactly.

## Quick Reference

| Command                  | Description                            |
| ------------------------ | -------------------------------------- |
| `make test-all-versions` | Test on all Python versions (parallel) |
| `make test-py39`         | Test on Python 3.9 only                |
| `make test-py310`        | Test on Python 3.10 only               |
| `make test-py311`        | Test on Python 3.11 only               |
| `make test-py312`        | Test on Python 3.12 only               |
| `tox -e lint`            | Run linter                             |
| `tox -e type`            | Run type checker                       |
| `tox -e all`             | Run all checks                         |
| `tox -l`                 | List all available environments        |
| `rm -rf .tox`            | Clean tox cache                        |

## Integration with Workflow

```bash
# Before creating a PR:
1. make test-all-versions  # Test on all Python versions
2. make lint               # Check code style
3. make type-check         # Check types
4. git add .
5. git commit -m "feat: add feature"
6. git push
7. make pr-create TITLE="feat: add feature" CLOSES=123

# CI will automatically run the same checks
```

## Performance Tips

1. **Parallel execution**: Use `-p auto` flag for faster testing
2. **Skip coverage**: Add `-- --no-cov` to speed up tests
3. **Re-run failed only**: Use `tox -e py39 --` to re-run specific environment
4. **Cache dependencies**: Tox caches environments, subsequent runs are faster

## Example Output

```bash
$ make test-all-versions
Running tests on all Python versions...
✔ py39: OK (12.34s)
✔ py310: OK (11.87s)
✔ py311: OK (12.01s)
✔ py312: OK (11.98s)
__________________________________ summary __________________________________
  py39: commands succeeded
  py310: commands succeeded
  py311: commands succeeded
  py312: commands succeeded
  congratulations :)
```
