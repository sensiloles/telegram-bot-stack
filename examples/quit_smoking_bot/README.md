# Quit Smoking Bot Example

A real-world bot that tracks your smoke-free period and calculates a growing prize fund. This demonstrates how to build a complete bot with custom business logic using `telegram-bot-stack`.

## Features

- ✅ Track smoke-free period (years, months, days)
- ✅ Calculate growing prize fund
- ✅ Motivational quotes
- ✅ Scheduled notifications (23rd of each month)
- ✅ User and admin management (inherited)
- ✅ Persistent storage across restarts

## Commands

**User Commands:**

- `/start` - Register and see welcome message
- `/status` - Show current smoke-free status and prize fund
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

2. Configure the bot:

Edit `config.py` to set your start date and prize fund settings:

```python
# Start date - when you quit smoking
START_YEAR = 2025
START_MONTH = 1
NOTIFICATION_DAY = 23

# Prize fund settings
MONTHLY_AMOUNT = 5000  # starting amount in rubles
PRIZE_FUND_INCREASE = 5000  # increase per month
MAX_PRIZE_FUND = 100000  # maximum cap
```

3. Create `.env` file in this directory:

```bash
BOT_TOKEN=your_bot_token_here
TZ=Europe/Moscow  # Optional: set your timezone
```

Get your bot token from [@BotFather](https://t.me/BotFather) on Telegram.

## Usage

Run the bot:

```bash
cd examples/quit_smoking_bot
python bot.py
```

Or with explicit token:

```bash
export BOT_TOKEN="your_token"
python bot.py
```

## Example Output

```
User: /status
Bot: 📊 Your current status:

     🚭 Smoke-free period: 0 years, 2 months, 15 days
     💰 Current prize fund: 15000 rubles
     📅 Next increase: 23.04.2025 at 21:58 (Europe/Moscow)
     ➕ Next increase amount: +5000 rubles

     💭 Each day without cigarettes is a victory over yourself. - Mark Twain
```

## Code Architecture

The bot is organized into several modules:

### config.py

Contains all configuration:

- Start date and timezone
- Prize fund settings
- Message templates
- Notification schedule

### utils.py

Helper functions:

- `calculate_period()` - Calculate time elapsed
- `calculate_prize_fund()` - Calculate prize based on months

### quotes_manager.py

Manages motivational quotes:

- Loads quotes from JSON file
- Provides random quote selection
- Extends quote list for 20 years

### status_manager.py

Core business logic:

- Calculates smoke-free period
- Computes prize fund
- Generates formatted status messages
- Determines next notification date

### bot.py

Main bot implementation:

- Extends `BotBase` from telegram-bot-stack
- Registers command handlers
- Implements custom `/status` command
- Overrides framework hooks

## Customization

### 1. Change Start Date

Edit `config.py`:

```python
START_YEAR = 2024
START_MONTH = 6
NOTIFICATION_DAY = 15  # Your quit date
```

### 2. Modify Prize Fund

Edit `config.py`:

```python
MONTHLY_AMOUNT = 10000  # Start with 10,000
PRIZE_FUND_INCREASE = 10000  # Add 10,000 each month
MAX_PRIZE_FUND = 200000  # Cap at 200,000
```

### 3. Add Custom Quotes

Edit `data/quotes.json`:

```json
[
  "Your custom motivational quote here",
  "Another inspiring message",
  "Keep going, you're doing great!"
]
```

### 4. Add Scheduled Notifications

Extend the bot to send automatic reminders:

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

class QuitSmokingBot(BotBase):
    def __init__(self, storage):
        super().__init__(storage)
        self.scheduler = AsyncIOScheduler()

    async def send_monthly_notification(self):
        """Send status to all users monthly."""
        status = self.status_manager.get_status_info()
        for user_id in self.user_manager.get_all_users():
            await self.application.bot.send_message(
                chat_id=user_id,
                text=status
            )
```

## Storage

Bot data is stored in `./data/` directory:

- `bot_users.json` - Registered users
- `bot_admins.json` - Administrators
- `quotes.json` - Motivational quotes

## Framework Integration

This bot demonstrates key telegram-bot-stack features:

### Extending BotBase

```python
class QuitSmokingBot(BotBase):
    def __init__(self, storage):
        super().__init__(storage, bot_name="Quit Smoking Bot")
        # Add custom managers
        self.quotes_manager = QuotesManager(storage)
        self.status_manager = StatusManager(self.quotes_manager)
```

### Overriding Hooks

```python
def get_welcome_message(self) -> str:
    """Custom welcome message."""
    return "Welcome to Quit Smoking Bot!"

async def get_user_status(self, user_id: int) -> str:
    """Custom status for each user."""
    return self.status_manager.get_status_info(str(user_id))
```

### Adding Custom Commands

```python
def register_handlers(self):
    super().register_handlers()  # Register base commands
    self.application.add_handler(CommandHandler("status", self.status))
```

## Next Steps

- Add user-specific quit dates (multi-user support)
- Implement achievement system (milestones)
- Add statistics and progress graphs
- Create scheduled notifications
- Integrate with external services (health tracking)

## Credits

This bot is a real-world example migrated to telegram-bot-stack framework, demonstrating how to build production-ready bots with minimal code.
