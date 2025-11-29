# Windows Developer Setup

Complete guide for developing and deploying Telegram bots on Windows 10/11 using `telegram-bot-stack`.

**Good news:** Everything works natively on Windows! WSL2 is optional.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Terminal Options](#terminal-options)
- [Common Tasks](#common-tasks)
- [SSH Setup on Windows](#ssh-setup-on-windows)
- [Deployment from Windows](#deployment-from-windows)
- [Common Issues](#common-issues)
- [WSL2 vs Native Windows](#wsl2-vs-native-windows)
- [FAQ](#faq)

---

## Prerequisites

### Required

1. **Python 3.9 or higher**

   **Option A: Python.org (Recommended)**

   - Download from [python.org](https://www.python.org/downloads/)
   - ✅ Check "Add Python to PATH" during installation
   - Verify installation:

   ```powershell
   python --version  # Should show 3.9+
   pip --version
   ```

   **Option B: Microsoft Store**

   - Search "Python 3.11" in Microsoft Store
   - Click "Get" and install
   - Automatically added to PATH

2. **Git for Windows**

   - Download from [git-scm.com](https://git-scm.com/download/win)
   - Use default settings during installation
   - Verify:

   ```powershell
   git --version
   ```

### Optional

1. **Docker Desktop** (for VPS deployment)

   - Download from [docker.com](https://www.docker.com/products/docker-desktop/)
   - Requires Windows 10/11 Pro/Enterprise or WSL2 backend
   - Used for local testing (deployment targets Linux VPS)

2. **Terminal Enhancement** (optional)

   - [Windows Terminal](https://aka.ms/terminal) - Modern terminal from Microsoft Store
   - [PowerShell 7+](https://aka.ms/powershell) - Enhanced PowerShell

---

## Quick Start

### Installation

**PowerShell:**

```powershell
# Install the framework
pip install telegram-bot-stack

# Verify installation
telegram-bot-stack --version
```

**Command Prompt (cmd):**

```cmd
pip install telegram-bot-stack
telegram-bot-stack --version
```

### Create Your First Bot

**PowerShell:**

```powershell
# Create a new bot project
telegram-bot-stack init my-bot
cd my-bot

# Set your bot token (get from @BotFather)
$env:BOT_TOKEN = "123456:ABC-your-bot-token-here"

# Run the bot
telegram-bot-stack dev
```

**Command Prompt:**

```cmd
telegram-bot-stack init my-bot
cd my-bot

set BOT_TOKEN=123456:ABC-your-bot-token-here
telegram-bot-stack dev
```

### Development Workflow

**PowerShell:**

```powershell
# Start development server with auto-reload
telegram-bot-stack dev --reload

# Run tests
python -m pytest

# Run linting
python -m ruff check .

# Format code
python -m ruff format .
```

---

## Terminal Options

Windows offers multiple terminal environments. Here's what works best:

### PowerShell (Recommended)

**Built-in (PowerShell 5.1):**

- Pre-installed on Windows 10/11
- Full framework support ✅
- Best for everyday development

**PowerShell 7+ (Modern):**

- Download from [aka.ms/powershell](https://aka.ms/powershell)
- Better performance
- Cross-platform compatibility

**Environment variables:**

```powershell
# Temporary (current session)
$env:BOT_TOKEN = "123456:ABC..."

# Persistent (current user)
[System.Environment]::SetEnvironmentVariable('BOT_TOKEN', '123456:ABC...', 'User')
```

### Command Prompt (cmd)

**Classic Windows terminal:**

- Works fine for basic operations
- Limited scripting features

**Environment variables:**

```cmd
set BOT_TOKEN=123456:ABC...
```

### Git Bash

**Unix-like experience on Windows:**

- Included with Git for Windows
- Unix commands available (`ls`, `grep`, etc.)
- Can use Unix-style commands from docs

**Environment variables:**

```bash
export BOT_TOKEN="123456:ABC..."
```

### Windows Terminal (Modern UI)

**Best overall experience:**

- Multiple tabs
- PowerShell, cmd, Git Bash in one app
- Customizable themes
- Free from Microsoft Store

**Recommended for daily use.**

---

## Common Tasks

### Running Tests

**Without `make` (cross-platform):**

```powershell
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=telegram_bot_stack --cov-report=term

# Run specific test
python -m pytest tests/unit/core/test_bot_base.py -v
```

**Using `tasks.py` (alternative to Makefile):**

```powershell
# Run tests
python scripts/tasks.py test

# Run linting
python scripts/tasks.py lint

# Format code
python scripts/tasks.py format

# Run all checks
python scripts/tasks.py check-all
```

**Using `make` (if installed):**

```powershell
# Install make via Chocolatey
choco install make

# Or via Scoop
scoop install make

# Then use Makefile commands
make test
make lint
```

### Linting and Formatting

**Using ruff directly:**

```powershell
# Check for issues
python -m ruff check .

# Auto-fix issues
python -m ruff check . --fix

# Format code
python -m ruff format .
```

**Using tasks.py:**

```powershell
python scripts/tasks.py lint
python scripts/tasks.py format
```

### Type Checking

```powershell
# Run mypy
python -m mypy telegram_bot_stack
```

### Pre-commit Hooks

**Install pre-commit:**

```powershell
pip install pre-commit

# Install hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

**Works natively on Windows!** No WSL2 required.

---

## SSH Setup on Windows

SSH is required for VPS deployment. Windows 10/11 includes OpenSSH client built-in.

### Verify OpenSSH Client

**PowerShell (as Administrator):**

```powershell
# Check if OpenSSH client is installed
Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Client*'

# If not installed, install it
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
```

**OR use Settings:**

1. Settings → Apps → Optional Features
2. Search "OpenSSH Client"
3. If not listed, click "Add a feature" and install

### Generate SSH Key

**PowerShell:**

```powershell
# Create .ssh directory if needed
New-Item -Path $env:USERPROFILE\.ssh -ItemType Directory -Force

# Generate ED25519 key (recommended)
ssh-keygen -t ed25519 -f $env:USERPROFILE\.ssh\id_ed25519 -C "your_email@example.com"

# OR generate RSA key (if server doesn't support ed25519)
ssh-keygen -t rsa -b 4096 -f $env:USERPROFILE\.ssh\id_rsa -C "your_email@example.com"
```

**During generation:**

- Press Enter for default file location
- Enter passphrase (recommended) or leave empty
- Key is saved to `C:\Users\YourName\.ssh\id_ed25519`

### Fix SSH Key Permissions

**PowerShell (as Administrator):**

```powershell
# Navigate to .ssh directory
cd $env:USERPROFILE\.ssh

# Remove inherited permissions and set owner-only access
icacls .\id_ed25519 /inheritance:r
icacls .\id_ed25519 /grant:r "$($env:USERNAME):(R)"

# Verify
icacls .\id_ed25519
```

**Expected output:**

```
C:\Users\YourName\.ssh\id_ed25519 YOURNAME:(R)
```

### Copy Public Key to Server

**PowerShell:**

```powershell
# Display public key
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub

# Copy to clipboard
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub | Set-Clipboard

# Then paste it manually on server:
# ssh root@your-vps-ip
# echo "your-public-key" >> ~/.ssh/authorized_keys
```

**OR use ssh-copy-id (if available):**

```powershell
# If Git Bash or WSL available
ssh-copy-id -i $env:USERPROFILE\.ssh\id_ed25519.pub root@your-vps-ip
```

### Test SSH Connection

```powershell
# Test connection to VPS
ssh -i $env:USERPROFILE\.ssh\id_ed25519 root@your-vps-ip

# If successful, you'll be logged into the VPS
```

### Alternative: PuTTY

If you prefer PuTTY GUI:

**Generate keys with PuTTYgen:**

1. Download [PuTTY](https://www.putty.org/)
2. Run PuTTYgen
3. Generate SSH-2 ED25519 key
4. Save private key (.ppk)
5. Copy public key to server

**Convert PuTTY key to OpenSSH format:**

```powershell
# Use PuTTYgen: Conversions → Export OpenSSH key
# Save as id_ed25519 (no extension)
```

---

## Deployment from Windows

Deploy your bot to a Linux VPS from Windows using native tools.

### Prerequisites

1. ✅ SSH key generated (see above)
2. ✅ Linux VPS (Ubuntu, Debian, CentOS)
3. ✅ VPS IP address and root access

**Note:** Docker Desktop is NOT required for deployment (Docker runs on VPS, not locally).

### Initialize Deployment

**PowerShell:**

```powershell
# In your bot project directory
telegram-bot-stack deploy init

# Follow the prompts:
# - VPS hostname/IP: your-vps-ip
# - SSH user: root
# - SSH port: 22
# - SSH key path: C:\Users\YourName\.ssh\id_ed25519
# - Bot token: (will be stored securely)
```

**Configuration is saved to `.deployment/config.json`** (do not commit this file!)

### Deploy Your Bot

**PowerShell:**

```powershell
# Deploy to VPS
telegram-bot-stack deploy up

# Check status
telegram-bot-stack deploy status

# View logs
telegram-bot-stack deploy logs

# Update bot code
telegram-bot-stack deploy update

# Stop bot
telegram-bot-stack deploy down
```

### SSH Path Formats

**Windows paths work automatically:**

```json
{
  "ssh": {
    "key_path": "C:\\Users\\YourName\\.ssh\\id_ed25519"
  }
}
```

**OR use environment variable:**

```json
{
  "ssh": {
    "key_path": "~/.ssh/id_ed25519"
  }
}
```

**Both work!** The framework handles path conversion.

### Troubleshooting Deployment

**Permission denied (publickey)**

```powershell
# Fix key permissions
icacls $env:USERPROFILE\.ssh\id_ed25519 /inheritance:r
icacls $env:USERPROFILE\.ssh\id_ed25519 /grant:r "$($env:USERNAME):(R)"

# Verify SSH manually
ssh -i $env:USERPROFILE\.ssh\id_ed25519 root@your-vps-ip
```

**Connection timeout**

```powershell
# Check VPS firewall allows SSH (port 22)
# Check Windows Firewall allows outbound SSH

# Test connectivity
Test-NetConnection -ComputerName your-vps-ip -Port 22
```

**SSH key not found**

```powershell
# Verify key exists
Test-Path $env:USERPROFILE\.ssh\id_ed25519

# Check config.json has correct path
Get-Content .deployment\config.json
```

---

## Common Issues

### Line Endings (CRLF vs LF)

**Problem:** Git converts Unix line endings (LF) to Windows (CRLF), breaking scripts.

**Solution:** Configure Git to preserve LF:

```powershell
# For this repository
git config core.autocrlf input

# For all repositories (recommended)
git config --global core.autocrlf input

# Verify
git config --get core.autocrlf  # Should show "input"
```

**What this does:**

- Checkout: Keep LF (Unix) endings
- Commit: Keep LF (Unix) endings
- Result: Linux scripts work correctly

### Path Separators (Backslash vs Forward Slash)

**Problem:** Windows uses `\`, Unix uses `/`.

**Solution:** Use `pathlib` (already done in framework):

```python
from pathlib import Path

# Works on Windows and Unix
config_path = Path.home() / ".ssh" / "id_ed25519"
```

**For config files:**

```json
// ✅ Both work
"path": "C:/Users/Name/.ssh/id_ed25519"
"path": "C:\\Users\\Name\\.ssh\\id_ed25519"
```

### File Permissions

**Problem:** Windows doesn't support Unix file permissions (chmod 600).

**Solution:** Use `icacls` (Windows equivalent):

```powershell
# Make file readable only by you
icacls myfile.txt /inheritance:r
icacls myfile.txt /grant:r "$($env:USERNAME):(R)"
```

**Framework handles this automatically for SSH keys!**

### Docker Desktop Issues

**Problem:** "Docker daemon not running" error.

**Solutions:**

1. **Start Docker Desktop:**

   - Open Docker Desktop from Start menu
   - Wait for "Docker Desktop is running" status

2. **WSL2 backend (if on Windows Home):**

   - Install WSL2: [docs.microsoft.com/en-us/windows/wsl/install](https://docs.microsoft.com/en-us/windows/wsl/install)
   - Docker Desktop → Settings → General → "Use WSL 2 based engine"

3. **Not needed for deployment!**
   - Docker Desktop is only for local testing
   - Deployment uses Docker on Linux VPS

### Virtual Environment Activation

**PowerShell:**

```powershell
# Create venv
python -m venv venv

# Activate venv
.\venv\Scripts\Activate.ps1

# If you see execution policy error:
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**Command Prompt:**

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### Pytest Not Found

**Problem:** `pytest: command not found`

**Solution:**

```powershell
# Install in current environment
pip install pytest

# OR use module syntax (always works)
python -m pytest
```

### Git Bash Path Issues

**Problem:** Paths like `/c/Users/...` instead of `C:\Users\...`

**Solution:** Use `$USERPROFILE` or convert:

```bash
# Git Bash
export SSH_KEY="$USERPROFILE/.ssh/id_ed25519"

# Convert to Windows path if needed
winpath=$(cygpath -w "$USERPROFILE/.ssh/id_ed25519")
```

---

## WSL2 vs Native Windows

### When to Use WSL2

**Recommended for:**

- Advanced Linux tooling (e.g., `make`, `sed`, `awk`)
- Complex shell scripts
- Testing Linux-specific features
- Preference for Linux environment

**Setup:**

```powershell
# Install WSL2
wsl --install

# Install Ubuntu
wsl --install -d Ubuntu

# Inside WSL2:
sudo apt update
sudo apt install python3 python3-pip
pip install telegram-bot-stack
```

### When Native Windows is Fine

**Use native Windows for:**

- **Most development work** ✅
- Running tests
- Bot development
- VPS deployment
- Linting and formatting

**Advantages:**

- No extra setup
- Better performance (no virtualization)
- Simpler file paths
- Native IDE integration

### Performance Considerations

**Native Windows:**

- Faster file I/O
- No virtualization overhead
- Direct hardware access

**WSL2:**

- Slight overhead for virtualization
- File access across WSL/Windows boundary is slow
- Best to keep files inside WSL filesystem

**Recommendation:** Start with native Windows. Use WSL2 only if you need specific Linux tools.

---

## FAQ

### Do I need WSL2?

**No!** Everything works natively on Windows:

- ✅ Installing the framework
- ✅ Creating bots
- ✅ Development workflow
- ✅ Running tests
- ✅ Deploying to VPS

WSL2 is **optional** and only useful for advanced Linux tooling.

### Can I deploy from Windows to a Linux VPS?

**Yes!** This is the standard workflow:

- Develop on Windows
- Deploy to Linux VPS
- SSH works natively (OpenSSH included in Windows 10/11)

The framework handles all platform differences automatically.

### Which terminal should I use?

**Recommended order:**

1. **PowerShell** - Best overall (built-in, powerful)
2. **Windows Terminal** - Modern UI for PowerShell
3. **Git Bash** - If you prefer Unix commands
4. **Command Prompt (cmd)** - Works but limited

**All work fine!** Use what you're comfortable with.

### How do I run `make` commands?

**Option 1: Use `tasks.py` (no installation needed)**

```powershell
python scripts/tasks.py test
python scripts/tasks.py lint
```

**Option 2: Install `make`**

```powershell
# Using Chocolatey
choco install make

# Using Scoop
scoop install make

# Then use Makefile
make test
```

**Option 3: Use direct commands**

```powershell
python -m pytest
python -m ruff check .
```

### What about Python from Microsoft Store vs Python.org?

**Both work!**

**Python.org (Recommended):**

- More control over installation
- Official CPython distribution
- Better for development

**Microsoft Store:**

- Easier installation
- Automatic updates
- Good for beginners

**Either is fine for bot development.**

### How do I handle environment variables?

**PowerShell (temporary):**

```powershell
$env:BOT_TOKEN = "123456:ABC..."
```

**PowerShell (persistent):**

```powershell
[System.Environment]::SetEnvironmentVariable('BOT_TOKEN', '123456:ABC...', 'User')
```

**Command Prompt:**

```cmd
set BOT_TOKEN=123456:ABC...
```

**Best practice:** Use `.env` file:

```powershell
# Create .env file
echo "BOT_TOKEN=123456:ABC..." > .env

# Load in code (using python-dotenv)
from dotenv import load_dotenv
load_dotenv()
```

### Does Docker Desktop work on Windows Home?

**Yes!** But requires WSL2 backend:

1. Install WSL2: `wsl --install`
2. Install Docker Desktop
3. Enable "Use WSL 2 based engine" in settings

**Note:** Windows 10/11 Pro/Enterprise can use Hyper-V backend directly.

### Can I use Windows Subsystem for Linux (WSL)?

**Yes!** But it's optional:

**Recommended when:**

- You need Linux-specific tools
- You prefer Linux environment
- You're testing cross-platform features

**Not needed for:**

- Bot development
- Running tests
- VPS deployment

**Framework works great natively on Windows!**

---

## Additional Resources

### Official Documentation

- **Python on Windows:** [python.org/downloads/windows](https://www.python.org/downloads/windows/)
- **Git for Windows:** [git-scm.com/download/win](https://git-scm.com/download/win)
- **OpenSSH on Windows:** [docs.microsoft.com/en-us/windows-server/administration/openssh](https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_overview)
- **PowerShell Documentation:** [docs.microsoft.com/en-us/powershell](https://docs.microsoft.com/en-us/powershell/)
- **WSL2 Guide:** [docs.microsoft.com/en-us/windows/wsl](https://docs.microsoft.com/en-us/windows/wsl/)

### Framework Documentation

- **Main README:** [../README.md](../README.md)
- **Installation Guide:** [installation.md](installation.md)
- **Quick Start:** [quickstart.md](quickstart.md)
- **Deployment Guide:** [deployment_guide.md](deployment_guide.md)
- **Contributing:** [../CONTRIBUTING.md](../CONTRIBUTING.md)

### Community

- **GitHub Issues:** [github.com/sensiloles/telegram-bot-stack/issues](https://github.com/sensiloles/telegram-bot-stack/issues)
- **Discussions:** [github.com/sensiloles/telegram-bot-stack/discussions](https://github.com/sensiloles/telegram-bot-stack/discussions)

---

## Need Help?

**Found a Windows-specific issue?**

1. Check this guide first
2. Search [existing issues](https://github.com/sensiloles/telegram-bot-stack/issues)
3. Open a new issue with:
   - Windows version (10/11)
   - PowerShell/cmd/Git Bash
   - Error message
   - Steps to reproduce

**We're here to help!** 🚀
