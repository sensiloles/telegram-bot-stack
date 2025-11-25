# Echo Bot - Basic Template

A simple Telegram bot that echoes back user messages.

## Quick Start

1. **Get your bot token** from [@BotFather](https://t.me/BotFather)

2. **Create `.env` file**:

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

## Features

- Echoes back all user messages
- Simple welcome message on /start
- Built with telegram-bot-stack

## Customization

Edit `bot.py` to customize:

- Welcome message in `get_welcome_message()`
- Add custom commands
- Change storage backend (JSON, SQL, Redis)

## Documentation

- [telegram-bot-stack](https://github.com/sensiloles/telegram-bot-stack)
- [python-telegram-bot](https://docs.python-telegram-bot.org/)
