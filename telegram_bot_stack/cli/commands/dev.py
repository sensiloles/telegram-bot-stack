"""Run bot in development mode with auto-reload."""

import subprocess
import sys
import time
from pathlib import Path

import click


@click.command()
@click.option(
    "--reload/--no-reload",
    default=True,
    help="Auto-reload on code changes",
)
@click.option(
    "--bot-file",
    default="bot.py",
    help="Bot file to run (default: bot.py)",
)
def dev(reload: bool, bot_file: str) -> None:
    """Run bot in development mode with auto-reload.

    Features:
    - Auto-reload on code changes (with --reload)
    - Pretty logging
    - Debug mode

    Example:

        telegram-bot-stack dev --reload

        telegram-bot-stack dev --bot-file my_bot.py
    """
    bot_path = Path.cwd() / bot_file

    if not bot_path.exists():
        click.secho(f"❌ Error: Bot file not found: {bot_file}", fg="red")
        click.echo("\nMake sure you're in the project directory and bot.py exists.")
        sys.exit(1)

    # Check for .env file
    env_file = Path.cwd() / ".env"
    if not env_file.exists():
        click.secho("⚠️  Warning: .env file not found", fg="yellow")
        click.echo("Create .env with your BOT_TOKEN:")
        click.echo('  echo "BOT_TOKEN=your_token_here" > .env\n')

    if reload:
        click.secho(
            "🤖 Starting bot in development mode (auto-reload enabled)...\n", fg="cyan"
        )
        click.echo("Press Ctrl+C to stop\n")

        try:
            # Use watchdog for auto-reload
            _run_with_reload(bot_path)
        except ImportError:
            click.secho(
                "⚠️  Warning: watchdog not installed, running without auto-reload",
                fg="yellow",
            )
            _run_bot(bot_path)
    else:
        click.secho("🤖 Starting bot...\n", fg="cyan")
        _run_bot(bot_path)


def _run_bot(bot_path: Path) -> None:
    """Run the bot without auto-reload.

    Args:
        bot_path: Path to the bot file
    """
    try:
        subprocess.run([sys.executable, str(bot_path)], check=True)
    except KeyboardInterrupt:
        click.echo("\n\n👋 Bot stopped")
    except subprocess.CalledProcessError as e:
        click.secho(f"\n❌ Bot exited with error code {e.returncode}", fg="red")
        sys.exit(e.returncode)


def _run_with_reload(bot_path: Path) -> None:
    """Run the bot with auto-reload using watchdog.

    Args:
        bot_path: Path to the bot file
    """
    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError:
        raise ImportError(
            "watchdog is required for auto-reload. "
            "Install it with: pip install watchdog"
        )

    process = None
    restart_requested = False

    class BotReloadHandler(FileSystemEventHandler):
        """Handler for file changes."""

        def on_modified(self, event):
            """Handle file modification."""
            nonlocal restart_requested

            # Only reload on .py file changes
            if event.src_path.endswith(".py"):
                restart_requested = True

    def start_bot():
        """Start the bot process."""
        return subprocess.Popen(
            [sys.executable, str(bot_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

    # Start initial bot process
    process = start_bot()
    click.secho("✅ Bot started", fg="green")

    # Setup file watcher
    event_handler = BotReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, path=str(bot_path.parent), recursive=True)
    observer.start()

    try:
        while True:
            # Check if process is still running
            if process.poll() is not None:
                click.secho("\n⚠️  Bot process exited", fg="yellow")
                break

            # Check if restart requested
            if restart_requested:
                click.echo("\n🔄 Code changed, restarting bot...")
                process.terminate()
                process.wait(timeout=5)
                process = start_bot()
                click.secho("✅ Bot restarted", fg="green")
                restart_requested = False

            time.sleep(0.5)

    except KeyboardInterrupt:
        click.echo("\n\n👋 Stopping bot...")
        if process:
            process.terminate()
            process.wait(timeout=5)
    finally:
        observer.stop()
        observer.join()
