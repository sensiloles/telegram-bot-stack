# ⚡ Configure Git Workflow - Quick Setup

**Final step:** Configure branch protection on GitHub to enable the new workflow.

## 🎯 What Was Added

✅ **Git Flow Implementation:**
- GitHub Flow with PR-only workflow
- Automatic semantic releases
- Conventional commits enforcement
- Complete documentation

✅ **Files Created:**
- `.github/workflows/release.yml` - Automatic releases
- `.github/GIT_WORKFLOW.md` - Complete guide
- `.github/GIT_FLOW_QUICK_START.md` - Quick reference
- `.github/BRANCH_PROTECTION.md` - Setup instructions
- `.github/pull_request_template.md` - PR template

## 🚀 Setup (5 minutes)

### Step 1: Enable GitHub Actions Permissions

1. Go to: https://github.com/sensiloles/telegram-bot-stack/settings/actions
2. Scroll to **Workflow permissions**
3. Select: ☑️ **Read and write permissions**
4. Check: ☑️ **Allow GitHub Actions to create and approve pull requests**
5. Click **Save**

### Step 2: Configure Branch Protection

1. Go to: https://github.com/sensiloles/telegram-bot-stack/settings/branches
2. Click **Add rule** or **Add branch protection rule**
3. **Branch name pattern:** `main`

#### Configure These Settings:

☑️ **Require a pull request before merging**
  - ☑️ Require approvals: `1`
  - ☑️ Dismiss stale pull request approvals when new commits are pushed

☑️ **Require status checks to pass before merging**
  - ☑️ Require branches to be up to date before merging
  - **Note:** Status check names will appear after first PR

☑️ **Require conversation resolution before merging**

☑️ **Block force pushes** (Everyone)

☐ **Do not allow bypassing the above settings**
  - Or: ☑️ if you want emergency access

4. Click **Create** or **Save changes**

### Step 3: Test the Setup

```bash
# 1. Try direct push (should fail)
git commit --allow-empty -m "test: direct push"
git push origin main
# ❌ Expected: remote: error: GH006: Protected branch update failed

# 2. Create test PR (should work)
git checkout -b test/workflow
git commit --allow-empty -m "test: verify workflow"
git push origin test/workflow
# ✅ Then create PR on GitHub
```

## 📚 What's Next?

### For Your First Feature

```bash
# 1. Create feature branch
git checkout main && git pull
git checkout -b feature/my-feature

# 2. Make changes
# ... code ...

# 3. Commit with conventional format
git add .
git commit -m "feat(bot): add awesome feature"

# 4. Push and create PR
git push origin feature/my-feature
# Go to GitHub and create PR

# 5. After merge → Automatic release! 🚀
```

### Commit Message Format

```bash
feat:  New feature    → Minor version (0.1.0 → 0.2.0)
fix:   Bug fix        → Patch version (0.1.0 → 0.1.1)
docs:  Documentation  → No version bump
chore: Maintenance    → No version bump

# Breaking change (major version)
feat!: API redesign
BREAKING CHANGE: Details here
```

## 📖 Full Documentation

- **Quick Start:** [.github/GIT_FLOW_QUICK_START.md](.github/GIT_FLOW_QUICK_START.md)
- **Complete Guide:** [.github/GIT_WORKFLOW.md](.github/GIT_WORKFLOW.md)
- **Branch Protection:** [.github/BRANCH_PROTECTION.md](.github/BRANCH_PROTECTION.md)
- **Detailed Setup:** [.github/SETUP_INSTRUCTIONS.md](.github/SETUP_INSTRUCTIONS.md)

## 🔒 After Configuration

✅ **Enabled:**
- Pull Requests required for all changes
- Automatic CI checks on every PR
- Code review approval required
- Automatic semantic versioning
- Auto-generated changelogs
- Auto-created GitHub Releases

❌ **Blocked:**
- Direct pushes to `main`
- Force pushes
- Merging without approval
- Merging without CI passing

## ✨ Benefits

- 🔐 **Protected main branch** - No accidental commits
- 🤖 **Automatic releases** - Version bumps on every merge
- 📝 **Clear history** - Conventional commits
- 🧪 **Always tested** - CI runs before merge
- 👥 **Code reviews** - Improve code quality
- 📊 **Auto changelog** - Generated from commits

## 🆘 Need Help?

**Detailed instructions:** [.github/BRANCH_PROTECTION.md](.github/BRANCH_PROTECTION.md)

**Questions?** Open an issue or check documentation.

---

**This is the last direct push to `main` - future changes via PRs only!** 🎉

Configure branch protection and enjoy automatic releases! 🚀
