# 🚀 Cloud Agent Quick Start

**Get started with automated issue management in 2 minutes!**

## ✨ What You Get

- 🤖 **Automatic labeling** of all new issues
- 📋 **Smart task breakdown** for complex features
- ✅ **Auto-generated acceptance criteria**
- 🔍 **Intelligent context analysis**
- 📊 **Complexity estimation**

## 🎯 How to Use

### 1. Create an Issue

Go to [Issues → New Issue](../../issues/new/choose) and choose a template:

- 🎯 **Feature Request** - For new functionality
- 🐛 **Bug Report** - For bugs and issues

Cloud Agent will automatically analyze and label your issue!

### 2. Use Slash Commands

In any issue comment, type:

```
/breakdown    # Break into subtasks
/accept       # Generate acceptance criteria
/estimate     # Get time estimate
/relate       # Find related files/issues
```

### 3. Manage with Labels

Issues are automatically labeled with:

- **Type**: `feature`, `bug`, `refactor`, `docs`
- **Component**: `component:bot`, `component:docker`, etc.
- **Priority**: `priority:critical`, `priority:high`, etc.

## 📖 Examples

### Example 1: Create Feature with Auto-Labeling

**Issue Title:** Add user statistics dashboard
**Issue Body:** We need a dashboard showing all user progress metrics

**Result:** Cloud Agent automatically adds:

- ✅ `feature` label
- ✅ `component:bot` label
- ✅ `priority:medium` label

### Example 2: Break Down Complex Task

**Comment:** `/breakdown`

**Result:** Cloud Agent creates 4 subtask issues:

1. Frontend implementation
2. Backend implementation
3. Testing
4. Documentation

### Example 3: Generate Acceptance Criteria

**Comment:** `/accept`

**Result:** Cloud Agent adds detailed checklist:

- ✅ Functional requirements (5+ items)
- ✅ Technical requirements (5+ items)
- ✅ Testing requirements (4+ items)
- ✅ Documentation requirements (4+ items)

## 🎨 Available Commands

| Command            | Description                  | Example Output                    |
| ------------------ | ---------------------------- | --------------------------------- |
| `/breakdown`       | Break into subtasks          | Creates 3-5 linked subtask issues |
| `/accept`          | Generate acceptance criteria | Adds 15+ requirement checkboxes   |
| `/estimate`        | Estimate complexity          | "Medium complexity (4-8 hours)"   |
| `/relate`          | Find related context         | Lists related files and issues    |
| `/label bug, high` | Add custom labels            | Adds specified labels             |
| `/assign @user`    | Assign to someone            | Assigns issue to user             |

## 📚 Learn More

- **[Complete Guide](GUIDE.md)** - Full documentation with examples
- **[README](README.md)** - Overview and architecture
- **[Configuration](../../cloud-agent-config.yml)** - Customize behavior

## 💡 Pro Tips

1. **Use Templates** - They're optimized for Cloud Agent
2. **Be Descriptive** - More context = better automation
3. **Batch Commands** - Use multiple commands in one comment
4. **Check History** - Use `/relate` to learn from past issues

## 🚀 Try It Now!

1. [Create your first automated issue →](../../issues/new/choose)
2. Add a comment with `/estimate` to see it in action
3. Try `/breakdown` on a complex feature
4. Use `/accept` to generate acceptance criteria

**Cloud Agent is ready to help! 🤖**

---

**Questions?** See the [Full Guide](GUIDE.md) or [open an issue](../../issues/new).
