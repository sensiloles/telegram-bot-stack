# Counter Bot

A Telegram bot that demonstrates **state management** with persistent storage.

## Features

- 📊 Counts messages per user
- 💾 Persists data using JSONStorage
- 🔄 Reset counter command
- 👤 Per-user state tracking

## Quick Start

1. **Get your bot token** from [@BotFather](https://t.me/BotFather)

2. **Create `.env` file** with your token:

   ```bash
   echo "BOT_TOKEN=your_token_here" > .env
   ```

3. **Install dependencies**:

   ```bash
   pip install telegram-bot-stack
   ```

4. **Run the bot**:
   ```bash
   python bot.py
   ```

## Commands

- `/start` - Show welcome message
- `/count` - Show your message count
- `/reset` - Reset your counter
- `/help` - Get help

## How It Works

The bot uses `JSONStorage` to persist user data between restarts:

```python
# Initialize storage
storage = JSONStorage(data_dir="data")
bot = CounterBot(storage=storage)

# Get user data
count = await self.storage.get_user_data(user_id, "message_count", 0)

# Set user data
await self.storage.set_user_data(user_id, "message_count", count + 1)
```

Data is stored in `data/users.json` and persists across bot restarts.

## Project Structure

```
counter-bot/
├── bot.py              # Main bot implementation
├── .env                # Environment variables (not in git)
├── .env.example        # Example environment variables
├── data/               # Storage directory (created automatically)
│   └── users.json      # User data (created automatically)
└── README.md           # This file
```

## Learn More

- [Storage Guide](https://github.com/sensiloles/telegram-bot-stack/blob/main/docs/storage_guide.md)
- [API Reference](https://github.com/sensiloles/telegram-bot-stack/blob/main/docs/api_reference.md)

## License

MIT
