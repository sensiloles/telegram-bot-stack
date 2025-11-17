# Private Installation Guide

Различные способы установки `telegram-bot-stack` без публикации на публичный PyPI.

## 🔐 Option 1: GitHub Packages (Recommended)

### Setup

1. **Configure package for GitHub Packages:**

Add to `pyproject.toml`:

```toml
[project.urls]
Repository = "https://github.com/sensiloles/telegram-bot-stack"

[tool.setuptools]
packages = ["telegram_bot_stack"]
```

2. **Publish to GitHub Packages:**

```bash
# Build package
python -m build

# Publish (requires GitHub token)
export GITHUB_TOKEN="your_github_token"
twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
```

Or use GitHub Actions workflow (`.github/workflows/publish-github-packages.yml`)

### Installation

Users need to configure pip to use GitHub Packages:

**Option A: Using pip with GitHub token:**

```bash
pip install telegram-bot-stack \
    --index-url https://<GITHUB_TOKEN>@github.com/sensiloles/telegram-bot-stack
```

**Option B: Configure pip permanently:**

Create `~/.pip/pip.conf` (Linux/Mac) or `%APPDATA%\pip\pip.ini` (Windows):

```ini
[global]
extra-index-url = https://<GITHUB_TOKEN>@github.com/sensiloles/telegram-bot-stack
```

Then install:

```bash
pip install telegram-bot-stack
```

---

## 📦 Option 2: Install Directly from Git (Simplest)

**No packaging needed!** Users install directly from your GitHub repository.

### Public Repository

```bash
# Install from main branch
pip install git+https://github.com/sensiloles/telegram-bot-stack.git

# Install specific version/tag
pip install git+https://github.com/sensiloles/telegram-bot-stack.git@v0.1.0

# Install specific branch
pip install git+https://github.com/sensiloles/telegram-bot-stack.git@develop

# Install specific commit
pip install git+https://github.com/sensiloles/telegram-bot-stack.git@abc123def
```

### Private Repository

For private repos, use SSH or token:

```bash
# Using SSH (recommended)
pip install git+ssh://git@github.com/sensiloles/telegram-bot-stack.git

# Using HTTPS with token
pip install git+https://<GITHUB_TOKEN>@github.com/sensiloles/telegram-bot-stack.git
```

### In requirements.txt

```txt
# Public repo
telegram-bot-stack @ git+https://github.com/sensiloles/telegram-bot-stack.git

# Private repo with SSH
telegram-bot-stack @ git+ssh://git@github.com/sensiloles/telegram-bot-stack.git

# Specific version
telegram-bot-stack @ git+https://github.com/sensiloles/telegram-bot-stack.git@v0.1.0
```

### Pros & Cons

✅ **Pros:**

- Simplest setup (no publishing needed)
- Works immediately
- Version control via git tags
- No extra infrastructure

❌ **Cons:**

- Slower installation (clones entire repo)
- Requires Git to be installed
- No package metadata on PyPI

---

## 🏢 Option 3: Self-Hosted PyPI Server

Run your own private PyPI server.

### Option 3A: devpi

```bash
# Install devpi
pip install devpi-server devpi-web devpi-client

# Start server
devpi-server --start --init

# Create index
devpi use http://localhost:3141
devpi login root --password=''
devpi index -c myindex bases=root/pypi

# Upload package
devpi upload
```

**Installation:**

```bash
pip install --index-url http://localhost:3141/root/myindex telegram-bot-stack
```

### Option 3B: pypiserver

```bash
# Install
pip install pypiserver

# Run server
mkdir ~/packages
pypiserver run -p 8080 ~/packages

# Upload package
twine upload --repository-url http://localhost:8080 dist/*
```

**Installation:**

```bash
pip install --index-url http://localhost:8080 telegram-bot-stack
```

---

## ☁️ Option 4: Cloud Package Registries

### GitLab Package Registry

If you mirror to GitLab:

```bash
# Configure .gitlab-ci.yml
stages:
  - publish

publish:
  stage: publish
  script:
    - pip install twine build
    - python -m build
    - TWINE_PASSWORD=${CI_JOB_TOKEN} TWINE_USERNAME=gitlab-ci-token
      twine upload --repository-url ${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/packages/pypi dist/*
```

### AWS CodeArtifact

```bash
# Configure
aws codeartifact login --tool pip --domain my-domain --repository my-repo

# Publish
twine upload --repository codeartifact dist/*

# Install
pip install telegram-bot-stack
```

### Azure Artifacts

```bash
# Configure
pip install keyring artifacts-keyring

# Publish via Azure Pipelines

# Install
pip install telegram-bot-stack --index-url https://pkgs.dev.azure.com/...
```

---

## 🎯 Recommended Approach

### For Current Situation (Public GitHub Repo):

**Best option: Direct Git Installation**

No setup needed, works immediately:

```bash
pip install git+https://github.com/sensiloles/telegram-bot-stack.git
```

**Update your README.md:**

````markdown
## Installation

```bash
# Install latest version from GitHub
pip install git+https://github.com/sensiloles/telegram-bot-stack.git

# Install specific version
pip install git+https://github.com/sensiloles/telegram-bot-stack.git@v0.1.0
```
````

````

### For Production Use:

1. **Small team / Personal use:** Git installation
2. **Company internal:** GitHub Packages or Self-hosted PyPI
3. **Public release later:** TestPyPI first, then PyPI

---

## 📝 Implementation Steps

### Step 1: Enable Git Installation (Easiest)

Just update your README.md to include git installation instructions. **No other changes needed!**

Your package is already installable via:
```bash
pip install git+https://github.com/sensiloles/telegram-bot-stack.git
````

### Step 2: Create Git Tags for Versions

```bash
# Tag current version
git tag -a v0.1.0 -m "Release v0.1.0 - Minimal Viable Framework"
git push origin v0.1.0

# Users can install specific versions
pip install git+https://github.com/sensiloles/telegram-bot-stack.git@v0.1.0
```

### Step 3: Add Installation Instructions

Update `README.md` and `docs/quickstart.md` with Git installation method.

---

## 🔒 Making Repository Private

If you want to keep the repository private:

```bash
# On GitHub: Settings → General → Danger Zone → Change visibility → Private
```

Then users need:

- SSH keys configured for GitHub
- Or GitHub personal access token

Installation:

```bash
# With SSH (users must have repo access)
pip install git+ssh://git@github.com/sensiloles/telegram-bot-stack.git

# With token
pip install git+https://<TOKEN>@github.com/sensiloles/telegram-bot-stack.git
```

---

## ⚖️ Comparison Table

| Method               | Setup Effort     | Cost | Access Control | Speed  | Recommended For       |
| -------------------- | ---------------- | ---- | -------------- | ------ | --------------------- |
| **Git Install**      | ⭐ Minimal       | Free | GitHub         | Medium | Small teams, personal |
| **GitHub Packages**  | ⭐⭐ Easy        | Free | GitHub         | Fast   | Teams, internal       |
| **Self-hosted PyPI** | ⭐⭐⭐ Medium    | Low  | Custom         | Fast   | Companies             |
| **Cloud Registry**   | ⭐⭐⭐⭐ Complex | $$$  | Cloud IAM      | Fast   | Enterprise            |
| **Public PyPI**      | ⭐⭐ Easy        | Free | Public         | Fast   | Open source           |

---

## 💡 Recommendation for Your Project

**Current status:** Public GitHub repository

**Best approach:**

1. ✅ **Now:** Use Git installation (zero setup)
2. 🔄 **Later:** Publish to PyPI when ready for public release

**Update README.md:**

````markdown
## Installation

### From GitHub (Current)

```bash
pip install git+https://github.com/sensiloles/telegram-bot-stack.git
```
````

### From PyPI (Coming Soon)

```bash
pip install telegram-bot-stack
```

````

This gives you:
- ✅ Immediate usability
- ✅ Version control via git tags
- ✅ No infrastructure setup
- ✅ Easy to switch to PyPI later

---

## 🚀 Quick Start

Want to make it installable **right now**?

Just tell users to run:
```bash
pip install git+https://github.com/sensiloles/telegram-bot-stack.git
````

**That's it!** Your package is already installable. 🎉
