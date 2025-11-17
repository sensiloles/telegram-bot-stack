## 📝 Description

<!-- Describe your changes in detail -->

## 🎯 Type of Change

<!-- Mark with 'x' the type of change -->

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [ ] 🔧 Chore (maintenance, dependencies, etc.)
- [ ] ⚡ Performance improvement
- [ ] 🧪 Tests

## 🔗 Related Issue

<!-- Link to related issue(s) -->

Closes #
Related to #

## 🧪 Testing

<!-- Describe the tests you ran to verify your changes -->

- [ ] All existing tests pass
- [ ] Added new tests for new functionality
- [ ] Coverage remains ≥80%
- [ ] Manual testing completed

### Test Commands

```bash
# Commands used to test changes
pytest
pytest --cov=telegram_bot_stack
```

## 📋 Checklist

<!-- Mark completed items with 'x' -->

### Code Quality

- [ ] My code follows the project's style guide (passes `ruff check`)
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] My changes generate no new warnings or errors

### Testing

- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Test coverage is maintained or improved (≥80%)

### Documentation

- [ ] I have updated the documentation accordingly
- [ ] I have updated the relevant docstrings
- [ ] I have added examples if needed
- [ ] README.md is updated (if applicable)

### Commits

- [ ] My commits follow [Conventional Commits](https://www.conventionalcommits.org/) format
- [ ] Each commit is atomic and has a clear purpose
- [ ] Commit messages are descriptive

**Examples:**

```bash
feat(storage): add Redis backend support
fix(auth): resolve token validation issue
docs: update API reference
```

### Version Impact

<!-- Indicate expected version bump based on changes -->

- [ ] 🔴 **MAJOR** - Breaking changes (1.0.0 → 2.0.0)
- [ ] 🟡 **MINOR** - New features (0.1.0 → 0.2.0)
- [ ] 🟢 **PATCH** - Bug fixes (0.1.0 → 0.1.1)
- [ ] ⚪ **NONE** - No release (docs/chore only)

## 📸 Screenshots (if applicable)

<!-- Add screenshots to help explain your changes -->

## 🔄 Migration Guide (if breaking change)

<!-- If this is a breaking change, describe migration steps -->

**Before:**

```python
# Old API usage
```

**After:**

```python
# New API usage
```

## 💡 Additional Context

<!-- Add any other context about the PR here -->

## ⚠️ Breaking Changes (if any)

<!-- List all breaking changes with migration path -->

- **Change:** Description
- **Reason:** Why was this change necessary?
- **Migration:** How should users update their code?

---

<!--
Thank you for your contribution! 🎉
Please ensure all checkboxes are marked before requesting review.
-->
