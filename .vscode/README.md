# VSCode Configuration

This directory contains VSCode workspace settings.

## Files

- **`settings.json`** - Current workspace settings (basic Ruff setup)
- **`settings.recommended.json`** - Recommended settings with **type checking enabled**
- **`extensions.json`** - Recommended extensions
- **`launch.json`** - Debug configurations

## Enable Type Checking

To see type errors in real-time (like in CI), **copy** `settings.recommended.json` to `settings.json`:

```bash
cp .vscode/settings.recommended.json .vscode/settings.json
```

**What you get:**
- ✅ Real-time type error highlighting
- ✅ Better autocomplete
- ✅ Inline type hints
- ✅ Catch bugs before CI

**Requirements:**
- Install **Pylance** extension: `ms-python.vscode-pylance`
- Restart VSCode

## Why Two Files?

**`settings.json`** (current):
- Basic setup with Ruff
- Works out of the box
- No strict type checking

**`settings.recommended.json`** (recommended):
- Full type checking with Pylance
- Shows all 44 type errors (from Issue #30)
- Better developer experience
- Same as CI checks

## See Also

- Issue #30: Type checking errors and fixes
- `pyproject.toml`: mypy configuration
