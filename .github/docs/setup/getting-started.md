# 🚀 Git Flow Setup Instructions

Complete setup guide for implementing the new Git workflow with automatic releases.

## 📋 Overview

This guide will help you set up:

1. ✅ Branch protection for `main`
2. ✅ Pull Request workflow
3. ✅ Automatic semantic releases
4. ✅ Conventional commits enforcement

**Estimated time:** 10-15 minutes

---

## 🎯 Step 1: Configure Branch Protection

### On GitHub Web Interface

1. Go to **Settings** → **Branches**
2. Click **Add rule** for `main` branch
3. Configure as described in [BRANCH_PROTECTION.md](BRANCH_PROTECTION.md)

**Quick checklist:**

- ☑️ Require pull requests
- ☑️ Require 1 approval
- ☑️ Require status checks
- ☑️ Require conversation resolution
- ☑️ Block force pushes
- ☑️ Restrict direct pushes

**Detailed guide:** [.github/BRANCH_PROTECTION.md](.github/BRANCH_PROTECTION.md)

---

## 🤖 Step 2: Enable GitHub Actions

### Grant Workflow Permissions

1. Go to **Settings** → **Actions** → **General**
2. Scroll to **Workflow permissions**
3. Select: **Read and write permissions**
4. Check: **Allow GitHub Actions to create and approve pull requests**
5. Click **Save**

This allows the release workflow to:

- Create tags
- Generate releases
- Update version files
- Commit changelogs

---

## 📝 Step 3: Test the Setup

### Create a Test Pull Request

```bash
# 1. Create test branch
git checkout main
git pull origin main
git checkout -b test/workflow-setup

# 2. Make a small change
echo "# Test PR" >> TEST.md
git add TEST.md
git commit -m "test: verify branch protection and CI"

# 3. Push and create PR (set upstream)
git push -u origin test/workflow-setup

# 4. On GitHub: Create Pull Request
# - Fill out PR template
# - Wait for CI checks
# - Request review (or approve yourself if admin)
# - Merge

# 5. Verify automatic release
# - Check GitHub Actions tab
# - Should see "Release" workflow running
# - Check Releases page for new version
```

---

## ✅ Step 4: Verify Everything Works

### Checklist

After merging test PR, verify:

- [ ] **Direct push blocked:**

  ```bash
  # This should fail
  git checkout main
  git commit --allow-empty -m "test"
  git push origin main
  # ❌ Expected: error: GH006: Protected branch update failed
  ```

- [ ] **PR workflow works:**

  - Can create feature branches ✅
  - Can push to feature branches ✅
  - Can create PRs ✅
  - CI checks run automatically ✅
  - Require approval to merge ✅

- [ ] **Automatic release works:**
  - Check: https://github.com/sensiloles/telegram-bot-stack/actions
  - "Release" workflow should have run ✅
  - New version tag created ✅
  - GitHub Release created ✅
  - CHANGELOG.md updated ✅

---

## 🔧 Step 5: Configure Semantic Release

### Verify Configuration Files

The following files should exist:

```
.github/
├── semantic_release.toml   # ✅ Semantic release config
├── workflows/
│   ├── release.yml         # ✅ Automatic release workflow
│   └── tests.yml           # ✅ CI tests
├── GIT_WORKFLOW.md         # ✅ Workflow documentation
├── BRANCH_PROTECTION.md    # ✅ Protection setup guide
└── pull_request_template.md # ✅ PR template
```

All files are already created! ✅

---

## 📚 Step 6: Update Documentation

### Add to README.md

Add contributing section (optional):

```markdown
## Contributing

See [GIT_WORKFLOW.md](.github/GIT_WORKFLOW.md) for our development workflow.

### Quick Start

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes
4. Commit: `git commit -m "feat(scope): description"`
5. Push: `git push -u origin feature/my-feature` (first push sets upstream)
6. Create Pull Request

All PRs require:

- ✅ Tests passing
- ✅ Code review approval
- ✅ Conventional commit format
```

---

## 🎓 Step 7: Team Onboarding

### Share with Team Members

Send them:

1. [GIT_WORKFLOW.md](.github/GIT_WORKFLOW.md) - Full workflow guide
2. Key points:
   - Always work in feature branches
   - Use conventional commits
   - Create PRs for all changes
   - Wait for CI checks

### Example Onboarding Message

```
👋 Welcome to telegram-bot-stack development!

Our workflow:
1. 🌿 Create feature branch: `git checkout -b feature/my-feature`
2. 💻 Make changes and commit: `git commit -m "feat: add feature"`
3. 🚀 Push and create PR: `git push -u origin feature/my-feature`
4. ✅ Wait for CI and approval
5. 🎉 Merge → automatic release!

📖 Full guide: .github/GIT_WORKFLOW.md
🤝 PR template will guide you

Questions? Ask in #dev-telegram-bot-stack
```

---

## 🔍 Troubleshooting

### CI Checks Not Running

**Problem:** PR created but no CI checks appear

**Solution:**

1. Check GitHub Actions is enabled: Settings → Actions
2. Verify workflow files are in `.github/workflows/`
3. Check workflow syntax: `act -l` (if using act locally)
4. Trigger manually: Actions tab → Select workflow → Run workflow

### Status Checks Not Required

**Problem:** Can merge without CI passing

**Solution:**

1. Go to Branch Protection settings
2. Edit `main` rule
3. "Require status checks to pass before merging"
4. Search and select all check names
5. Save changes

### Can Still Push to Main

**Problem:** Direct pushes still work

**Solution:**

1. Verify you're not an admin bypassing rules
2. Check "Do not allow bypassing" is enabled
3. Verify "Restrict who can push" is set
4. Check rule is applied to `main` (exact match)

### Release Not Triggering

**Problem:** Merged PR but no release created

**Solution:**

1. Check commit message format:
   - Must start with: `feat:`, `fix:`, or `perf:`
   - Others (`docs:`, `chore:`) don't trigger releases
2. Check Release workflow: Actions tab → Release
3. Check workflow logs for errors
4. Verify GitHub Actions has write permissions

---

## 📊 Success Metrics

After setup, you should see:

### In GitHub Repository

- ✅ Branch protection rules active on `main`
- ✅ Pull requests required for all changes
- ✅ CI checks running on every PR
- ✅ Automatic releases after merges
- ✅ Clean, linear history

### In Development Flow

- ✅ No direct pushes to `main`
- ✅ All changes reviewed via PRs
- ✅ Consistent commit format
- ✅ Automatic versioning
- ✅ Generated changelogs

---

## 🎯 Next Steps

After successful setup:

1. **Create your first feature:**

   ```bash
   git checkout -b feature/my-first-feature
   git commit -m "feat(bot): add awesome feature"
   git push origin feature/my-first-feature
   # Create PR
   ```

2. **Monitor automatic release:**

   - Merge PR
   - Watch Actions tab
   - Check Releases page
   - Verify version bump

3. **Share workflow with team:**

   - Link to GIT_WORKFLOW.md
   - Explain conventional commits
   - Show PR template usage

4. **Iterate and improve:**
   - Add CODEOWNERS if needed
   - Configure auto-assign
   - Add more CI checks
   - Customize release notes

---

## 🆘 Need Help?

- 📖 **Read:** [GIT_WORKFLOW.md](.github/GIT_WORKFLOW.md)
- 🔒 **Protection:** [BRANCH_PROTECTION.md](.github/BRANCH_PROTECTION.md)
- 📝 **Commits:** https://www.conventionalcommits.org/
- 🤖 **Actions:** https://github.com/sensiloles/telegram-bot-stack/actions

---

**Ready to go?** Your repository is now using modern Git workflow with automatic releases! 🚀
