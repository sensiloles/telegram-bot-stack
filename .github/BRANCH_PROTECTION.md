# 🔒 Branch Protection Setup Guide

Step-by-step guide to configure branch protection for `telegram-bot-stack`.

## 📋 Prerequisites

- Admin access to the repository
- GitHub account with appropriate permissions

## 🛡️ Configure Main Branch Protection

### Step 1: Navigate to Settings

1. Go to repository: https://github.com/sensiloles/telegram-bot-stack
2. Click **Settings** (top menu)
3. Click **Branches** (left sidebar)
4. Click **Add rule** or **Add branch protection rule**

### Step 2: Branch Name Pattern

```
Branch name pattern: main
```

### Step 3: Protection Rules

#### ✅ Require a pull request before merging

**Enable:** ☑️ Require a pull request before merging

**Sub-options:**

- ☑️ **Require approvals:** `1`
- ☑️ **Dismiss stale pull request approvals when new commits are pushed**
- ☐ Require review from Code Owners (optional - if you create CODEOWNERS file)
- ☑️ **Require approval of the most recent reviewable push**

#### ✅ Require status checks to pass before merging

**Enable:** ☑️ Require status checks to pass before merging

**Sub-options:**

- ☑️ **Require branches to be up to date before merging**

**Status checks to require:** (search and select)

- `test (Python 3.9)` or `test / test (3.9, ubuntu-latest)`
- `test (Python 3.10)` or `test / test (3.10, ubuntu-latest)`
- `test (Python 3.11)` or `test / test (3.11, ubuntu-latest)`
- `test (Python 3.12)` or `test / test (3.12, ubuntu-latest)`
- `lint` or `lint / Lint with Ruff`
- `type-check` or `type-check / Type Check with mypy`

**Note:** Status check names appear after first PR. You may need to:

1. Create a test PR first
2. Wait for checks to run
3. Return here to add them

#### ✅ Require conversation resolution before merging

**Enable:** ☑️ Require conversation resolution before merging

#### ⚙️ Rules applied to administrators (Optional)

**Recommended:**

- ☑️ **Do not allow bypassing the above settings**

**Or if you need emergency access:**

- ☐ Do not allow bypassing the above settings
- ☑️ **Include administrators** (in branch protection)

#### 🚫 Restrict Pushes and Deletions

**Recommended:**

- ☑️ **Restrict who can push to matching branches**
  - Select: Nobody (or specific users if needed)
- ☑️ **Block force pushes**
  - Enable: ☑️ Everyone
- ☑️ **Allow deletions:** ☐ (disabled)

### Step 4: Save Changes

Click **Create** or **Save changes** at the bottom

---

## 📝 Additional Configurations

### CODEOWNERS File (Optional)

Create `.github/CODEOWNERS` to auto-assign reviewers:

```
# Default owner for everything
* @sensiloles

# Core framework components
/telegram_bot_stack/ @sensiloles

# Documentation
/docs/ @sensiloles
*.md @sensiloles

# GitHub workflows
/.github/ @sensiloles

# Examples
/examples/ @sensiloles
```

### Auto-assign Issues and PRs

Create `.github/auto_assign.yml`:

```yaml
# Auto-assign issues and PRs
addReviewers: true
addAssignees: true

# Reviewers list
reviewers:
  - sensiloles

# Number of reviewers
numberOfReviewers: 1

# Assignees for issues
numberOfAssignees: 0
```

---

## 🧪 Test Branch Protection

### Method 1: Try Direct Push (Should Fail)

```bash
# This should be rejected
git checkout main
git commit --allow-empty -m "test: direct push"
git push origin main

# Expected error:
# remote: error: GH006: Protected branch update failed
```

### Method 2: Create Test PR (Should Succeed)

```bash
# Create feature branch
git checkout -b test/branch-protection
git commit --allow-empty -m "test: verify branch protection"
git push origin test/branch-protection

# Create PR on GitHub
# ✅ Should allow creating PR
# ✅ Should require approval
# ✅ Should require checks to pass
```

---

## 🔧 Troubleshooting

### Issue: Can't find status checks to require

**Solution:** Status checks appear after first workflow run:

1. Create a PR
2. Wait for CI checks to complete
3. Go back to Branch Protection settings
4. Search for check names (they'll now appear)
5. Select required checks

### Issue: Can't push even with PR

**Cause:** You're pushing directly to `main`

**Solution:** Always push to feature branch:

```bash
git checkout -b feature/my-feature
git push origin feature/my-feature
# Then create PR
```

### Issue: Need emergency fix

**Options:**

1. **Recommended:** Create hotfix PR with fast-track:

   ```bash
   git checkout -b hotfix/critical-fix
   # ... make fix ...
   git push origin hotfix/critical-fix
   # Create PR, request expedited review
   ```

2. **Emergency only:** Temporarily disable protection:
   - Go to Branch Protection settings
   - Click "Edit" on `main` rule
   - Uncheck "Do not allow bypassing"
   - Make fix
   - **Re-enable immediately**

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Direct push to `main` is blocked
- [ ] Can create branches and push to them
- [ ] Can create PRs to `main`
- [ ] PR requires at least 1 approval
- [ ] PR requires CI checks to pass
- [ ] Can't merge until checks pass
- [ ] Can't merge until approved
- [ ] Automatic releases work after merge

---

## 📊 Expected Workflow

```
Developer → Feature Branch → Push → Create PR
                                        ↓
                              CI Checks Run (auto)
                                        ↓
                              Code Review (manual)
                                        ↓
                              Approval (manual)
                                        ↓
                              Merge to main ✅
                                        ↓
                              Auto Release 🚀
```

---

## 🆘 Need Help?

- **GitHub Docs:** https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches
- **Test setup:** Create a test PR and verify all checks work
- **Questions:** Open an issue with label `question`

---

**Ready?** Follow these steps and your `main` branch will be protected! 🛡️
