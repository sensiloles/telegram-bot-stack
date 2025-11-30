# Poll Bot Example

A Telegram bot that demonstrates SQL storage usage with telegram-bot-stack. Users can create polls, vote, and view results.

## Features

- 📊 Create polls with multiple options
- 🗳️ Vote on active polls
- 📈 View real-time results with progress bars
- 📋 List all active polls
- 🔐 Admin-only poll management
- 💾 Persistent storage (SQLite/PostgreSQL)

## Storage Backend

This example demonstrates **SQL storage** (SQLite or PostgreSQL), which is ideal for:

- Production deployments
- Multiple concurrent users
- Data persistence and integrity
- Scalable poll management

## Installation

1. Install telegram-bot-stack with database support:

```bash
pip install telegram-bot-stack[database]
```

2. For PostgreSQL support (optional):

```bash
pip install telegram-bot-stack[database,postgres]
```

## Configuration

### Using SQLite (Default)

Create a `.env` file:

```bash
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_user_id
STORAGE_BACKEND=sqlite
DATABASE_URL=sqlite:///poll_bot.db  # Will be created in data/ directory
```

### Using PostgreSQL (Production)

Create a `.env` file:

```bash
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_user_id
STORAGE_BACKEND=postgres
DATABASE_URL=postgresql://user:password@localhost/poll_bot_db
```

### Using JSON (Fallback)

If SQL is not available, the bot falls back to JSON storage:

```bash
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_user_id
STORAGE_BACKEND=json
```

## Running the Bot

```bash
# Load environment variables
source .env  # or: export $(cat .env | xargs)

# Run the bot
python examples/poll_bot/bot.py
```

Or directly:

```bash
BOT_TOKEN=your_token ADMIN_ID=your_id python examples/poll_bot/bot.py
```

## Usage

### User Commands

**Create a poll:**

```
/create_poll What's your favorite color? | Red | Blue | Green | Yellow
```

**Vote on a poll:**

```
/vote 1 2
```

(Vote for option 2 in poll 1)

**View results:**

```
/results 1
```

**List all polls:**

```
/list_polls
```

### Admin Commands

**Delete a poll:**

```
/delete_poll 1
```

**Clear all polls:**

```
/clear_polls
```

## Example Session

```
User: /start
Bot: Welcome to Poll Bot! 🗳️
     Create and vote on polls with your friends.
     ...

User: /create_poll What's your favorite language? | Python | JavaScript | Go
Bot: ✅ Poll created! ID: 1

     ❓ What's your favorite language?

     1. Python
     2. JavaScript
     3. Go

     Vote with: /vote 1 <option_number>

User: /vote 1 1
Bot: ✅ Your vote has been recorded!

     You voted for: Python

     View results with: /results 1

User: /results 1
Bot: 📊 Poll Results (ID: 1)

     ❓ What's your favorite language?

     1. Python
        ████████████████████ 1 votes (100.0%)

     2. JavaScript
        ░░░░░░░░░░░░░░░░░░░░ 0 votes (0.0%)

     3. Go
        ░░░░░░░░░░░░░░░░░░░░ 0 votes (0.0%)

     Total votes: 1
     Created by: @username
```

## Storage Structure

The bot uses two storage keys:

### Polls (`polls`)

```json
{
  "1": {
    "question": "What's your favorite language?",
    "options": ["Python", "JavaScript", "Go"],
    "created_by": 123456789,
    "created_by_username": "username"
  },
  "2": {
    "question": "Best framework?",
    "options": ["Django", "Flask", "FastAPI"],
    "created_by": 123456789,
    "created_by_username": "username"
  }
}
```

### Votes (`votes`)

```json
{
  "1": {
    "123456789": 1,
    "987654321": 2
  },
  "2": {
    "123456789": 3
  }
}
```

## Database Schema (SQL)

When using SQL storage, data is stored in the `storage` table:

| key   | data                     | created_at          | updated_at          |
| ----- | ------------------------ | ------------------- | ------------------- |
| polls | {"1": {...}, "2": {...}} | 2024-01-01 10:00:00 | 2024-01-01 10:30:00 |
| votes | {"1": {...}, "2": {...}} | 2024-01-01 10:05:00 | 2024-01-01 10:35:00 |

## Switching Storage Backends

The beauty of telegram-bot-stack is that you can switch backends without changing code:

```python
# Development with JSON
storage = create_storage("json", base_dir="data")

# Production with SQLite (database will be created in data/ directory)
storage = create_storage("sqlite", database_url="sqlite:///poll_bot.db")

# Production with PostgreSQL
storage = create_storage("postgres", database_url="postgresql://...")

# All work with the same bot code!
bot = PollBot(token=token, storage=storage, admin_ids=admin_ids)
```

## Migration

If you started with JSON and want to migrate to SQL:

```bash
# Migrate data from JSON to SQLite (database will be created in data/ directory)
python scripts/migrate_json_to_sql.py \
    --json-dir data \
    --database-url sqlite:///poll_bot.db

# Verify migration
python scripts/migrate_json_to_sql.py \
    --json-dir data \
    --database-url sqlite:///poll_bot.db \
    --verify
```

## Production Deployment

### Using SQLite

Good for small to medium bots:

```bash
# Set environment variables
export BOT_TOKEN=your_token
export ADMIN_ID=your_id
export STORAGE_BACKEND=sqlite
export DATABASE_URL=sqlite:///poll_bot.db

# Run bot
python examples/poll_bot/bot.py
```

### Using PostgreSQL

Recommended for large-scale deployments:

```bash
# Set environment variables
export BOT_TOKEN=your_token
export ADMIN_ID=your_id
export STORAGE_BACKEND=postgres
export DATABASE_URL=postgresql://user:pass@localhost/poll_bot_db

# Run bot
python examples/poll_bot/bot.py
```

## Extending the Bot

This example can be extended with:

- Poll expiration dates
- Multiple choice voting
- Anonymous polls
- Poll categories
- Vote history per user
- Poll statistics and analytics
- Export results to CSV

## See Also

- [Storage Guide](../../docs/storage_guide.md) - Complete storage documentation
- [API Reference](../../docs/api_reference.md) - Framework API
- [Counter Bot](../counter_bot/) - Simpler example with JSON storage
- [Echo Bot](../echo_bot/) - Minimal example
