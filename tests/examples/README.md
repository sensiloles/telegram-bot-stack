# Example Bots Tests

This directory contains comprehensive tests for all example bots in the `examples/` directory.

## Test Structure

Each bot has its own dedicated test file:

- `test_counter_bot.py` - Tests for Counter Bot
- `test_echo_bot.py` - Tests for Echo Bot
- `test_menu_bot.py` - Tests for Menu Bot
- `test_poll_bot.py` - Tests for Poll Bot
- `test_quit_smoking_bot.py` - Tests for Quit Smoking Bot
- `test_reminder_bot.py` - Tests for Reminder Bot
- `test_examples.py` - General integration tests for all bots

## What is Tested

Each bot test suite verifies:

1. **Module Import** - Bot module can be imported without errors
2. **Class Existence** - Bot class exists and has correct name
3. **Initialization** - Bot can be initialized with new API (`storage` and `bot_name` parameters)
4. **Required Attributes** - Bot has `storage`, `user_manager`, `admin_manager`, `application`
5. **Handler Registration** - Bot has `register_handlers` method
6. **Bot-Specific Features** - Storage keys, custom methods, managers, etc.

## Running Tests

### Run all example bot tests:

```bash
pytest tests/examples/ -v
```

### Run specific bot tests:

```bash
pytest tests/examples/test_counter_bot.py -v
pytest tests/examples/test_echo_bot.py -v
pytest tests/examples/test_menu_bot.py -v
pytest tests/examples/test_poll_bot.py -v
pytest tests/examples/test_quit_smoking_bot.py -v
pytest tests/examples/test_reminder_bot.py -v
```

### Run integration tests:

```bash
pytest tests/examples/test_examples.py -v
```

## Test Results

Current status: **71 tests, all passing** ✅

- Counter Bot: 6 tests
- Echo Bot: 6 tests
- Menu Bot: 6 tests
- Poll Bot: 7 tests
- Quit Smoking Bot: 11 tests
- Reminder Bot: 7 tests
- Integration tests: 28 tests

## Purpose

These tests ensure that:

1. All example bots use the **new unified API**
2. All bots can be **imported and initialized** correctly
3. All bots have **required framework attributes**
4. All bots implement **proper handler registration**
5. Changes to the framework don't break example bots

## Integration with CI/CD

These tests are part of the main test suite and run automatically on:

- Every commit
- Every pull request
- Before releases

The tests help maintain high quality of example code that users rely on for learning the framework.
