# 📦 Installation Instructions

> 📚 **Documentation Index:** See [Documentation Index](README.md) for all available guides.

`telegram-bot-stack` v0.1.0 - Reusable Telegram Bot Framework

## ✅ Quick Install (Recommended)

**Linux / macOS:**

```bash
# Install latest stable version
pip install telegram-bot-stack
```

**Windows (PowerShell):**

```powershell
# Install latest stable version
pip install telegram-bot-stack
```

**That's it!** Package is now installed and ready to use.

> **Windows Users:** See the comprehensive [Windows Setup Guide](windows-setup.md) for platform-specific instructions.

---

## 📋 All Installation Methods

### 1. Install Stable Version (v0.1.0)

```bash
pip install git+https://github.com/sensiloles/telegram-bot-stack.git@v0.1.0
```

**Use this for:** Production deployments, stable projects

### 2. Install Latest Development Version

```bash
pip install git+https://github.com/sensiloles/telegram-bot-stack.git
```

**Use this for:** Testing newest features, development

### 3. Install in requirements.txt

Add to your `requirements.txt`:

```txt
# Stable version
telegram-bot-stack @ git+https://github.com/sensiloles/telegram-bot-stack.git@v0.1.0

# Or latest
telegram-bot-stack @ git+https://github.com/sensiloles/telegram-bot-stack.git
```

Then install:

```bash
pip install -r requirements.txt
```

### 4. Install for Development

```bash
git clone https://github.com/sensiloles/telegram-bot-stack.git
cd telegram-bot-stack
pip install -e ".[dev]"
```

**Use this for:** Contributing to the framework, local modifications

---

## 🔒 Private Repository Installation

If the repository is private, use SSH:

```bash
# Install stable version
pip install git+ssh://git@github.com/sensiloles/telegram-bot-stack.git@v0.1.0

# Or latest
pip install git+ssh://git@github.com/sensiloles/telegram-bot-stack.git
```

**Requirements:**

- SSH key configured for GitHub
- Access to the repository

---

## 🚀 Verify Installation

**Linux / macOS:**

```bash
# Check version
python -c "import telegram_bot_stack; print(telegram_bot_stack.__version__)"

# Quick test
python -c "from telegram_bot_stack import BotBase; print('✅ Installation successful!')"
```

**Windows (PowerShell):**

```powershell
# Check version
python -c "import telegram_bot_stack; print(telegram_bot_stack.__version__)"

# Quick test
python -c "from telegram_bot_stack import BotBase; print('✅ Installation successful!')"
```

**Test in Python:**

```python
# Import components
from telegram_bot_stack import BotBase, UserManager, AdminManager
from telegram_bot_stack.storage import JSONStorage, MemoryStorage

print("✅ telegram-bot-stack installed successfully!")
```

---

## 🪟 Windows-Specific Installation

### Prerequisites

**1. Python 3.9+ Installation:**

Choose one:

- **Python.org (Recommended):**
  - Download from [python.org](https://www.python.org/downloads/)
  - ✅ Check "Add Python to PATH" during installation
- **Microsoft Store:**
  - Search "Python 3.11" in Microsoft Store
  - Automatically added to PATH

**Verify:**

```powershell
python --version  # Should show 3.9+
pip --version
```

**2. Git for Windows:**

- Download from [git-scm.com](https://git-scm.com/download/win)
- Use default installation settings

```powershell
git --version
```

### Installation

**PowerShell:**

```powershell
# Install framework
pip install telegram-bot-stack

# Verify
python -c "import telegram_bot_stack; print('✅ Installed!')"
```

**Command Prompt (cmd):**

```cmd
pip install telegram-bot-stack
python -c "import telegram_bot_stack; print('✅ Installed!')"
```

### Virtual Environment (Recommended)

**PowerShell:**

```powershell
# Create virtual environment
python -m venv venv

# Activate (if you see execution policy error, see below)
.\venv\Scripts\Activate.ps1

# Install framework
pip install telegram-bot-stack
```

**Fix execution policy error:**

```powershell
# Allow running scripts for current user
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**Command Prompt:**

```cmd
python -m venv venv
venv\Scripts\activate.bat
pip install telegram-bot-stack
```

### Common Windows Issues

**Issue: "python: command not found"**

Solution:

1. Reinstall Python from [python.org](https://www.python.org/downloads/)
2. ✅ Check "Add Python to PATH" during installation
3. Restart PowerShell/cmd

**Issue: "pip: command not found"**

```powershell
# Use Python module syntax
python -m pip install telegram-bot-stack
```

**Issue: Virtual environment activation fails**

```powershell
# PowerShell - allow script execution
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

# Then activate again
.\venv\Scripts\Activate.ps1
```

For complete Windows setup instructions, see the [Windows Setup Guide](windows-setup.md).

---

## 📚 Next Steps

After installation:

1. **Read Quick Start:** [Quick Start Guide](quickstart.md)
2. **Check Examples:** [examples/](../examples/)
3. **API Reference:** [API Reference](api_reference.md)

---

## 🔄 Upgrading

### Upgrade to Latest Version

```bash
pip install --upgrade git+https://github.com/sensiloles/telegram-bot-stack.git@v0.1.0
```

### Upgrade to Development Version

```bash
pip install --upgrade git+https://github.com/sensiloles/telegram-bot-stack.git
```

---

## ❓ Troubleshooting

### Issue: "No module named 'telegram_bot_stack'"

**Solution:** Install the package:

```bash
pip install git+https://github.com/sensiloles/telegram-bot-stack.git@v0.1.0
```

### Issue: "fatal: could not read from remote repository"

**For private repos:**

```bash
# Use SSH instead
pip install git+ssh://git@github.com/sensiloles/telegram-bot-stack.git@v0.1.0
```

### Issue: "Permission denied (publickey)"

**Solution:** Configure SSH key for GitHub:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# Add key to GitHub: Settings → SSH and GPG keys
```

---

## 📖 More Information

- **Full Documentation:** [Main README](../README.md)
- **Private Installation Options:** [Private Installation Guide](private_installation.md)
- **Migration Guide:** [Migration Guide](migration_guide.md)
- **GitHub Repository:** https://github.com/sensiloles/telegram-bot-stack

---

**Ready to build your bot?** Start with the [Quick Start Guide](quickstart.md)! 🤖✨
