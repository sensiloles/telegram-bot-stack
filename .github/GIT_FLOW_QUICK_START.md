# ⚡ Git Flow Quick Start

**TL;DR:** How to work with the new Git workflow in 5 minutes.

## 🎯 The Workflow

```bash
# 1. Start feature
git checkout main && git pull
git checkout -b feature/my-feature

# 2. Make changes & commit
git add .
git commit -m "feat(bot): add cool feature"

# 3. Push & create PR
git push origin feature/my-feature
# → Go to GitHub → Create Pull Request

# 4. Wait for:
# ✅ CI checks pass
# ✅ Code review approval

# 5. Merge PR
# → Automatic release happens! 🚀
```

## 📝 Commit Message Format

```
<type>(<scope>): <description>

feat:  New feature    → Minor version bump (0.1.0 → 0.2.0)
fix:   Bug fix        → Patch version bump (0.1.0 → 0.1.1)
docs:  Documentation  → No version bump
chore: Maintenance    → No version bump
```

### Examples

```bash
# New feature (minor bump)
git commit -m "feat(storage): add Redis backend"

# Bug fix (patch bump)
git commit -m "fix(auth): resolve token validation"

# Docs (no bump)
git commit -m "docs: update API reference"

# Breaking change (major bump)
git commit -m "feat!: redesign storage API

BREAKING CHANGE: All storage methods now async"
```

## 🚫 What's Blocked

```bash
# ❌ Direct push to main (blocked)
git push origin main

# ❌ Force push (blocked)
git push --force

# ❌ Merge without approval (blocked)
```

## ✅ What's Allowed

```bash
# ✅ Create branches
git checkout -b feature/anything

# ✅ Push to your branch
git push origin feature/anything

# ✅ Create PRs
# (on GitHub)

# ✅ Merge after approval + CI
# (on GitHub)
```

## 🔄 Common Operations

### Update Your Branch

```bash
# Get latest changes from main
git checkout main
git pull origin main
git checkout feature/my-feature
git merge main
git push origin feature/my-feature
```

### Fix Commit Message

```bash
# Amend last commit
git commit --amend -m "feat(bot): correct message"
git push --force-with-lease origin feature/my-feature
```

### Squash Commits

```bash
# Interactive rebase
git rebase -i main

# In editor: change 'pick' to 'squash' for commits to merge
# Save and exit

git push --force-with-lease origin feature/my-feature
```

## 📦 Automatic Releases

After merging to `main`:

1. **GitHub Action runs**
2. **Analyzes commits** (`feat`, `fix`, `perf`)
3. **Bumps version** (based on commit types)
4. **Creates tag** (e.g., `v0.2.0`)
5. **Generates changelog**
6. **Publishes release**

Install specific version:
```bash
pip install git+https://github.com/sensiloles/telegram-bot-stack.git@v0.2.0
```

## 🆘 Emergency Hotfix

```bash
# 1. Create hotfix branch
git checkout -b hotfix/critical-fix

# 2. Fix the issue
# ... make changes ...

# 3. Commit with fix type
git commit -m "fix(security): patch vulnerability"

# 4. Push & create PR with "hotfix" label
git push origin hotfix/critical-fix

# 5. Request expedited review
# 6. Merge ASAP
```

## 📚 Full Documentation

- **Complete workflow:** [GIT_WORKFLOW.md](GIT_WORKFLOW.md)
- **Branch protection:** [BRANCH_PROTECTION.md](BRANCH_PROTECTION.md)
- **Setup guide:** [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)

## ✨ Tips

- **Small PRs:** Easier to review, faster to merge
- **One feature per PR:** Keep changes focused
- **Test locally:** Run `pytest` before pushing
- **Clear descriptions:** Help reviewers understand changes
- **Conventional commits:** Enables automatic versioning

## 🎯 Remember

1. **Never push directly to `main`**
2. **Always use conventional commits**
3. **Wait for CI checks to pass**
4. **Request/provide code reviews**
5. **Delete branches after merge**

---

**Questions?** Check [GIT_WORKFLOW.md](GIT_WORKFLOW.md) or ask in discussions!
