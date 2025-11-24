"""Main CLI entry point for telegram-bot-stack."""

import sys

import click

from telegram_bot_stack.cli.commands import dev, init, new, validate


@click.group()
@click.version_option(package_name="telegram-bot-stack")
def cli() -> None:
    """Telegram Bot Stack - Professional bot development framework.

    Create, develop, and deploy Telegram bots with ease.
    """
    pass


# Register commands
cli.add_command(init.init)
cli.add_command(new.new)
cli.add_command(dev.dev)
cli.add_command(validate.validate)


def main() -> None:
    """Entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        click.secho(f"\n❌ Error: {e}", fg="red", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
