# 🤖 Cloud Agent Guide for Quit Smoking Bot

Complete guide for using the automated issue management system.

## 🎯 Overview

Cloud Agent is an intelligent automation system that helps you manage GitHub Issues more efficiently. It provides:

- **🎤 Voice/Text Commands**: Create issues naturally
- **📋 Auto Task Breakdown**: Complex issues → manageable subtasks
- **🏷️ Smart Labeling**: Automatic label assignment based on content
- **✅ Acceptance Criteria**: Auto-generated success criteria
- **🔍 Context Analysis**: Find related files and issues
- **📊 Complexity Estimation**: Automatic time estimates

## 🚀 Quick Start

### 1. Create an Issue Normally

Just create a GitHub issue as you normally would. Cloud Agent will:

1. Analyze the content
2. Apply appropriate labels automatically
3. Suggest complexity level

Example:

```
Title: Add user statistics feature to /status command
Body: We need to show additional stats like days saved, money saved, etc.
```

Cloud Agent will automatically add labels like: `feature`, `component:bot`, `priority:medium`

### 2. Use Slash Commands

In any issue comment, use these commands:

#### `/breakdown`

Break the issue into subtasks automatically.

```
/breakdown
```

Result: Creates 3-5 subtask issues linked to the parent issue.

#### `/accept`

Generate acceptance criteria checklist.

```
/accept
```

Result: Adds a detailed checklist of requirements to the issue.

#### `/estimate`

Get time and complexity estimate.

```
/estimate
```

Result: Adds estimated complexity (simple/medium/complex/epic) and time estimate.

#### `/relate`

Find related files and similar issues.

```
/relate
```

Result: Lists related code files and similar past issues.

#### `/label <labels>`

Add specific labels manually.

```
/label bug, priority:high
```

#### `/assign @username`

Assign the issue to someone.

```
/assign @sensiloles
```

## 📋 Automatic Features

### Auto-Labeling

When you create an issue, labels are automatically applied based on keywords:

| Keywords                     | Applied Label             |
| ---------------------------- | ------------------------- |
| "add", "implement", "new"    | `feature`                 |
| "fix", "bug", "error"        | `bug`                     |
| "refactor", "improve"        | `refactor`                |
| "documentation", "readme"    | `docs`                    |
| "bot", "telegram", "command" | `component:bot`           |
| "docker", "container"        | `component:docker`        |
| "notification", "schedule"   | `component:notifications` |
| "critical", "urgent"         | `priority:critical`       |

### Auto-Subtask Generation

For issues labeled as `epic` or when you use `/breakdown`, subtasks are created based on issue type:

**Feature Issues** → Subtasks:

1. Frontend implementation
2. Backend implementation
3. Testing
4. Documentation

**Bug Issues** → Subtasks:

1. Reproduce the bug
2. Implement fix
3. Add regression tests
4. Verify in production

**Refactor Issues** → Subtasks:

1. Code analysis
2. Implementation
3. Testing
4. Cleanup & documentation

### Auto-Acceptance Criteria

When you label an issue as `feature` or `refactor`, or use `/accept`, Cloud Agent adds:

- ✅ Functional requirements checklist
- 🔧 Technical requirements
- 🧪 Testing requirements
- 📚 Documentation requirements

## 🎨 Available Labels

### Type Labels

- `feature` - New functionality
- `bug` - Something isn't working
- `refactor` - Code improvement
- `docs` - Documentation changes
- `test` - Testing related
- `chore` - Maintenance tasks
- `security` - Security issues

### Priority Labels

- `priority:critical` - Needs immediate attention
- `priority:high` - Important, work on soon
- `priority:medium` - Normal priority
- `priority:low` - Nice to have

### Component Labels

- `component:bot` - Bot core functionality
- `component:notifications` - Notification system
- `component:users` - User/admin management
- `component:prize` - Prize fund system
- `component:docker` - Docker/deployment
- `component:monitoring` - Health monitoring
- `component:cli` - CLI tools

### Status Labels

- `status:planning` - In planning phase
- `status:in-progress` - Currently being worked on
- `status:blocked` - Blocked by something
- `status:review` - In review
- `status:done` - Completed

## 📖 Usage Examples

### Example 1: Feature Request

**Create issue:**

```
Title: Add weekly statistics email digest
Body: Users should receive a weekly email with their quit smoking progress
```

**Cloud Agent automatically:**

- Adds labels: `feature`, `component:notifications`, `priority:medium`

**Then comment:**

```
/accept
```

**Result:** Acceptance criteria added with checkboxes for tracking.

### Example 2: Bug Report

**Create issue:**

```
Title: Bot crashes when user clicks /status multiple times
Body: If a user clicks /status command multiple times quickly, the bot crashes
```

**Cloud Agent automatically:**

- Adds labels: `bug`, `component:bot`, `priority:high`

**Then comment:**

```
/estimate
```

**Result:** Complexity estimate and time estimate added.

### Example 3: Large Refactoring

**Create issue:**

```
Title: Refactor user data storage to use database instead of JSON
Body: Current JSON file storage is not scalable. Need to migrate to SQLite/PostgreSQL
```

**Add label:** `epic`

**Cloud Agent automatically:**

- Creates 4 subtask issues:
  1. Analysis of current data structure
  2. Database implementation
  3. Migration script and testing
  4. Cleanup and documentation

### Example 4: Find Related Context

**Comment on any issue:**

```
/relate
```

**Result:**

- List of relevant code files
- Similar past issues
- Detected keywords

## 🔧 Configuration

### Setup Requirements

1. **GitHub Token**: Required for API access

   - Add `GITHUB_TOKEN` as repository secret

2. **Optional: OpenAI API Key**: For advanced AI features
   - Add `OPENAI_API_KEY` as repository secret
   - Enables more intelligent task breakdown

### Customization

Edit `.github/cloud-agent-config.yml` to customize:

- Label definitions and colors
- Subtask generation rules
- Acceptance criteria templates
- Command aliases
- File scan paths

## 🎯 Best Practices

### 1. Write Clear Issue Titles

```
✅ Good: "Add user export feature to CLI"
❌ Bad: "Export thing"
```

### 2. Include Context in Description

```
✅ Good: Describe what, why, and expected outcome
❌ Bad: One-sentence description
```

### 3. Use Commands Early

- Use `/estimate` during planning
- Use `/breakdown` for complex features
- Use `/accept` before starting work

### 4. Tag Components

Mention component names in your issue to trigger correct labels:

- "bot command" → `component:bot`
- "docker deployment" → `component:docker`
- "notification system" → `component:notifications`

### 5. Track Progress

- Check off acceptance criteria as you complete them
- Close subtasks when done
- Update status labels

## 🐛 Troubleshooting

### Commands Not Working?

**Check:**

1. Command starts with `/` (e.g., `/breakdown`)
2. Command is in a comment, not in issue body
3. GitHub Actions workflow is enabled
4. GITHUB_TOKEN is configured

### Wrong Labels Applied?

**Fix:**

1. Manually remove incorrect labels
2. Add correct labels manually or with `/label`
3. Update `.github/cloud-agent-config.yml` if pattern is wrong

### Subtasks Not Created?

**Check:**

1. Issue has `epic` label OR you used `/breakdown` command
2. Workflow has necessary permissions
3. Check Actions tab for errors

### Need Help?

1. Check [GitHub Actions logs](../../actions)
2. Look for errors in workflow runs
3. Open an issue with `component:cli` label

## 🔐 Security & Permissions

### Required Permissions

- `issues: write` - Create and edit issues
- `contents: read` - Read repository files
- `pull_requests: write` - Link PRs to issues

### What Cloud Agent Can Do

✅ Create issues
✅ Add labels
✅ Add comments
✅ Assign issues
✅ Read repository files (for context)

### What Cloud Agent Cannot Do

❌ Delete issues
❌ Close issues (unless explicitly programmed)
❌ Modify code
❌ Push commits
❌ Access secrets (except configured ones)

## 📊 Metrics & Analytics

Cloud Agent tracks:

- Issue creation time
- Subtask completion rate
- Label accuracy
- Command usage frequency

View metrics in the Actions tab under workflow runs.

## 🚀 Advanced Usage

### Custom Templates

Edit `.github/cloud-agent-config.yml`:

```yaml
issue_templates:
  my_custom_type:
    title_prefix: "[Custom]"
    template: |
      ## Description
      {description}
    default_labels: ["custom-label"]
```

### Voice Input Integration

If you have a voice-to-text system, you can create issues via API:

```bash
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/YOUR-USERNAME/quit-smoking-bot/issues \
  -d '{
    "title": "Voice command: Add feature X",
    "body": "Transcribed: User wants feature X with behavior Y"
  }'
```

### Workflow Dispatch

Trigger commands manually from Actions tab:

1. Go to Actions → Cloud Agent workflow
2. Click "Run workflow"
3. Select command and parameters
4. Click "Run workflow"

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Issues API](https://docs.github.com/en/rest/issues)
- [Project README](../../../README.md)
- [Development Guide](../../../DEVELOPMENT.md)

## 🎉 Tips & Tricks

1. **Batch Operations**: Use multiple commands in one comment:

   ```
   /estimate
   /accept
   /relate
   ```

2. **Template Issues**: Create template issues with common commands pre-filled

3. **Label Shortcuts**: Common label combinations are detected automatically

4. **Search History**: Use `/relate` to find how similar issues were solved

5. **Progress Tracking**: Check off acceptance criteria items as you work

---

**🤖 Happy automating!** Let Cloud Agent handle the administrative work while you focus on building great features.
