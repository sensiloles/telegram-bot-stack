# VSCode Configuration

This directory contains VSCode workspace settings optimized for `telegram-bot-stack` development.

## 📁 Files

- **`settings.json`** - Active workspace settings (Ruff + Mypy + Pylance)
- **`settings.recommended.json`** - Same as settings.json (for easy restore)
- **`extensions.json`** - Recommended VSCode extensions
- **`launch.json`** - Debug configurations for bots and tests

## 🎯 What's Configured

### Code Quality Tools

✅ **Ruff** - Linter and formatter (configured in `pyproject.toml`)

- Auto-format on save
- Import organization
- Error highlighting

✅ **Mypy** - Type checker (configured in `pyproject.toml`)

- Uses venv executable (`./venv/bin/dmypy`)
- Workspace-level type checking
- Matches CI configuration

✅ **Pylance** - IntelliSense and navigation

- Type checking disabled (deferred to mypy)
- Auto-import completions
- Inline type hints

### File Associations

- `*.template` → Jinja (for CLI templates)
- `Dockerfile` → Dockerfile syntax
- `Makefile` → Makefile syntax

### Debug Configurations

1. **Python: Current File** - Debug active Python file
2. **🤖 Example: Echo Bot** - Debug echo bot example
3. **🤖 Example: Counter Bot** - Debug counter bot example
4. **🤖 Example: Quit Smoking Bot** - Debug quit smoking bot
5. **🧪 Tests: All** - Debug all tests
6. **🧪 Tests: Current File** - Debug current test file

All configurations use `./venv/bin/python3` and load `.env` file.

## 🚀 Quick Start

### 1. Install Recommended Extensions

VSCode will prompt you to install recommended extensions on first open.

Or install manually:

```bash
# Open command palette (Cmd+Shift+P / Ctrl+Shift+P)
# Type: Extensions: Show Recommended Extensions
# Click "Install Workspace Recommended Extensions"
```

### 2. Reload Window

After installing extensions:

```bash
# Cmd+Shift+P / Ctrl+Shift+P → Developer: Reload Window
```

### 3. Verify Setup

Check that:

- ✅ Python interpreter shows `./venv/bin/python3` in bottom bar
- ✅ Ruff is formatting on save
- ✅ Mypy shows type errors (if any)
- ✅ Auto-imports work

## 🔧 Customization

To modify settings for your needs, edit `settings.json`.

To restore recommended settings:

```bash
cp .vscode/settings.recommended.json .vscode/settings.json
```

## 📋 Settings Summary

| Setting            | Value                | Why                               |
| ------------------ | -------------------- | --------------------------------- |
| Python interpreter | `./venv/bin/python3` | Isolation from system             |
| Formatter          | Ruff                 | Fast, modern Python formatter     |
| Type checker       | Mypy                 | Matches CI, strict checking       |
| Linter             | Ruff                 | Replaces flake8, isort, pyupgrade |
| Autocomplete       | Pylance              | Fast, accurate completions        |
| Format on save     | ✅                   | Consistent code style             |

## 🐛 Troubleshooting

### Mypy not found error

If you see "dmypy executable not found":

1. Ensure venv is created: `make dev`
2. Reload VSCode window
3. Check `.vscode/settings.json` has correct path

### Ruff not formatting

1. Ensure Ruff extension is installed
2. Check Python file is not in excluded folders
3. Try manual format: `Cmd+Shift+P → Format Document`

### Wrong Python interpreter

1. Click Python version in bottom bar
2. Select `./venv/bin/python3`
3. Reload window

## 🔍 Import Resolution

Project uses dynamic imports from external directories. These are configured via:

**1. VSCode Settings** (`.vscode/settings.json`):

```json
"python.analysis.extraPaths": [
  ".project-graph",
  ".github/workflows/scripts"
]
```

**2. Pyright Config** (`pyrightconfig.json`):

- Configures import resolution for scripts directory
- Handles `mcp` package (Python 3.10+ only)
- Resolves `utils.graph_utils` from `.project-graph`
- Resolves `github_helper` from `.github/workflows/scripts`

**No `# type: ignore` needed!** ✅

## 📚 See Also

- [pyproject.toml](../pyproject.toml) - Tool configurations
- [pyrightconfig.json](../pyrightconfig.json) - Import resolution config
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Development guidelines
- [README.md](../README.md) - Project documentation
