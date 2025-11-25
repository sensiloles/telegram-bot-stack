# Menu Bot

A Telegram bot that demonstrates **interactive inline keyboards** and menu navigation.

## Features

- 🎛️ Interactive inline keyboard menus
- 🔄 Dynamic message updates
- 📱 Multi-level navigation
- ⚡ Callback query handling

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

- `/start` - Show main menu
- `/menu` - Show main menu
- `/help` - Get help

## How It Works

The bot uses inline keyboards for interactive menus:

```python
# Create inline keyboard
keyboard = [
    [
        InlineKeyboardButton("Option 1", callback_data="opt1"),
        InlineKeyboardButton("Option 2", callback_data="opt2"),
    ],
]
reply_markup = InlineKeyboardMarkup(keyboard)

# Send message with keyboard
await update.message.reply_text("Choose:", reply_markup=reply_markup)

# Handle button clicks
async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Remove loading state

    if query.data == "opt1":
        await query.edit_message_text("You chose Option 1!")
```

## Menu Structure

```
Main Menu
├── Features
│   ├── Feature 1
│   ├── Feature 2
│   └── Back
├── About
│   └── Back
├── Settings
│   ├── Notifications
│   ├── Language
│   └── Back
└── Help
    └── Back
```

## Learn More

- [Inline Keyboards Guide](https://docs.python-telegram-bot.org/en/stable/telegram.inlinekeyboardbutton.html)
- [Callback Queries](https://docs.python-telegram-bot.org/en/stable/telegram.callbackquery.html)

## License

MIT
