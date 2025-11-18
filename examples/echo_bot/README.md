# Echo Bot Example

The simplest possible bot built with `telegram-bot-stack`. This bot echoes back any message it receives.

## Features

- ✅ Echoes back all text messages
- ✅ User management (inherited from BotBase)
- ✅ Admin system (inherited from BotBase)
- ✅ Built-in commands: `/start`, `/my_id`
- ✅ Admin commands: `/list_users`, `/list_admins`, `/add_admin`, `/remove_admin`

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
cd examples/echo_bot
python bot.py
```

Or with explicit token:

```bash
export BOT_TOKEN="your_token"
python bot.py
```

## Trying the Bot

1. Start the bot: `/start`
2. Send any message: `Hello!`
3. Bot replies: `🔊 You said: Hello!`
4. Check your ID: `/my_id`

## Code Overview

The entire bot is just ~30 lines of actual code:

```python
class EchoBot(BotBase):
    def get_welcome_message(self) -> str:
        return "Welcome to Echo Bot! I echo everything you say."

    def register_handlers(self):
        super().register_handlers()
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo_message)
        )

    async def echo_message(self, update, context):
        user_message = update.message.text
        await update.message.reply_text(f"🔊 You said: {user_message}")
```

All user management, admin system, and common commands are inherited from `BotBase`!

## Storage

Bot data (users, admins) is stored in `./data/` directory as JSON files:

- `data/bot_users.json` - List of registered users
- `data/bot_admins.json` - List of administrators

## Next Steps

- Check out `counter_bot` for state management example
- Check out `quit_smoking_bot` for a real-world bot example
- Read the [framework documentation](../../README.md)
