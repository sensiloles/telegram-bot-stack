# Advanced Bot

A production-ready Telegram bot demonstrating **all features and best practices**.

## Features

- 💾 **SQL Storage** - Production-ready persistent storage
- 📊 **User Statistics** - Track user activity and engagement
- 👮 **Admin System** - Admin-only commands and features
- 🛡️ **Error Handling** - Graceful error handling and logging
- 📝 **Message Tracking** - Track all messages and commands
- 🔒 **Security** - Environment-based configuration

## Quick Start

1. **Get your bot token** from [@BotFather](https://t.me/BotFather)

2. **Create `.env` file** with your token and admin IDs:

   ```bash
   cat > .env << EOF
   BOT_TOKEN=your_token_here
   ADMIN_IDS=123456789,987654321
   EOF
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

### User Commands

- `/start` - Show welcome message
- `/stats` - Show your statistics
- `/help` - Get help

### Admin Commands

- `/admin` - Show admin panel
- `/broadcast` - Send message to all users

## Configuration

### Environment Variables

Create a `.env` file:

```bash
# Required: Bot token from @BotFather
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Optional: Admin user IDs (comma-separated)
ADMIN_IDS=123456789,987654321
```

### Getting Your User ID

1. Start a chat with [@userinfobot](https://t.me/userinfobot)
2. Send any message
3. Copy your user ID
4. Add it to `ADMIN_IDS` in `.env`

## Architecture

### Storage

Uses `SQLStorage` for production-ready persistent storage:

```python
storage = SQLStorage(db_path="bot.db")
bot = AdvancedBot(storage=storage, admin_ids=admin_ids)
```

Data is stored in `bot.db` (SQLite) and persists across restarts.

### Error Handling

Custom error handler logs errors and notifies users:

```python
async def error_handler(self, update, context):
    logger.error("Exception:", exc_info=context.error)
    await update.effective_message.reply_text(
        "❌ An error occurred. Please try again."
    )
```

### Statistics Tracking

Tracks per-user statistics:

- Message count
- Command count
- First seen timestamp
- Admin status

## Project Structure

```
advanced-bot/
├── bot.py              # Main bot implementation
├── .env                # Environment variables (not in git)
├── .env.example        # Example environment variables
├── bot.db              # SQLite database (created automatically)
└── README.md           # This file
```

## Production Deployment

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

### Using systemd

Create `/etc/systemd/system/telegram-bot.service`:

```ini
[Unit]
Description=Telegram Bot
After=network.target

[Service]
Type=simple
User=bot
WorkingDirectory=/opt/telegram-bot
ExecStart=/opt/telegram-bot/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

## Monitoring

### Logs

The bot logs to stdout. Redirect to file:

```bash
python bot.py > bot.log 2>&1
```

### Health Check

Check if bot is running:

```bash
ps aux | grep bot.py
```

Check database:

```bash
sqlite3 bot.db "SELECT COUNT(*) FROM users;"
```

## Security Best Practices

- ✅ Store tokens in `.env` (never commit)
- ✅ Use admin IDs from environment
- ✅ Validate user input
- ✅ Handle errors gracefully
- ✅ Log security events
- ✅ Use SQL storage (prevents data loss)

## Learn More

- [Storage Guide](https://github.com/sensiloles/telegram-bot-stack/blob/main/docs/storage_guide.md)
- [Admin System](https://github.com/sensiloles/telegram-bot-stack/blob/main/docs/api_reference.md#admin-system)
- [Error Handling](https://docs.python-telegram-bot.org/en/stable/telegram.ext.application.html#telegram.ext.Application.add_error_handler)

## License

MIT
