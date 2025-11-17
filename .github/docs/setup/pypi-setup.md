# PyPI Publication Setup

This guide explains how to configure PyPI publication for the `telegram-bot-stack` package.

## Prerequisites

1. **PyPI Account:** Register at https://pypi.org/
2. **Test PyPI Account:** Register at https://test.pypi.org/ (optional, for testing)
3. **GitHub Repository:** Admin access to configure secrets

## Step 1: Create PyPI API Tokens

### For Test PyPI (Optional)

1. Go to https://test.pypi.org/manage/account/token/
2. Click "Add API token"
3. **Token name:** `telegram-bot-stack-github-actions`
4. **Scope:** Project: `telegram-bot-stack` (or "Entire account" for first publication)
5. **Copy the token** (starts with `pypi-...`)
6. ⚠️ **Save it immediately** - you won't see it again!

### For Production PyPI

1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. **Token name:** `telegram-bot-stack-github-actions`
4. **Scope:** Project: `telegram-bot-stack` (or "Entire account" for first publication)
5. **Copy the token** (starts with `pypi-...`)
6. ⚠️ **Save it immediately** - you won't see it again!

## Step 2: Configure GitHub Secrets

### Add Secrets to Repository

1. Go to repository: https://github.com/sensiloles/telegram-bot-stack
2. Navigate to **Settings → Secrets and variables → Actions**
3. Click **"New repository secret"**

### Create Test PyPI Secret (Optional)

- **Name:** `TEST_PYPI_API_TOKEN`
- **Value:** `pypi-...` (paste the Test PyPI token)
- Click **"Add secret"**

### Create Production PyPI Secret

- **Name:** `PYPI_API_TOKEN`
- **Value:** `pypi-...` (paste the Production PyPI token)
- Click **"Add secret"**

## Step 3: Configure GitHub Environments (Optional)

For additional security, configure deployment environments:

### Create Test PyPI Environment

1. Go to **Settings → Environments**
2. Click **"New environment"**
3. **Name:** `testpypi`
4. **Deployment protection rules:**
   - No protection (for testing)
5. **Environment secrets:**
   - Add `TEST_PYPI_API_TOKEN` here (optional, overrides repository secret)

### Create PyPI Environment

1. Click **"New environment"**
2. **Name:** `pypi`
3. **Deployment protection rules:**
   - ✅ **Required reviewers:** Select yourself or team members
   - ⏱️ **Wait timer:** 0 minutes (or add delay)
4. **Environment secrets:**
   - Add `PYPI_API_TOKEN` here (optional, overrides repository secret)

## Step 4: Test Publication

### Option 1: Manual Workflow Dispatch (Recommended for first time)

1. Go to **Actions → Publish to PyPI**
2. Click **"Run workflow"**
3. Select branch: `main`
4. **Publish to:** `testpypi`
5. Click **"Run workflow"**
6. Monitor the workflow execution
7. If successful, test installation:

```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate  # or: test_env\Scripts\activate on Windows

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  telegram-bot-stack

# Test import
python -c "from telegram_bot_stack import TelegramBotBase; print('✅ Success!')"

# Cleanup
deactivate
rm -rf test_env
```

### Option 2: Automatic on Release

The workflow automatically publishes to PyPI when a new release is created:

1. Create a release using semantic-release (automatic) or manually
2. Workflow triggers automatically
3. Package is published to production PyPI

## Step 5: Verify Publication

### Check Test PyPI

- Package page: https://test.pypi.org/project/telegram-bot-stack/
- Installation: `pip install --index-url https://test.pypi.org/simple/ telegram-bot-stack`

### Check Production PyPI

- Package page: https://pypi.org/project/telegram-bot-stack/
- Installation: `pip install telegram-bot-stack`

## Manual Publication (Without GitHub Actions)

If you prefer manual control:

### Prerequisites

```bash
pip install build twine
```

### Build Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build
python -m build

# Verify
twine check dist/*
```

### Upload to Test PyPI

```bash
# Upload
twine upload --repository testpypi dist/*

# You'll be prompted for:
# Username: __token__
# Password: pypi-... (your token)

# Or use .pypirc (see below)
```

### Upload to Production PyPI

```bash
# Upload
twine upload dist/*

# You'll be prompted for:
# Username: __token__
# Password: pypi-... (your token)
```

### Configure .pypirc (Optional)

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-production-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-token-here
```

**⚠️ Security Warning:** This file contains sensitive tokens. Set proper permissions:

```bash
chmod 600 ~/.pypirc
```

## Troubleshooting

### Error: "Invalid or non-existent authentication information"

- Check token is correct (starts with `pypi-`)
- Verify token hasn't expired
- Ensure token has correct scope (project or account)

### Error: "File already exists"

- Package version already published to PyPI
- PyPI doesn't allow re-uploading same version
- Bump version in `pyproject.toml` and rebuild

### Error: "Project does not exist"

- For first publication, use token with "Entire account" scope
- After first publication, create project-specific token

### Workflow Fails on GitHub Actions

- Verify secrets are configured correctly
- Check secret names match workflow file (`PYPI_API_TOKEN`, `TEST_PYPI_API_TOKEN`)
- Ensure environment names match (if using environments)

## Security Best Practices

1. **Use Project-Scoped Tokens:** After first publication, create new tokens scoped to the project
2. **Rotate Tokens Regularly:** Update tokens every 6-12 months
3. **Use Environment Protection:** Require manual approval for production deployments
4. **Monitor Publications:** Enable PyPI email notifications
5. **Review Workflow Logs:** Check for any security warnings

## Resources

- [PyPI Publishing Guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [GitHub Actions for PyPI](https://github.com/marketplace/actions/pypi-publish)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Python Packaging Guide](https://packaging.python.org/)

## Next Steps

After successful publication:

1. ✅ Update README.md with PyPI badge
2. ✅ Verify package installation from PyPI
3. ✅ Test example bots with installed package
4. ✅ Announce release

---

**Need Help?** Open an issue at https://github.com/sensiloles/telegram-bot-stack/issues
