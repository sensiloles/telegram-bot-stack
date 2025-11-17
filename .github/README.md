# 🔧 GitHub Configuration

Automation, workflows, and documentation for telegram-bot-stack.

## 📂 Directory Structure

```
.github/
├── docs/                     # 📚 Documentation
│   ├── workflow/            # Git Flow, PRs, Issues
│   ├── setup/               # Setup guides
│   └── scripts.md           # Automation scripts reference
├── workflows/               # ⚙️ CI/CD Workflows
│   ├── tests.yml           # Test automation
│   ├── release.yml         # Semantic releases
│   └── scripts/            # Automation scripts
├── ISSUE_TEMPLATE/          # 📝 Issue templates
├── pull_request_template.md # 📝 PR template
└── PROJECT_STATUS.md        # 📊 Current status (START HERE!)
```

## 🚀 Quick Start

### For New Contributors

1. **Read:** [`PROJECT_STATUS.md`](PROJECT_STATUS.md) - Current project state
2. **Setup:** [`docs/setup/getting-started.md`](docs/setup/getting-started.md) - Environment setup
3. **Workflow:** [`docs/workflow/git-flow.md`](docs/workflow/git-flow.md) - Git workflow

### For AI Agents (Cursor)

See [`.cursorrules`](../.cursorrules) for complete workflow rules.

**On every new context:**

1. Read `PROJECT_STATUS.md` - current phase
2. Check open issues: `python3 .github/workflows/scripts/read_issues.py --list`
3. Follow issue checklist or user request

## 📚 Documentation

### Workflow Guides

- **[Git Flow](docs/workflow/git-flow.md)** - Complete Git workflow with semantic releases
- **[PR Automation](docs/workflow/pr-automation.md)** - Automated Pull Request creation
- **[PR Naming](docs/workflow/pr-naming.md)** - Naming conventions for PRs
- **[Issue Linking](docs/workflow/issue-linking.md)** - Link issues with PRs
- **[Branch Protection](docs/workflow/branch-protection.md)** - Setup branch protection

### Setup Guides

- **[Getting Started](docs/setup/getting-started.md)** - Complete setup instructions
- **[Token Setup](docs/setup/token-setup.md)** - Configure GitHub token

### Automation

- **[Scripts Documentation](docs/scripts.md)** - All automation scripts
- **Scripts Location:** `workflows/scripts/` - Python automation scripts

## ⚙️ CI/CD Workflows

### Active Workflows

- **`tests.yml`** - Run tests on all PRs (Python 3.9-3.12)
- **`release.yml`** - Automatic releases on merge to main
- **`publish-github-packages.yml`** - Publish to GitHub Packages

### Test Coverage

- High test coverage maintained across all components
- Automated coverage reporting in CI/CD
- Coverage thresholds enforced automatically

## 🤖 Automation Scripts

Located in [`workflows/scripts/`](workflows/scripts/):

```bash
# Check CI status
python3 .github/workflows/scripts/check_ci.py --pr 5

# Create Pull Request
python3 .github/workflows/scripts/create_pr.py \
  --title "feat(storage): add Redis" \
  --closes 42

# Create Issue
python3 .github/workflows/scripts/create_issue.py \
  --title "Bug: Fix tests" \
  --file issue.md

# Read Issues
python3 .github/workflows/scripts/read_issues.py --list
```

See [docs/scripts.md](docs/scripts.md) for complete reference.

## 📊 Project Status

**Current Phase:** See [PROJECT_STATUS.md](PROJECT_STATUS.md) for up-to-date status
**Details:** Phase information, metrics, and next steps

## 🔗 Quick Links

- **[Project Status](PROJECT_STATUS.md)** - Current phase and metrics
- **[All Documentation](docs/)** - Complete docs index
- **[Issue Templates](ISSUE_TEMPLATE/)** - Bug reports & feature requests
- **[PR Template](pull_request_template.md)** - Pull request template
- **[CI Workflows](workflows/)** - GitHub Actions configurations

## 💡 Tips

- **Documentation:** All docs use consistent structure and cross-link
- **Automation:** Scripts auto-install dependencies (PyGithub, etc.)
- **Token:** Required for scripts - see [token setup](docs/setup/token-setup.md)
- **Coverage:** Automation scripts excluded from coverage

---

**Need help?** Check [docs/](docs/) for complete guides!
