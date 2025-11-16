# 📊 Project Status & Workflow

**Project:** telegram-bot-stack - Reusable Telegram Bot Framework
**Repository:** https://github.com/sensiloles/telegram-bot-stack
**Current Phase:** Phase 1 - Minimal Viable Framework
**Last Updated:** 2024-11-16

## 🎯 Quick Start for Agent

### 1. Check Current Phase

```bash
# Read current open issues
python3 .github/workflows/scripts/read_issues.py --list --state open

# Read specific issue details
python3 .github/workflows/scripts/read_issues.py <issue_number>
```

### 2. Understand Project Plan

- **Full Plan:** `PACKAGE_CONVERSION_PLAN_RU.md` (lines 761-1928)
- **Current Phase:** Phase 0.3 - Validation & Documentation
- **Next Phase:** Phase 1 - Minimal Viable Framework

### 3. Create New Issues (if needed)

```bash
# Quick method: Use create_issue.py script
python3 .github/workflows/scripts/create_issue.py \
    --title "[Type] Phase X: Description" \
    --file /tmp/issue.md \
    --labels label1,label2

# Programmatic: Use github_helper
from github_helper import get_repo
repo = get_repo()  # Auto-detects from git
issue = repo.create_issue(title="...", body="...", labels=[...])
```

**See:** `.github/workflows/scripts/README.md` for complete guide.

## 📋 Project Phases

### ✅ Phase 0.1: Extract Reusable Components

- **Issue #1:** CLOSED
- **Status:** Completed
- Extracted `src/core/` framework components (BotBase, Storage, UserManager, AdminManager)
- Refactored example bot (`QuitSmokingBot`) to use framework

### ✅ Phase 0.2: Comprehensive Testing

- **Issue #2:** CLOSED
- **Status:** Completed
- 111 tests with 81% coverage for `src/core/`
- CI/CD pipeline with GitHub Actions
- Coverage threshold validation

### ✅ Phase 0.3: Validation & Documentation

- **Issue #3:** CLOSED
- **Status:** Completed
- Final validation before framework extraction
- Documentation updates (ARCHITECTURE.md, README.md, DEVELOPMENT.md)
- Performance metrics documented
- All acceptance criteria met

### 🔄 Phase 1: Minimal Viable Framework (CURRENT)

- **Issue #4:** OPEN
- **Status:** In Progress
- Extract `src/core/` into standalone `telegram-bot-stack` package
- Implement Storage Abstraction Layer (JSON + Memory backends)
- Create example bots with comprehensive documentation
- Comprehensive testing and CI/CD
- Prepare for PyPI publication

## 📁 Project Structure

```
telegram-bot-stack/
├── src/
│   ├── core/              # ✅ Framework components (future PyPI package)
│   │   ├── bot_base.py    # Base class with common patterns
│   │   ├── storage.py     # Storage abstraction (JSON)
│   │   ├── user_manager.py
│   │   └── admin_manager.py
│   └── config.py
├── tests/                 # ✅ 111 tests, 81% coverage
│   ├── core/              # Framework tests
│   └── integration/       # E2E tests
├── .github/
│   ├── PROJECT_STATUS.md  # 👈 THIS FILE (project state)
│   ├── HOW_TO_CREATE_ISSUES.md
│   └── workflows/
│       ├── tests.yml      # ✅ CI/CD pipeline
│       └── scripts/       # Automation scripts
└── PACKAGE_CONVERSION_PLAN_RU.md  # 📖 Master plan
```

## 🔑 Key Files to Read First

**On every new context:**

1. `.github/PROJECT_STATUS.md` (this file) - Current status
2. `PACKAGE_CONVERSION_PLAN_RU.md` (lines 761-847) - Phase 0 details
3. Open issues via: `python3 .github/workflows/scripts/read_issues.py --list`

**For specific tasks:**

- GitHub automation → `.github/workflows/scripts/README.md`
- Git workflow → `.cursorrules` (lines 12-89)
- Testing → `README.md` (lines 80-154)
- Architecture → `README.md` (lines 155-250)

## 🚀 Common Workflows

### "Continue work on project"

```bash
# 1. Check status
python3 .github/workflows/scripts/read_issues.py --list --state open

# 2. Read current issue
python3 .github/workflows/scripts/read_issues.py <issue_number>

# 3. Check plan context
# Read PACKAGE_CONVERSION_PLAN_RU.md relevant section

# 4. Start implementation
# Follow issue checklist
```

### Creating New Phase Issue

```bash
# 1. Read plan for next phase
# PACKAGE_CONVERSION_PLAN_RU.md

# 2. Write issue content to file
cat > /tmp/issue_content.md << 'EOF'
## Phase Description
...
EOF

# 3. Create issue with script
python3 .github/workflows/scripts/create_issue.py \
    --title "[Phase] Phase X.X: Name" \
    --file /tmp/issue_content.md \
    --labels "phase:X,enhancement"
```

### Running Tests

```bash
# All tests
python3 -m pytest

# With coverage
python3 -m pytest --cov=src/core --cov-report=term

# Specific test
python3 -m pytest tests/core/test_storage.py -v
```

## 📊 Current Metrics

**Code Quality:**

- Test Coverage: 81% (src/core/)
- Total Tests: 111
- CI/CD: ✅ Passing
- Linter: ✅ No errors

**Progress:**

- Phase 0.1: ✅ 100% Complete
- Phase 0.2: ✅ 100% Complete
- Phase 0.3: ✅ 100% Complete
- **Overall Phase 0: ✅ 100% Complete**
- Phase 1: 🔄 0% (Just Started)

## 🔗 Quick Links

- **Issues:** https://github.com/sensiloles/telegram-bot-stack/issues
- **CI/CD:** https://github.com/sensiloses/telegram-bot-stack/actions
- **Plan:** `PACKAGE_CONVERSION_PLAN_RU.md`
- **Tests:** `.github/workflows/tests.yml`

## 💡 Important Notes

1. **Use modern PyGithub scripts** in `.github/workflows/scripts/` (not `gh` CLI)
2. **Token auto-loads** from `.env` - no manual setup needed
3. **Read PACKAGE_CONVERSION_PLAN_RU.md** for context on phases
4. **Check open issues** before starting new work
5. **Follow Conventional Commits** for all commits
6. **Update documentation** before committing code changes

---

**For detailed workflow rules, see:** `.cursorrules`
**For GitHub automation, see:** `.github/workflows/`
