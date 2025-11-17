"""Configuration for Quit Smoking Bot."""

import datetime
import os
from zoneinfo import ZoneInfo

# Timezone settings - configurable via environment variable
DEFAULT_TIMEZONE = os.getenv("TZ", "UTC")
TIMEZONE = ZoneInfo(DEFAULT_TIMEZONE)

# Main timezone variable for the bot
BOT_TIMEZONE = TIMEZONE

# Start date components
START_YEAR = 2025
START_MONTH = 1

# Notification schedule - 23rd of each month at 21:58
NOTIFICATION_DAY = 23  # day of month
NOTIFICATION_HOUR = 21  # hour (24-hour format)
NOTIFICATION_MINUTE = 58  # minute

# Start date - January 23, 2025 at 21:58 (timezone-aware)
START_DATE = datetime.datetime(
    START_YEAR,
    START_MONTH,
    NOTIFICATION_DAY,
    NOTIFICATION_HOUR,
    NOTIFICATION_MINUTE,
    tzinfo=BOT_TIMEZONE,
)

# Prize fund settings
MONTHLY_AMOUNT = 5000  # amount in rubles
PRIZE_FUND_INCREASE = 5000  # increase amount per month
MAX_PRIZE_FUND = 100000  # maximum prize fund amount

# Bot settings
BOT_NAME = "Quit Smoking Bot"

# Message templates
WELCOME_MESSAGE = (
    "👋 Welcome to {bot_name}!\n\n"
    "I'll help you track your smoke-free period and motivate you with quotes. "
    "You'll also get a prize fund that increases every month!\n\n"
    "Commands:\n"
    "/status - Check your current status\n"
    "/my_id - Show your Telegram ID"
)

STATUS_MESSAGE = (
    "📊 Your current status:\n\n"
    "🚭 Smoke-free period: {years} years, {months} months, {days} days\n"
    "💰 Current prize fund: {prize_fund} rubles\n"
    "📅 Next increase: {next_increase_date} at {next_increase_time} {timezone}\n"
    "➕ Next increase amount: +{increase_amount} rubles\n\n"
    "💭 {quote}"
)
