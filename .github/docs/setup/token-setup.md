# 🔑 GitHub Token Setup Guide

Quick guide to configure your GitHub token for full automation support.

## 🎯 Problem

Getting this error when creating Pull Requests?

```
❌ Error: Failed to create Pull Request
Validation failed: not all refs are readable

⚠️  Token missing 'Contents: Read' permission (MOST COMMON)
```

## ✅ Solution: Update Token Permissions

### For Fine-Grained Tokens (Recommended)

1. **Go to Token Settings**
   ```
   https://github.com/settings/tokens?type=beta
   ```

2. **Find your token** (or create new one)

3. **Configure Repository Access:**
   - Select "Only select repositories"
   - Choose: `sensiloles/telegram-bot-stack`

4. **Set Permissions:**

   **Required permissions:**

   | Permission       | Access Level    | Why                              |
   | ---------------- | --------------- | -------------------------------- |
   | **Contents**     | **Read**        | **Read branches/refs (CRITICAL!)** |
   | **Pull requests** | **Read & Write** | Create and update PRs            |
   | **Issues**       | **Read & Write** | Create and link issues           |
   | **Metadata**     | **Read**        | Repository information (automatic) |

5. **Save Changes**

6. **Update `.env` file:**
   ```bash
   GITHUB_TOKEN=github_pat_YOUR_NEW_TOKEN_HERE
   ```

### For Classic Tokens (Alternative)

1. **Go to Classic Tokens**
   ```
   https://github.com/settings/tokens
   ```

2. **Generate new token (classic)**

3. **Select scopes:**
   - ✅ `repo` (Full control of private repositories)
     - This includes:
       - `repo:status`
       - `repo_deployment`
       - `public_repo`
       - `repo:invite`

4. **Generate and save token**

5. **Update `.env`:**
   ```bash
   GITHUB_TOKEN=ghp_YOUR_CLASSIC_TOKEN_HERE
   ```

## 🧪 Test Your Token

After updating, test the automation:

```bash
# Test PR creation (dry run)
python3 .github/workflows/scripts/create_pr.py \
--title "test: verify token permissions" \
--dry-run

# If dry-run works, try real creation
python3 .github/workflows/scripts/create_pr.py \
--title "test: verify token permissions" \
--draft
```

## 📋 Full Permissions Checklist

For complete automation support:

### Fine-Grained Token

```
Repository Access:
  ☑ sensiloles/telegram-bot-stack

Repository Permissions:
  ☑ Contents: Read               ← CRITICAL for PR creation
  ☑ Pull requests: Read & Write  ← Create PRs
  ☑ Issues: Read & Write         ← Create/link issues
  ☑ Metadata: Read               ← Auto-selected
  ☐ Workflows: Read & Write      ← Optional (for CI/CD updates)
```

### Classic Token

```
Scopes:
  ☑ repo (Full control)
    ☑ repo:status
    ☑ repo_deployment
    ☑ public_repo
    ☑ repo:invite
  ☐ workflow (Optional - for CI/CD)
```

## 🔍 Verify Token Permissions

Quick script to check your token:

```bash
# Check what your token can do
python3 << 'EOF'
import os
from github import Github

token = os.getenv('GITHUB_TOKEN')
if not token:
    print("❌ GITHUB_TOKEN not set")
    exit(1)

gh = Github(token)
user = gh.get_user()

print(f"✅ Token valid for user: {user.login}")
print(f"   Name: {user.name}")

# Try to access repo
try:
    repo = gh.get_repo("sensiloles/telegram-bot-stack")
    print(f"✅ Can access: {repo.full_name}")

    # Check what we can do
    permissions = repo.permissions
    print(f"\nPermissions:")
    print(f"  - Push: {permissions.push}")
    print(f"  - Pull: {permissions.pull}")
    print(f"  - Admin: {permissions.admin}")

except Exception as e:
    print(f"❌ Cannot access repo: {e}")

EOF
```

## 🚨 Common Issues

### Issue 1: "not all refs are readable"

**Cause:** Token missing `Contents: Read` permission

**Solution:** Add `Contents: Read` to token permissions

### Issue 2: "403 Forbidden"

**Cause:** Token doesn't have `Pull requests: Write` permission

**Solution:** Add `Pull requests: Read & Write` to token

### Issue 3: "401 Unauthorized"

**Cause:** Invalid token or token expired

**Solution:** Generate new token and update `.env`

### Issue 4: "404 Not Found"

**Cause:** Repository not accessible with token

**Solution:**
- For fine-grained: Add repository to "Repository access"
- For classic: Ensure `repo` scope is enabled

## 📱 Quick Links

- [Fine-grained tokens](https://github.com/settings/tokens?type=beta)
- [Classic tokens](https://github.com/settings/tokens)
- [GitHub API permissions docs](https://docs.github.com/en/rest/overview/permissions-required-for-fine-grained-personal-access-tokens)

## ✅ After Setup

Once token is configured:

```bash
# Test automation
cd /path/to/telegram-bot-stack

# 1. Create feature branch
git checkout -b test/token-verification

# 2. Make a change
echo "# Test" >> TEST.md
git add TEST.md
git commit -m "test: verify automation"
git push origin test/token-verification

# 3. Auto-create PR
python3 .github/workflows/scripts/create_pr.py \
--title "test: verify token automation" \
--draft

# 4. Should see:
# ✅ Pull Request created successfully!
#    Number: #X
#    URL: https://github.com/...

# 5. Clean up
git checkout main
git branch -D test/token-verification
# (Close PR on GitHub)
```

## 🎉 Success!

When you see:

```
✅ Pull Request created successfully!
   Number: #10
   URL: https://github.com/sensiloles/telegram-bot-stack/pull/10
```

Your token is properly configured! 🚀

---

**Need help?** Check [PR_AUTOMATION.md](.github/PR_AUTOMATION.md) for full automation guide.
