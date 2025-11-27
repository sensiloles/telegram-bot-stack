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

- ✅ Real-time type error highlighting (mypy - same as CI)
- ✅ Better autocomplete (Pylance)
- ✅ Inline type hints (Pylance)
- ✅ Catch bugs before CI (mypy shows the same errors)
- ✅ Single source of truth for types (mypy everywhere)

**Requirements:**

- Install **Pylance** extension: `ms-python.vscode-pylance` (autocomplete)
- Install **Mypy** extension: `matangover.mypy` (type checking)
- Restart VSCode

## Why Two Files?

**`settings.json`** (current):

- Basic setup with Ruff
- Works out of the box
- Type checking with mypy (matches CI)

**`settings.recommended.json`** (recommended):

- Full setup with Ruff + Pylance + Mypy
- **Mypy** - single source of type checking (matches CI/pre-commit)
- **Pylance** - autocomplete, navigation, hints (no type checking)
- Single source of truth for types: mypy everywhere (IDE and CI)
- Better developer experience without conflicts

## See Also

- Issue #30: Type checking errors and fixes
- `pyproject.toml`: mypy configuration
