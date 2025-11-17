# 🔗 Linking Issues and Pull Requests

Complete guide for connecting GitHub Issues with Pull Requests.

## 🎯 Why Link Issues to PRs?

- ✅ **Automatic issue closing** when PR is merged
- ✅ **Traceability** - see which PR fixed which issue
- ✅ **Context** - reviewers understand the "why"
- ✅ **Project management** - automatic board updates

## 📝 Automatic Closing Keywords

GitHub automatically closes issues when PR is merged if you use these keywords:

### Supported Keywords

| Keyword    | Example         | Result                           |
| ---------- | --------------- | -------------------------------- |
| `Closes`   | `Closes #123`   | Issue #123 closes when PR merges |
| `Fixes`    | `Fixes #456`    | Issue #456 closes when PR merges |
| `Resolves` | `Resolves #789` | Issue #789 closes when PR merges |

**Case-insensitive:** `closes`, `Closes`, `CLOSES` all work!

### Where to Use Keywords

#### 1. In PR Description (Recommended)

```markdown
## Description

Added Redis storage backend

## Related Issue

Closes #123
```

#### 2. In Commit Messages

```bash
git commit -m "feat(storage): add Redis backend

Closes #123"
```

#### 3. In PR Comments

Just type in any PR comment:

```
Closes #123
```

## 🔗 Linking Multiple Issues

### Close Multiple Issues

```markdown
Closes #123, closes #456, closes #789
```

Or:

```markdown
Closes #123
Closes #456
Closes #789
```

Or:

```markdown
Closes #123, #456, #789
```

### Mix Auto-Close and References

```markdown
Closes #123
Related to #456
Part of #789
```

- `#123` will close automatically
- `#456` and `#789` will just be linked (won't auto-close)

## 🎨 Different Issue States

### Close Issue

```markdown
Closes #123
Fixes #456
Resolves #789
```

**Result:** Issues close when PR merges

### Reference Only (No Auto-Close)

```markdown
Related to #123
See #456
Part of #789
Mentioned in #100
Ref #200
```

**Result:** Issues stay open, just linked

### Block/Depend On

```markdown
Blocked by #123
Depends on #456
```

**Result:** Shows relationship, no auto-action

## 📚 Real-World Examples

### Feature Implementation

```markdown
## Description

Implemented Redis storage backend with connection pooling

## Related Issue

Closes #42

## Additional Context

Related to #38 (overall storage refactoring)
Part of #20 (Phase 2 roadmap)
```

### Bug Fix

```markdown
## Description

Fixed memory leak in storage layer

## Related Issue

Fixes #156

## Root Cause

The issue was caused by unclosed connections...
```

### Multiple Bugs

```markdown
## Description

Fixed authentication issues

## Related Issues

Fixes #201
Fixes #202
Fixes #203
```

### Documentation Update

```markdown
## Description

Updated API documentation

## Related Issue

Related to #89
```

**Note:** Using "Related to" because docs PR doesn't "close" the feature issue

## 🔄 Cross-Repository Linking

Link to issues in other repositories:

```markdown
Closes username/repo#123
Fixes sensiloles/other-project#456
```

## 🤖 For AI Agent

### In PR Description Template

Agent should fill:

```markdown
## Related Issue

Closes #<issue-number>
```

### In Commit Messages

```bash
git commit -m "feat(storage): add Redis backend

Implements new storage abstraction layer with Redis support.

Closes #42"
```

### Decision Tree

```
Is this PR implementing an issue?
  ├─ YES → Use "Closes #N" in PR description
  ├─ NO → Continue
  ↓
Is this PR fixing a bug from issue?
  ├─ YES → Use "Fixes #N" in PR description
  ├─ NO → Continue
  ↓
Is this PR related to an issue but doesn't complete it?
  ├─ YES → Use "Related to #N" in PR description
  └─ NO → No linking needed
```

## 🎯 Best Practices

### ✅ DO

- **Be specific:** `Closes #123` (not just `#123`)
- **In PR description:** Most visible place
- **One issue per PR:** Easier to review and track
- **Link before merge:** So it's in the PR history

### ❌ DON'T

- **Don't use ambiguous references:** Avoid just `#123` without context
- **Don't link unrelated issues:** Only link truly related issues
- **Don't forget the keyword:** `#123` alone won't auto-close (need "Closes #123")

## 🔍 Verification

### Check if Link Works

After creating PR:

1. Go to the issue (#123)
2. Check sidebar: "Linked pull requests"
3. Should see your PR listed
4. Hover shows "Will close this issue when merged"

### In PR View

1. Look at PR description
2. Linked issues show as clickable
3. Hover shows preview
4. Check sidebar: "Development" section shows linked issues

## 📊 Issue Closing Flow

```
Feature Branch → Create PR → Link Issue
                                  ↓
                     "Closes #123" in description
                                  ↓
                         PR gets reviewed
                                  ↓
                         Tests pass ✅
                                  ↓
                         PR is merged
                                  ↓
                     Issue #123 auto-closes 🎉
                                  ↓
                     Comment added to issue:
                     "Closed via #PR-number"
```

## 🛠️ Advanced Techniques

### Template Automation

In `.github/pull_request_template.md`:

```markdown
## Related Issue

Closes #ISSUE_NUMBER_HERE
```

### Commit Message Template

```bash
# In commit message:
type(scope): description

Longer explanation of changes.

Closes #123
Related to #456
```

### GitHub CLI

```bash
# Create PR and link issue
gh pr create --title "Add feature" --body "Closes #123"

# Link issue to existing PR
gh pr edit 42 --body "$(gh pr view 42 --json body -q .body)\n\nCloses #123"
```

## 📖 Examples in Our Project

### Feature Branch → Issue

```bash
# 1. Start from issue
git checkout -b feature/42-add-redis-backend

# 2. Make changes
# ... code ...

# 3. Commit with reference
git commit -m "feat(storage): add Redis backend

Implements connection pooling and automatic reconnection.

Closes #42"

# 4. Create PR
# PR description: "Closes #42"
```

### Multiple Related Issues

```markdown
## Description

Refactored storage layer

## Related Issues

Closes #42 (Redis backend)
Closes #43 (Connection pooling)
Related to #38 (Storage abstraction)
Part of #20 (Phase 2)
```

## 🎓 Quick Reference

### Auto-Close Keywords

```
closes, closed, close
fixes, fixed, fix
resolves, resolved, resolve
```

### Reference Keywords (No Auto-Close)

```
related to, relates to
part of
see, see also
mentioned in
ref, refs
```

### Usage Patterns

```markdown
# Single issue

Closes #123

# Multiple issues

Closes #123, closes #456

# Mixed

Closes #123
Related to #456

# Cross-repo

Closes username/repo#123
```

## 📚 Resources

- **GitHub Docs:** https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue
- **Autolinked References:** https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/autolinked-references-and-urls

---

**Pro Tip:** Always link your PRs to issues - it makes project management automatic! 🎯
