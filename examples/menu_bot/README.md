# Menu Bot Example

A Telegram bot that demonstrates inline keyboards with telegram-bot-stack. Users can interact with menus, toggle settings, and browse paginated lists.

## Features

- 🎛️ Interactive main menu
- ⚙️ Settings menu with toggles
- 📋 Paginated item list
- ✅ Confirmation dialogs
- 🔄 Dynamic keyboard updates
- 💾 Persistent user settings

## What This Example Demonstrates

- **Inline Keyboards**: Creating interactive button menus
- **Callback Queries**: Handling button presses
- **Navigation**: Multi-level menu navigation
- **State Management**: Toggle buttons and user preferences
- **Pagination**: Browsing large lists with prev/next buttons
- **Confirmation Dialogs**: Yes/No confirmations for actions

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
python examples/menu_bot/bot.py
```

Or directly:

```bash
BOT_TOKEN=your_token ADMIN_ID=your_id python examples/menu_bot/bot.py
```

## Usage

### User Commands

**Show main menu:**

```
/menu
```

**Show settings:**

```
/settings
```

**Browse items:**

```
/items
```

## Example Session

```
User: /start
Bot: Welcome to Menu Bot! 🎛️
     I demonstrate interactive menus using inline keyboards.
     ...

User: /menu
Bot: 🎛️ Main Menu

     Choose an option:

     [⚙️ Settings]
     [📋 Browse Items]
     [ℹ️ About]
     [❓ Help]

User: [clicks "⚙️ Settings"]
Bot: ⚙️ Settings

     Adjust your preferences:

     [🔔 Notifications: ON]
     [☀️ Dark Mode: OFF]
     [🌐 Language: EN]
     [🔙 Back to Menu]

User: [clicks "🔔 Notifications: ON"]
Bot: [Updates keyboard]
     [🔕 Notifications: OFF]
     [☀️ Dark Mode: OFF]
     [🌐 Language: EN]
     [🔙 Back to Menu]

User: [clicks "🔙 Back to Menu"]
Bot: 🎛️ Main Menu

     Choose an option:
     ...

User: [clicks "📋 Browse Items"]
Bot: 📋 Browse Items

     Select an item:

     [1. Item 1]
     [2. Item 2]
     [3. Item 3]
     [4. Item 4]
     [5. Item 5]
     [📄 1/10] [➡️ Next]
     [🔙 Back to Menu]

User: [clicks "➡️ Next"]
Bot: [Updates keyboard with items 6-10]
     [6. Item 6]
     [7. Item 7]
     ...
     [⬅️ Prev] [📄 2/10] [➡️ Next]

User: [clicks "7. Item 7"]
Bot: 📦 Item Details

     Name: Item 7
     Index: 7

     Do you want to delete this item?

     [✅ Yes] [❌ No]

User: [clicks "✅ Yes"]
Bot: ✅ Item 'Item 7' deleted successfully!

     Use /items to browse remaining items.
```

## Storage Structure

### User Settings

```json
{
  "123456789": {
    "notifications": true,
    "dark_mode": false,
    "language": "en"
  }
}
```

### Items

```json
[
  "Item 1",
  "Item 2",
  "Item 3",
  ...
]
```

## How It Works

### 1. Building Keyboards

Inline keyboards are built using `InlineKeyboardButton` and `InlineKeyboardMarkup`:

```python
def _build_main_menu(self) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings")],
        [InlineKeyboardButton("📋 Browse Items", callback_data="menu_items")],
    ]
    return InlineKeyboardMarkup(keyboard)
```

### 2. Handling Callbacks

When a button is pressed, Telegram sends a callback query:

```python
async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Remove loading state

    if query.data == "menu_settings":
        # Show settings menu
        keyboard = self._build_settings_menu(user_id)
        await query.edit_message_text("⚙️ Settings", reply_markup=keyboard)
```

### 3. Toggle Buttons

Settings are stored and toggled:

```python
settings = self._get_user_settings(user_id)
settings["notifications"] = not settings["notifications"]
self._save_user_settings(user_id, settings)

# Update keyboard to reflect new state
keyboard = self._build_settings_menu(user_id)
await query.edit_message_reply_markup(reply_markup=keyboard)
```

### 4. Pagination

Large lists are split into pages:

```python
def _build_items_menu(self, page: int = 0) -> InlineKeyboardMarkup:
    items_per_page = 5
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    page_items = items[start_idx:end_idx]

    # Build keyboard with navigation buttons
    keyboard = []
    for item in page_items:
        keyboard.append([InlineKeyboardButton(item, callback_data=f"item_{idx}")])

    # Add prev/next buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"page_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"page_{page+1}"))

    keyboard.append(nav_buttons)
    return InlineKeyboardMarkup(keyboard)
```

## Keyboard Patterns

### Simple Menu

```python
keyboard = [
    [InlineKeyboardButton("Option 1", callback_data="opt1")],
    [InlineKeyboardButton("Option 2", callback_data="opt2")],
]
```

### Multiple Buttons Per Row

```python
keyboard = [
    [
        InlineKeyboardButton("Yes", callback_data="yes"),
        InlineKeyboardButton("No", callback_data="no"),
    ],
]
```

### URL Buttons

```python
keyboard = [
    [InlineKeyboardButton("Visit Website", url="https://example.com")],
]
```

### Mixed Buttons

```python
keyboard = [
    [InlineKeyboardButton("Callback", callback_data="cb")],
    [InlineKeyboardButton("URL", url="https://example.com")],
    [InlineKeyboardButton("Switch Inline", switch_inline_query="query")],
]
```

## Callback Data Patterns

### Simple Actions

```python
callback_data = "action"

if query.data == "action":
    # Handle action
```

### Parameterized Actions

```python
callback_data = f"action_{param}"

if query.data.startswith("action_"):
    param = query.data.split("_")[1]
    # Handle action with param
```

### Complex Data

For complex data, use JSON (but keep under 64 bytes):

```python
import json

callback_data = json.dumps({"action": "delete", "id": 123})

data = json.loads(query.data)
if data["action"] == "delete":
    item_id = data["id"]
```

## Best Practices

### 1. Always Answer Callback Queries

```python
await query.answer()  # Remove loading state
```

Or with notification:

```python
await query.answer("Action completed!", show_alert=True)
```

### 2. Keep Callback Data Short

Telegram limits callback data to 64 bytes:

```python
# Good
callback_data = f"del_{id}"

# Bad (if id is very long)
callback_data = f"delete_item_with_very_long_identifier_{id}"
```

### 3. Handle Errors Gracefully

```python
try:
    await query.edit_message_text(...)
except telegram.error.BadRequest as e:
    if "Message is not modified" in str(e):
        # Message content is the same, ignore
        pass
    else:
        raise
```

### 4. Use Meaningful Icons

Icons make menus more intuitive:

```python
"⚙️ Settings"
"📋 Items"
"✅ Confirm"
"❌ Cancel"
"⬅️ Back"
"➡️ Next"
```

## Extending the Bot

This example can be extended with:

- **User profiles**: Edit profile with inline keyboards
- **Shopping cart**: Add/remove items with buttons
- **Surveys**: Multi-step surveys with navigation
- **Games**: Interactive games with button controls
- **Admin panel**: Bot administration via menus
- **Search filters**: Toggle filters with buttons
- **Language selection**: Switch languages dynamically

## Production Considerations

### Rate Limiting

Prevent callback query spam:

```python
from telegram_bot_stack.decorators import rate_limit

@rate_limit(max_calls=10, period=1)
async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    ...
```

### Error Handling

Handle edge cases:

```python
async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    try:
        await query.answer()

        # Handle callback
        ...

    except telegram.error.BadRequest as e:
        logger.error(f"Error handling callback: {e}")
        await query.answer("An error occurred", show_alert=True)
```

### State Management

For complex flows, use context.user_data:

```python
async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    # Store state
    context.user_data["current_page"] = page
    context.user_data["selected_item"] = item_id

    # Use state
    current_page = context.user_data.get("current_page", 0)
```

### Keyboard Caching

Cache frequently used keyboards:

```python
class MenuBot(BotBase):
    def __init__(self, ...):
        super().__init__(...)
        self._main_menu_cache = None

    def _build_main_menu(self) -> InlineKeyboardMarkup:
        if self._main_menu_cache is None:
            self._main_menu_cache = InlineKeyboardMarkup([...])
        return self._main_menu_cache
```

## See Also

- [Echo Bot](../echo_bot/) - Minimal example
- [Counter Bot](../counter_bot/) - State management
- [Reminder Bot](../reminder_bot/) - Scheduler usage
- [Poll Bot](../poll_bot/) - SQL storage
- [API Reference](../../docs/api_reference.md) - Framework API
- [Telegram Bot API - Inline Keyboards](https://core.telegram.org/bots/api#inlinekeyboardmarkup)
