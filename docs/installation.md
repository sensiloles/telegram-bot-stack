# 📦 Installation Instructions

> 📚 **Documentation Index:** See [Documentation Index](README.md) for all available guides.

`telegram-bot-stack` v0.1.0 - Reusable Telegram Bot Framework

## ✅ Quick Install (Recommended)

```bash
# Install latest stable version
pip install git+https://github.com/sensiloles/telegram-bot-stack.git@v0.1.0
```

**That's it!** Package is now installed and ready to use.

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

```python
# Check version
python -c "import telegram_bot_stack; print(telegram_bot_stack.__version__)"
# Output: 0.1.0

# Import components
from telegram_bot_stack import BotBase, UserManager, AdminManager
from telegram_bot_stack.storage import JSONStorage, MemoryStorage

print("✅ telegram-bot-stack installed successfully!")
```

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
