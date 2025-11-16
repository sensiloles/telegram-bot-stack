# 📁 .github Directory Structure

This directory contains GitHub-specific configuration, workflows, and automation scripts.

## 🚀 Quick Start for Agents

**First time in new context? Read in this order:**

1. `PROJECT_STATUS.md` - Current project status and phase
2. `HOW_TO_CREATE_ISSUES.md` - Issue creation guide
3. `workflows/scripts/README.md` - Automation tools

## 📂 Directory Structure

```
.github/
├── PROJECT_STATUS.md           # 👈 START HERE - Current status
├── HOW_TO_CREATE_ISSUES.md     # Issue creation via PyGithub
├── README.md                    # This file
│
├── workflows/                   # GitHub Actions
│   ├── tests.yml               # CI/CD: tests, linting, coverage
│   ├── cloud-agent.yml         # Cloud Agent automation
│   └── scripts/                # Automation scripts
│       ├── README.md           # Scripts documentation
│       ├── read_issues.py      # ⭐ Read GitHub issues
│       ├── auto_label.py       # Auto-labeling
│       └── ...                 # Other automation
│
├── ISSUE_TEMPLATE/              # Issue templates
│   ├── bug_report.yml
│   ├── feature_request.yml
│   └── config.yml
│
├── docs/                        # Extended documentation
│   ├── cloud-agent/            # Cloud Agent guides
│   └── issue-management/       # Issue management docs
│
└── archive/                     # Old/reference files
    ├── create_github_issue.py  # Reference implementation
    ├── FIRST_ISSUE_DRAFT.md    # Issue #1 draft
    └── ...
```

## 🎯 Key Files

### For New Context Setup

| File                               | Purpose                          | Read When             |
| ---------------------------------- | -------------------------------- | --------------------- |
| `PROJECT_STATUS.md`                | Current phase, progress, metrics | **Every new context** |
| `HOW_TO_CREATE_ISSUES.md`          | PyGithub guide with template     | Creating issues       |
| `workflows/scripts/read_issues.py` | Read issues programmatically     | Checking status       |

### For Automation

| File                        | Purpose                | Usage                  |
| --------------------------- | ---------------------- | ---------------------- |
| `workflows/tests.yml`       | CI/CD pipeline         | Auto-runs on push/PR   |
| `workflows/cloud-agent.yml` | Cloud Agent automation | Issue commands         |
| `workflows/scripts/*.py`    | Helper scripts         | Manual/automated tasks |

## 🔍 Common Commands

### Check Project Status

```bash
# List open issues
python3 .github/workflows/scripts/read_issues.py --list --state open

# Read specific issue
python3 .github/workflows/scripts/read_issues.py <issue_number>

# Read with details
python3 .github/workflows/scripts/read_issues.py <issue_number> --json
```

### Create New Issue

```bash
# 1. Create issue content
cat > /tmp/issue_N.md << 'EOF'
## Issue content here
EOF

# 2. Use PyGithub (see HOW_TO_CREATE_ISSUES.md)
python3 /tmp/create_issue.py
```

### Check CI/CD Status

```bash
# View workflow runs
gh run list --limit 5

# View specific run
gh run view <run_id>
```

## 📊 Automation Features

### GitHub Actions Workflows

**tests.yml** - Comprehensive testing:

- Runs on: push, pull_request
- Python versions: 3.9, 3.10, 3.11, 3.12
- Steps: tests, linting, type checking, coverage
- Coverage threshold: 80%

**cloud-agent.yml** - Issue automation:

- Auto-labeling based on content
- Command execution (/breakdown, /accept, etc.)
- Context analysis

### Scripts

See `workflows/scripts/README.md` for detailed documentation.

**Key scripts:**

- `read_issues.py` - Read and format issues
- `auto_label.py` - Automatic issue labeling
- `generate_subtasks.py` - Break down large tasks

## 🔗 Related Documentation

- **Project Plan:** `../PACKAGE_CONVERSION_PLAN_RU.md`
- **Main README:** `../README.md`
- **Agent Rules:** `../.cursorrules`
- **Development:** `../DEVELOPMENT.md`

## 💡 Best Practices

1. **Always check** `PROJECT_STATUS.md` first
2. **Use PyGithub** for issue creation (not `gh` CLI)
3. **Read issues programmatically** via `read_issues.py`
4. **Check CI/CD** status before starting work
5. **Update PROJECT_STATUS.md** when phases complete

---

**For complete project workflow, see:** `PROJECT_STATUS.md`
