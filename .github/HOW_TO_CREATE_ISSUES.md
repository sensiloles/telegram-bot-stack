# How to Create GitHub Issues Programmatically

## ✅ Working Method: PyGithub Library

**Use PyGithub instead of `gh` CLI** - it works reliably with our token setup.

### Quick Script Template

```python
#!/usr/bin/env python3
"""Create GitHub Issue"""

import os
import sys
from pathlib import Path

try:
    from github import Github
    from github.GithubException import GithubException
except ImportError:
    print("Installing PyGithub...")
    os.system("pip3 install PyGithub -q")
    from github import Github
    from github.GithubException import GithubException

# Read issue content from file
with open("/path/to/issue_content.md", "r") as f:
    body = f.read()

# Get token from environment or .env
token = os.getenv("GITHUB_TOKEN")
if not token:
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith("GITHUB_TOKEN="):
                    token = line.split("=", 1)[1].strip().strip('"')
                    break

if not token:
    print("❌ GITHUB_TOKEN not found")
    sys.exit(1)

# Create issue using PyGithub
try:
    g = Github(token)
    repo = g.get_repo("sensiloles/telegram-bot-stack")

    print("📝 Creating issue...")
    issue = repo.create_issue(
        title="Your Issue Title",
        body=body,
        labels=["label1", "label2", "priority:high"]  # Optional labels
    )

    print(f"✅ Issue created successfully!")
    print(f"🔗 URL: {issue.html_url}")
    print(f"📋 Issue #{issue.number}")

except GithubException as e:
    print(f"❌ Failed: {e}")
    if e.status == 401:
        print("Token invalid or missing 'repo' scope")
    sys.exit(1)
```

### Why PyGithub Works

1. **Correct Authentication**: Uses token properly without GraphQL permission issues
2. **Proven**: Successfully created Issues #1, #2, #3
3. **Simple API**: Direct Python calls, no shell escaping issues
4. **Better Error Handling**: Clear error messages and status codes

### ❌ Why gh CLI Fails

The `gh` CLI command fails with:
```
GraphQL: Resource not accessible by personal access token (repository.defaultBranchRef)
```

This is a permission issue with how `gh` accesses the repository metadata.

### Dependencies

Install PyGithub if needed:
```bash
pip3 install PyGithub
```

Or it will auto-install in the script.

### Token Setup

Token should be in `.env`:
```bash
GITHUB_TOKEN=your_token_here
```

Or exported:
```bash
export GITHUB_TOKEN=your_token_here
```

### Working Examples

See these files for reference:
- `.github/archive/create_github_issue.py` - Full-featured example
- This guide's template - Simplified version

### Usage Pattern

1. Write issue content to markdown file
2. Create Python script using template above
3. Run: `source .env && python3 script.py`
4. Issue created! ✅

## Previous Issues Created

- **Issue #1**: Phase 0.1 - Extract Reusable Components
- **Issue #2**: Phase 0.2 - Comprehensive Testing
- **Issue #3**: Phase 0.3 - Validation & Documentation

All created successfully with PyGithub! 🎉
