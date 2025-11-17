# 📝 Pull Request Naming Guide

Best practices and conventions for naming Pull Requests.

## 🎯 Why PR Names Matter

- ✅ **Clear history** - Shows what changed at a glance
- ✅ **Auto-changelog** - Used in release notes
- ✅ **Code review** - Reviewers understand purpose immediately
- ✅ **Searchability** - Easy to find specific changes

## 📋 Naming Convention

### For Squash Merge (Recommended)

**Format:** `type(scope): description`

Same as conventional commits - the PR title becomes the commit message!

```
feat(storage): add Redis backend support
fix(auth): resolve token validation issue
docs(api): update API reference
```

### For Merge Commit

**Format:** More descriptive, can be longer

```
Add Redis storage backend with connection pooling
Fix critical security vulnerability in auth flow
Update documentation for v0.2.0 release
```

## 🎨 PR Title Format

### Structure

```
<type>(<scope>): <short description>
```

**Components:**

1. **Type** - What kind of change (required)
2. **Scope** - What area affected (optional but recommended)
3. **Description** - Clear, concise summary (required)

### Type Options

| Type       | Use For                  | Example                                       |
| ---------- | ------------------------ | --------------------------------------------- |
| `feat`     | New features             | `feat(bot): add webhook support`              |
| `fix`      | Bug fixes                | `fix(storage): handle connection timeout`     |
| `docs`     | Documentation only       | `docs(readme): add installation guide`        |
| `refactor` | Code refactoring         | `refactor(handlers): simplify error handling` |
| `test`     | Adding/updating tests    | `test(storage): add integration tests`        |
| `chore`    | Maintenance tasks        | `chore(deps): update dependencies`            |
| `perf`     | Performance improvements | `perf(cache): optimize user lookup`           |
| `style`    | Code style/formatting    | `style(core): apply black formatting`         |
| `ci`       | CI/CD changes            | `ci(actions): add code coverage report`       |

### Scope Options (Project-Specific)

For `telegram-bot-stack`:

- `bot` - Bot core functionality
- `storage` - Storage layer (JSON, Memory, etc.)
- `auth` - Authentication/authorization
- `handlers` - Command handlers
- `workflow` - Git workflow, CI/CD
- `docs` - Documentation
- `examples` - Example bots
- `tests` - Test infrastructure

## ✅ Good Examples

### Features

```
feat(storage): add Redis backend support
feat(bot): implement webhook mode
feat(handlers): add rate limiting
```

### Bug Fixes

```
fix(auth): resolve token expiration issue
fix(storage): handle JSON decode errors
fix(bot): prevent duplicate message handling
```

### Documentation

```
docs(readme): add quick start guide
docs(api): document storage interface
docs(examples): add Redis bot example
```

### Refactoring

```
refactor(storage): extract common interface
refactor(handlers): consolidate error handling
refactor(bot): simplify command registration
```

### Multiple Changes

```
feat(storage): add Redis and PostgreSQL backends
fix(auth, handlers): resolve security issues
docs(readme, contributing): update guidelines
```

## ❌ Bad Examples

### Too Vague

```
❌ Update code
❌ Fix bug
❌ Changes
❌ WIP
```

### Too Long

```
❌ feat(storage): add Redis backend support with connection pooling, automatic reconnection, sentinel support, cluster mode, and comprehensive error handling
```

### Wrong Format

```
❌ Storage: Redis backend (missing type)
❌ FEAT: Add Redis (wrong capitalization)
❌ feat add redis (missing scope separator)
```

### No Context

```
❌ feat: add feature
❌ fix: fix issue
❌ Update file
```

## 🎯 Best Practices

### 1. Use Present Tense

✅ `feat(bot): add webhook support`
❌ `feat(bot): added webhook support`

### 2. Be Specific but Concise

✅ `fix(storage): handle connection timeout`
❌ `fix: fix problem`

### 3. Reference Issue Number (Optional in Title)

**Option A:** In title

```
feat(storage): add Redis backend (#42)
```

**Option B:** In description (better)

```
Title: feat(storage): add Redis backend
Description: Closes #42
```

### 4. Use Scope for Context

✅ `feat(storage): add Redis backend`
❌ `feat: add Redis backend`

### 5. Capitalize First Word After Colon

✅ `feat(bot): Add webhook support`
✅ `feat(bot): add webhook support`

Both acceptable, be consistent!

## 📊 Version Impact

PR title determines version bump (with squash merge):

| Title Type | Version Change        | Example                  |
| ---------- | --------------------- | ------------------------ |
| `feat:`    | MINOR (0.1.0 → 0.2.0) | `feat(bot): add feature` |
| `fix:`     | PATCH (0.1.0 → 0.1.1) | `fix(bot): fix bug`      |
| `perf:`    | PATCH (0.1.0 → 0.1.1) | `perf(bot): optimize`    |
| `docs:`    | No change             | `docs: update readme`    |
| `chore:`   | No change             | `chore: update deps`     |
| `feat!:`   | MAJOR (0.1.0 → 1.0.0) | `feat!: breaking change` |

## 🔄 Changing PR Title

Can change anytime before merge:

1. Go to PR on GitHub
2. Click title to edit
3. Update following conventions
4. Press Enter to save

## 🤖 For AI Agent

### Decision Tree

```
What type of changes?
  ├─ New feature → feat(scope): description
  ├─ Bug fix → fix(scope): description
  ├─ Documentation → docs(scope): description
  ├─ Tests → test(scope): description
  ├─ Refactoring → refactor(scope): description
  └─ Other → chore(scope): description

What scope?
  ├─ Bot core → (bot)
  ├─ Storage → (storage)
  ├─ Auth → (auth)
  ├─ Workflow → (workflow)
  ├─ Documentation → (docs)
  └─ Multiple → (scope1, scope2)

Description?
  ├─ Present tense
  ├─ Start with verb
  ├─ Be specific
  └─ Keep under 72 chars
```

### Template for Agent

```
[type]([scope]): [verb] [what] [where/why if needed]

Examples:
feat(storage): add Redis backend
fix(auth): resolve token validation
docs(api): update storage interface
test(storage): add Redis integration tests
refactor(handlers): simplify error handling
```

## 📝 Current PR Example

For our current PR (Git workflow documentation):

### Good Options:

```
✅ docs(workflow): add Git Flow rules and issue linking
✅ docs(cursorrules): add Git Flow rules for AI agent
✅ docs: add Git workflow rules and issue-PR linking
```

### Why These Work:

- **Type**: `docs` (documentation changes, no version bump)
- **Scope**: `workflow` or `cursorrules` (specific area)
- **Description**: Clear what was added
- **Length**: Under 72 characters
- **Present tense**: "add" not "added"

## 🎯 Templates by Type

### Feature PR

```
feat(storage): add [backend name] support
feat(bot): implement [feature name]
feat(handlers): add [handler name] command
```

### Bug Fix PR

```
fix(component): resolve [issue description]
fix(component): handle [edge case]
fix(component): prevent [problem]
```

### Documentation PR

```
docs(area): add [document name]
docs(area): update [document name]
docs: improve [section] documentation
```

### Refactoring PR

```
refactor(component): extract [what]
refactor(component): simplify [what]
refactor(component): restructure [what]
```

### Test PR

```
test(component): add [test type] tests
test(component): improve [test aspect]
test: increase coverage for [component]
```

## 🔗 Integration with Issues

### In PR Title (Optional)

```
feat(storage): add Redis backend (#42)
```

### In PR Description (Recommended)

```
Title: feat(storage): add Redis backend
Body:
Closes #42

Full description here...
```

**Why description is better:**

- Cleaner title
- Auto-linking still works
- Title used in changelog stays clean

## 📚 Real Project Examples

### From telegram-bot-stack

Recent PRs should follow:

```
feat(workflow): implement GitHub Flow with automatic releases
docs(status): update project status for Phase 1 completion
feat(framework): extract core to telegram-bot-stack package
docs(framework): add comprehensive documentation
chore: add MIT license file
```

## ✨ Quick Reference

**Format:** `type(scope): description`

**Types:** feat, fix, docs, refactor, test, chore, perf, style, ci

**Scopes:** bot, storage, auth, handlers, workflow, docs, examples, tests

**Description:** Present tense, specific, concise (< 72 chars)

**Issue Link:** In description, not title (use "Closes #N")

---

**Keep it simple, clear, and consistent!** 🎯
