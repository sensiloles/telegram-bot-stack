# How to Create GitHub Issues

**⚠️ NOTE: This guide is simplified. See `.github/workflows/scripts/README.md` for complete documentation.**

## ✅ Quick Method: Use create_issue.py

The easiest way to create issues:

```bash
# From markdown file
python3 .github/workflows/scripts/create_issue.py \
    --title "Bug: Fix tests" \
    --file /tmp/issue.md \
    --labels bug,priority:high

# Interactive (type description, Ctrl+D when done)
python3 .github/workflows/scripts/create_issue.py --title "New feature"
```

**Full documentation:** `.github/workflows/scripts/README.md`

## 📚 Programmatic Method: Use PyGithub

For custom scripts or complex operations:

```python
from github_helper import get_repo

# Get repository (auto-detected)
repo = get_repo()

# Create issue
issue = repo.create_issue(
    title="Bug: Something broke",
    body="Detailed description...",
    labels=["bug", "priority:high"]
)

print(f"✅ Created: {issue.html_url}")
```

## 🔧 Setup

Token automatically loaded from `.env`:

```bash
GITHUB_TOKEN=your_token_here
```

## 💡 Why PyGithub?

- ✅ Works reliably with personal access tokens
- ✅ No GraphQL permission issues (unlike `gh` CLI)
- ✅ Successfully created Issues #1, #2, #3, #4
- ✅ Better error handling and messages

## 🔗 See Also

- **Complete Guide:** `.github/workflows/scripts/README.md`
- **Scripts:** `.github/workflows/scripts/`
- **Project Workflow:** `.github/PROJECT_STATUS.md`
