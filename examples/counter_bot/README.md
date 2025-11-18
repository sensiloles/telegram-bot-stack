# Counter Bot Example

A bot that maintains a counter for each user, demonstrating state management with `telegram-bot-stack`.

## Features

- ✅ Individual counter for each user
- ✅ Persistent storage (survives restarts)
- ✅ Increment/decrement operations
- ✅ Reset functionality
- ✅ User and admin management (inherited)

## Commands

**User Commands:**

- `/start` - Register and see welcome message
- `/increment` - Add 1 to your counter
- `/decrement` - Subtract 1 from your counter
- `/count` - Show your current count
- `/reset` - Reset your counter to 0
- `/my_id` - Show your Telegram ID

**Admin Commands:**

- `/list_users` - List all registered users
- `/list_admins` - List all administrators
- `/add_admin USER_ID` - Add a new admin
- `/remove_admin USER_ID` - Remove an admin

## Installation

1. Install telegram-bot-stack:

```bash
# From the project root
pip install -e .
```

2. Create `.env` file in this directory:

```bash
BOT_TOKEN=your_bot_token_here
```

Get your bot token from [@BotFather](https://t.me/BotFather) on Telegram.

## Usage

Run the bot:

```bash
cd examples/counter_bot
python bot.py
```

Or with explicit token:

```bash
export BOT_TOKEN="your_token"
python bot.py
```

## Example Session

```
User: /start
Bot: 👋 Welcome to Counter Bot!
     I keep track of a counter for each user.
     Commands: /increment, /decrement, /count, /reset

User: /count
Bot: 🔢 Your current count: 0

User: /increment
Bot: ➕ Counter incremented!
     Your count: 0 → 1

User: /increment
Bot: ➕ Counter incremented!
     Your count: 1 → 2

User: /count
Bot: 🔢 Your current count: 2

User: /decrement
Bot: ➖ Counter decremented!
     Your count: 2 → 1

User: /reset
Bot: 🔄 Counter reset!
     Previous count: 1
     New count: 0
```

## Code Overview

Key concepts demonstrated:

### 1. Custom State Management

```python
def _get_user_count(self, user_id: int) -> int:
    """Get counter value for a specific user."""
    counters = self._get_counters()
    return counters.get(str(user_id), 0)

def _set_user_count(self, user_id: int, value: int) -> bool:
    """Set counter value for a specific user."""
    counters = self._get_counters()
    counters[str(user_id)] = value
    return self._save_counters(counters)
```

### 2. Custom Commands

```python
async def increment(self, update, context):
    user_id = update.effective_user.id
    current = self._get_user_count(user_id)
    new_value = current + 1
    self._set_user_count(user_id, new_value)
    await update.message.reply_text(f"Your count: {current} → {new_value}")
```

### 3. Storage Integration

The bot uses the framework's storage system to persist user counters across restarts.

## Storage

Bot data is stored in `./data/` directory as JSON files:

- `data/bot_users.json` - List of registered users
- `data/bot_admins.json` - List of administrators
- `data/user_counters.json` - Counter values for each user

Example `user_counters.json`:

```json
{
  "123456789": 5,
  "987654321": 12
}
```

## Next Steps

- Extend with more complex state (e.g., history of operations)
- Add leaderboard showing users with highest counts
- Implement counter limits or goals
- Check out `quit_smoking_bot` for a real-world example
