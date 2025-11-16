# 🤖 Cloud Agent - Automated Issue Management System

<div align="center">

**Intelligent automation for GitHub Issues with voice/text commands, auto-labeling, task breakdown, and acceptance criteria generation**

[![GitHub Actions](https://img.shields.io/badge/Automation-GitHub%20Actions-2088FF?logo=github-actions)](https://github.com/features/actions)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[Quick Start](#-quick-start) •
[Features](#-features) •
[Commands](#-slash-commands) •
[Guide](GUIDE.md) •
[Configuration](../../cloud-agent-config.yml)

</div>

---

## 🎯 What is Cloud Agent?

Cloud Agent is a comprehensive GitHub Issues automation system that brings AI-powered assistance to your issue management workflow. It's designed specifically for the **Quit Smoking Bot** project but can be adapted for any repository.

### Why Cloud Agent?

**Before Cloud Agent:**

- ❌ Manual labeling of every issue
- ❌ Spending time breaking down complex tasks
- ❌ Writing acceptance criteria from scratch
- ❌ Searching for related files manually
- ❌ Estimating complexity subjectively

**With Cloud Agent:**

- ✅ Automatic intelligent labeling
- ✅ AI-powered task breakdown
- ✅ Auto-generated acceptance criteria
- ✅ Context-aware file search
- ✅ Consistent complexity estimation

## ✨ Features

### 🎤 **Natural Language Processing**

Create issues using voice or text commands. Cloud Agent understands context and intent.

```
"Create an issue to add user statistics to the status command"
→ Automatically labeled as: feature, component:bot, priority:medium
```

### 🏷️ **Intelligent Auto-Labeling**

Issues are automatically labeled based on content analysis:

- **Type Detection**: feature, bug, refactor, docs, test, chore, security
- **Component Mapping**: bot, notifications, users, prize, docker, monitoring, cli
- **Priority Assignment**: critical, high, medium, low
- **Status Tracking**: planning, in-progress, blocked, review, done

### 📋 **Smart Task Breakdown**

Complex issues are automatically split into manageable subtasks:

**Feature** → Frontend + Backend + Testing + Documentation
**Bug** → Reproduce + Fix + Test + Verify
**Refactor** → Analysis + Implementation + Testing + Cleanup

### ✅ **Acceptance Criteria Generation**

Auto-generated checklists with:

- Functional requirements
- Technical requirements
- Testing requirements
- Documentation requirements

### 🔍 **Context Analysis**

Find related code files and similar issues automatically:

- Scans repository structure
- Analyzes git history
- Suggests relevant files
- Links similar past issues

### 📊 **Complexity Estimation**

Automatic time and effort estimation:

- **Simple**: 1-3 hours
- **Medium**: 4-8 hours
- **Complex**: 1-3 days
- **Epic**: 1+ weeks

## 🚀 Quick Start

### 1. Setup

Cloud Agent is already configured in this repository. To enable:

1. **Ensure GitHub Actions is enabled** in repository settings
2. **Add secrets** (if using advanced AI features):
   ```
   Settings → Secrets → Actions → New repository secret
   Name: OPENAI_API_KEY
   Value: your-openai-api-key
   ```
3. **Create an issue** - Cloud Agent starts working automatically!

### 2. Create Your First Automated Issue

**Method 1: Use Issue Templates**

1. Go to [Issues → New Issue](../../issues/new/choose)
2. Choose "🎯 Feature Request" or "🐛 Bug Report"
3. Fill in the form
4. Submit → Cloud Agent automatically labels it!

**Method 2: Manual Creation**

1. Create a regular GitHub issue
2. Cloud Agent analyzes the content
3. Labels are applied automatically
4. Use slash commands for more automation

### 3. Use Slash Commands

In any issue comment, type commands:

```
/breakdown     # Break into subtasks
/accept        # Generate acceptance criteria
/estimate      # Get time estimate
/relate        # Find related files
```

## 🎯 Slash Commands

### Core Commands

| Command      | Description                   | Example      |
| ------------ | ----------------------------- | ------------ |
| `/breakdown` | Break issue into subtasks     | `/breakdown` |
| `/accept`    | Generate acceptance criteria  | `/accept`    |
| `/estimate`  | Estimate complexity and time  | `/estimate`  |
| `/relate`    | Find related files and issues | `/relate`    |

### Management Commands

| Command             | Description         | Example                     |
| ------------------- | ------------------- | --------------------------- |
| `/label <labels>`   | Add specific labels | `/label bug, priority:high` |
| `/assign @user`     | Assign to user      | `/assign @sensiloles`       |
| `/priority <level>` | Set priority        | `/priority high`            |

### Batch Commands

You can use multiple commands in one comment:

```
/estimate
/accept
/relate
```

## 📖 Usage Examples

### Example 1: Feature Request with Auto-Labeling

**Issue Created:**

```
Title: Add weekly email digest for users
Body: Users should receive a weekly summary of their progress via email
```

**Cloud Agent Automatically:**

- Labels: `feature`, `component:notifications`, `priority:medium`
- Detects complexity: Medium (4-8 hours)

**Then Comment:**

```
/accept
```

**Result:** Acceptance criteria checklist added with 15+ specific requirements

---

### Example 2: Bug Report with Quick Fix

**Issue Created:**

```
Title: Bot crashes on /status command
Body: When clicking /status multiple times, bot crashes with timeout error
```

**Cloud Agent Automatically:**

- Labels: `bug`, `component:bot`, `priority:high`

**Then Comment:**

```
/estimate
/relate
```

**Result:**

- Estimated fix time: 2-4 hours
- Related files found: `src/bot.py`, `src/status.py`
- Similar issue found: #42 (fixed last month)

---

### Example 3: Epic Feature Breakdown

**Issue Created with `epic` label:**

```
Title: Complete user statistics dashboard
Body: Build comprehensive dashboard showing all user progress metrics
```

**Then Comment:**

```
/breakdown
```

**Result:** Cloud Agent creates 4 subtask issues:

1. [Subtask 1/4] Frontend: Complete user statistics dashboard
2. [Subtask 2/4] Backend: Complete user statistics dashboard
3. [Subtask 3/4] Testing: Complete user statistics dashboard
4. [Subtask 4/4] Documentation: Complete user statistics dashboard

Each subtask includes specific objectives and links to parent issue.

---

## 🏗️ Architecture

```
Cloud Agent System
├── Configuration
│   └── .github/cloud-agent-config.yml     # Main configuration
│
├── GitHub Actions Workflows
│   └── .github/workflows/
│       └── cloud-agent.yml                # Main workflow
│
├── Automation Scripts
│   └── .github/workflows/scripts/
│       ├── parse_command.py               # Command parser
│       ├── execute_command.py             # Command executor
│       ├── auto_label.py                  # Auto-labeling logic
│       ├── generate_subtasks.py           # Task breakdown
│       ├── add_acceptance_criteria.py     # Criteria generation
│       └── analyze_context.py             # Context analysis
│
└── Issue Templates
    └── .github/ISSUE_TEMPLATE/
        ├── feature_request.yml
        ├── bug_report.yml
        └── config.yml
```

## 🔧 Configuration

### Basic Configuration

Edit `.github/cloud-agent-config.yml` to customize:

```yaml
# Enable/disable features
issue_creation:
  auto_labeling:
    enabled: true
  subtask_generation:
    enabled: true
    max_subtasks: 10

# Customize labels
auto_labeling:
  labels:
    type:
      - name: "custom-type"
        color: "FF5733"
        keywords: ["my keyword"]
```

### Advanced Configuration

See [cloud-agent-config.yml](cloud-agent-config.yml) for all available options:

- Label definitions and colors
- Subtask generation rules
- Acceptance criteria templates
- Context analysis settings
- Voice command patterns
- Workflow automation rules

## 🛠️ Project-Specific Labels

### Component Labels (Quit Smoking Bot)

| Label                     | Purpose                | Triggered By                   |
| ------------------------- | ---------------------- | ------------------------------ |
| `component:bot`           | Core bot functionality | "bot", "telegram", "command"   |
| `component:notifications` | Notification system    | "notification", "schedule"     |
| `component:users`         | User management        | "user", "admin", "auth"        |
| `component:prize`         | Prize fund system      | "prize", "fund", "reward"      |
| `component:docker`        | Docker/deployment      | "docker", "container"          |
| `component:monitoring`    | Health monitoring      | "monitoring", "health", "logs" |
| `component:cli`           | CLI tools              | "cli", "manager", "script"     |

## 📊 Analytics & Reporting

Cloud Agent tracks metrics:

- Issue creation time
- Subtask completion rate
- Label accuracy
- Command usage frequency
- Time estimates vs actual

View reports in GitHub Actions → Cloud Agent workflow runs.

## 🔐 Security & Permissions

### What Cloud Agent Can Do

✅ Create and edit issues
✅ Add labels and comments
✅ Assign issues
✅ Read repository files (for context)
✅ Analyze git history

### What Cloud Agent Cannot Do

❌ Delete issues
❌ Modify code or push commits
❌ Access user data outside the repository
❌ Close issues without permission
❌ Modify repository settings

### Required Secrets

- `GITHUB_TOKEN` - Automatically provided by GitHub Actions
- `OPENAI_API_KEY` - Optional, for advanced AI features

## 🐛 Troubleshooting

### Commands Not Working?

**Check:**

1. Command starts with `/` (e.g., `/breakdown`)
2. GitHub Actions is enabled
3. Workflow has permissions (issues: write)
4. Check Actions tab for error logs

### Wrong Labels Applied?

**Solutions:**

1. Manually adjust labels
2. Update keyword patterns in config
3. Use `/label` command for manual labeling

### Need More Help?

- 📖 [Full Guide](GUIDE.md) - Comprehensive documentation
- 🐛 [Report Issue](../../issues/new?labels=component:cli,bug)
- 💬 [Discussions](../../discussions)

## 📚 Documentation

- **[Complete Guide](GUIDE.md)** - Full usage guide with examples
- **[Configuration Reference](../../cloud-agent-config.yml)** - All configuration options
- **[Project README](../../../README.md)** - Main project documentation

## 🎉 Tips & Tricks

### 1. Use Batch Commands

```
/estimate
/accept
/relate
```

### 2. Create Template Issues

Save time by creating issue templates with common patterns.

### 3. Leverage Auto-Labeling

Include component keywords in your issue title for automatic labeling.

### 4. Track Progress

Check off acceptance criteria items as you work.

### 5. Learn from History

Use `/relate` to see how similar issues were solved.

## 🚀 Roadmap

Planned features:

- [ ] Integration with project boards
- [ ] Slack notifications
- [ ] Advanced AI-powered code analysis
- [ ] Voice input via Telegram bot
- [ ] Custom workflow triggers
- [ ] Metric dashboards

## 🤝 Contributing

Contributions welcome! To add features:

1. Fork the repository
2. Edit scripts in `.github/workflows/scripts/`
3. Update configuration in `cloud-agent-config.yml`
4. Test with workflow dispatch
5. Submit pull request

## 📄 License

MIT License - same as the main project.

---

<div align="center">

**🤖 Cloud Agent** - Making issue management effortless

Created for [Quit Smoking Bot](../../../README.md)

[Get Started](#-quick-start) • [View Guide](GUIDE.md) • [Report Bug](../../issues/new?labels=bug,component:cli)

</div>
