# Reminder Bot Example

A Telegram bot that demonstrates scheduler usage with telegram-bot-stack. Users can create reminders with natural language and receive notifications at the right time.

## Features

- ⏰ Create reminders with natural language
- 📋 List active reminders
- 🗑️ Delete reminders
- 🔔 Automatic notifications
- 🧹 Automatic cleanup of completed reminders
- 💾 Persistent storage

## What This Example Demonstrates

- **APScheduler Integration**: Using `python-telegram-bot`'s job queue
- **Natural Language Parsing**: Simple time parsing ("in 30m", "at 14:30")
- **User-Specific Notifications**: Sending messages to specific users
- **Scheduled Task Management**: Creating, listing, and deleting scheduled tasks
- **Storage Patterns**: Storing reminder metadata

## Installation

Install telegram-bot-stack:

```bash
pip install telegram-bot-stack
```

## Configuration

Create a `.env` file or set environment variables:

```bash
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_user_id
STORAGE_BACKEND=json
STORAGE_DIR=data
```

## Running the Bot

```bash
# Load environment variables
source .env  # or: export $(cat .env | xargs)

# Run the bot
python examples/reminder_bot/bot.py
```

Or directly:

```bash
BOT_TOKEN=your_token ADMIN_ID=your_id python examples/reminder_bot/bot.py
```

## Usage

### User Commands

**Create a reminder:**

```
/remind in 30m Check the oven
/remind in 2h Call mom
/remind at 15:00 Meeting with team
```

**List your reminders:**

```
/reminders
```

**Delete a reminder:**

```
/delete_reminder r1
```

### Admin Commands

**Clear all reminders:**

```
/clear_reminders
```

## Time Formats

The bot supports several natural language time formats:

| Format     | Example    | Description                                    |
| ---------- | ---------- | ---------------------------------------------- |
| `in Xm`    | `in 30m`   | In X minutes                                   |
| `in Xh`    | `in 2h`    | In X hours                                     |
| `in Xd`    | `in 1d`    | In X days                                      |
| `at HH:MM` | `at 14:30` | At specific time today (or tomorrow if passed) |

## Example Session

```
User: /start
Bot: Welcome to Reminder Bot! ⏰
     I'll help you remember important things.
     ...

User: /remind in 30m Check the oven
Bot: ✅ Reminder created! ID: r1

     📝 Check the oven
     ⏰ In 30m (14:30)

User: /remind in 2h Call mom
Bot: ✅ Reminder created! ID: r2

     📝 Call mom
     ⏰ In 2h (16:00)

User: /reminders
Bot: 📋 Your Active Reminders:

     ID: r1
     📝 Check the oven
     ⏰ In 28m (14:30)

     ID: r2
     📝 Call mom
     ⏰ In 1h 58m (16:00)

     Delete with: /delete_reminder <id>

[30 minutes later]

Bot: ⏰ Reminder:

     Check the oven

User: /reminders
Bot: 📋 Your Active Reminders:

     ID: r2
     📝 Call mom
     ⏰ In 1h 28m (16:00)

     Delete with: /delete_reminder <id>
```

## Storage Structure

The bot stores reminders in the following format:

```json
{
  "123456789": {
    "r1": {
      "message": "Check the oven",
      "time": "2024-01-01T14:30:00",
      "created_at": "2024-01-01T14:00:00"
    },
    "r2": {
      "message": "Call mom",
      "time": "2024-01-01T16:00:00",
      "created_at": "2024-01-01T14:00:00"
    }
  }
}
```

## How It Works

### 1. Time Parsing

The bot uses regex patterns to parse natural language time expressions:

```python
def _parse_time(self, time_str: str) -> datetime | None:
    # "in 5m" -> 5 minutes from now
    # "in 2h" -> 2 hours from now
    # "at 14:30" -> today at 14:30 (or tomorrow if passed)
    ...
```

### 2. Scheduling

Uses `python-telegram-bot`'s job queue (powered by APScheduler):

```python
context.job_queue.run_once(
    self._send_reminder,
    when=target_time,
    data={"user_id": user_id, "reminder_id": reminder_id, "message": message},
    name=f"reminder_{user_id}_{reminder_id}",
)
```

### 3. Notification

When the scheduled time arrives, the bot sends a message:

```python
async def _send_reminder(self, context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    user_id = job.data["user_id"]
    message = job.data["message"]

    await context.bot.send_message(
        chat_id=user_id,
        text=f"⏰ Reminder:\n\n{message}",
    )
```

### 4. Cleanup

After sending the reminder, it's automatically removed from storage.

## Extending the Bot

This example can be extended with:

- **Timezone support**: Handle different user timezones
- **Recurring reminders**: Daily, weekly, monthly reminders
- **More time formats**: "tomorrow at 9am", "next Monday"
- **Reminder categories**: Work, personal, etc.
- **Snooze functionality**: Postpone reminders
- **Reminder history**: Track completed reminders
- **Natural language processing**: More flexible time parsing

## Advanced Time Parsing

For production bots, consider using libraries like:

- `dateparser` - Parse dates in almost any string format
- `parsedatetime` - Parse human-readable date/time text
- `arrow` - Better dates and times for Python

Example with `dateparser`:

```python
import dateparser

def _parse_time(self, time_str: str) -> datetime | None:
    return dateparser.parse(time_str, settings={'PREFER_DATES_FROM': 'future'})

# Now supports:
# "tomorrow at 9am"
# "next Monday"
# "in 2 weeks"
# "December 25th at noon"
```

## Production Considerations

### Persistence

Reminders are stored in the storage backend, but scheduled jobs are in-memory. When the bot restarts:

1. Load reminders from storage
2. Reschedule all pending reminders

Add this to `__init__`:

```python
def __init__(self, token: str, storage, admin_ids: List[int]):
    super().__init__(token=token, storage=storage, admin_ids=admin_ids)
    self._restore_reminders()

def _restore_reminders(self):
    """Restore reminders from storage after restart."""
    reminders = self._get_reminders()
    now = datetime.now()

    for user_id, user_reminders in reminders.items():
        for reminder_id, reminder in list(user_reminders.items()):
            target_time = datetime.fromisoformat(reminder["time"])

            if target_time > now:
                # Reschedule
                self.application.job_queue.run_once(
                    self._send_reminder,
                    when=target_time,
                    data={
                        "user_id": int(user_id),
                        "reminder_id": reminder_id,
                        "message": reminder["message"],
                    },
                    name=f"reminder_{user_id}_{reminder_id}",
                )
            else:
                # Remove expired reminders
                del user_reminders[reminder_id]
```

### Rate Limiting

Add rate limiting to prevent spam:

```python
from telegram_bot_stack.decorators import rate_limit

@rate_limit(max_calls=10, period=60)  # 10 reminders per minute
async def create_reminder(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    ...
```

### User Limits

Limit number of active reminders per user:

```python
MAX_REMINDERS_PER_USER = 50

async def create_reminder(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_reminders = self._get_reminders().get(str(user_id), {})

    if len(user_reminders) >= MAX_REMINDERS_PER_USER:
        await update.message.reply_text(
            f"❌ You have reached the maximum of {MAX_REMINDERS_PER_USER} active reminders.\n"
            "Please delete some reminders first."
        )
        return
    ...
```

## See Also

- [Counter Bot](../counter_bot/) - State management example
- [Poll Bot](../poll_bot/) - SQL storage example
- [Echo Bot](../echo_bot/) - Minimal example
- [API Reference](../../docs/api_reference.md) - Framework API
- [Storage Guide](../../docs/storage_guide.md) - Storage backends
