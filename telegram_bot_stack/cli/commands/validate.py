"""Validate bot configuration and environment."""

import os
import sys
from pathlib import Path

import click


@click.command()
@click.option(
    "--strict/--no-strict",
    default=False,
    help="Exit with error if validation fails",
)
def validate(strict: bool) -> None:
    """Validate bot configuration and environment.

    Checks:
    - BOT_TOKEN is set and valid format
    - Required files exist (bot.py)
    - Python dependencies are installed
    - Storage configuration (if applicable)

    Example:

        telegram-bot-stack validate

        telegram-bot-stack validate --strict
    """
    click.secho("\n🔍 Validating bot configuration...\n", fg="cyan", bold=True)

    errors = []
    warnings = []

    # 1. Check bot.py exists
    bot_file = Path.cwd() / "bot.py"
    if bot_file.exists():
        click.secho("✅ bot.py found", fg="green")
    else:
        errors.append("bot.py not found in current directory")
        click.secho("❌ bot.py not found", fg="red")

    # 2. Check .env file
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        click.secho("✅ .env file found", fg="green")
    else:
        warnings.append(".env file not found")
        click.secho("⚠️  .env file not found", fg="yellow")

    # 3. Check BOT_TOKEN
    bot_token = os.getenv("BOT_TOKEN")
    if bot_token:
        # Basic validation of token format
        if ":" in bot_token and len(bot_token) > 40:
            click.secho("✅ BOT_TOKEN is set and looks valid", fg="green")
        else:
            warnings.append("BOT_TOKEN format looks invalid")
            click.secho("⚠️  BOT_TOKEN format looks invalid", fg="yellow")
    else:
        errors.append("BOT_TOKEN not set in environment")
        click.secho("❌ BOT_TOKEN not set", fg="red")

    # 4. Check telegram-bot-stack is installed
    try:
        import telegram_bot_stack

        click.secho(
            f"✅ telegram-bot-stack installed (v{telegram_bot_stack.__version__})",
            fg="green",
        )
    except ImportError:
        errors.append("telegram-bot-stack not installed")
        click.secho("❌ telegram-bot-stack not installed", fg="red")

    # 5. Check python-telegram-bot is installed
    try:
        import telegram  # noqa: F401

        click.secho("✅ python-telegram-bot installed", fg="green")
    except ImportError:
        errors.append("python-telegram-bot not installed")
        click.secho("❌ python-telegram-bot not installed", fg="red")

    # 6. Check for common issues
    if bot_file.exists():
        content = bot_file.read_text()

        # Check if BotBase is imported
        if "BotBase" not in content:
            warnings.append("bot.py doesn't seem to import BotBase")
            click.secho("⚠️  bot.py doesn't import BotBase", fg="yellow")

        # Check if storage is configured
        if "Storage" not in content:
            warnings.append("No storage configuration found in bot.py")
            click.secho("⚠️  No storage configuration found", fg="yellow")

    # Summary
    click.echo("\n" + "=" * 70)

    if errors:
        click.secho(
            f"\n❌ Validation failed with {len(errors)} error(s):", fg="red", bold=True
        )
        for error in errors:
            click.secho(f"  • {error}", fg="red")

    if warnings:
        click.secho(f"\n⚠️  {len(warnings)} warning(s):", fg="yellow", bold=True)
        for warning in warnings:
            click.secho(f"  • {warning}", fg="yellow")

    if not errors and not warnings:
        click.secho(
            "\n✅ All checks passed! Your bot is ready to run.", fg="green", bold=True
        )

    click.echo("\n" + "=" * 70 + "\n")

    # Exit with error if strict mode and there are errors
    if strict and errors:
        sys.exit(1)
