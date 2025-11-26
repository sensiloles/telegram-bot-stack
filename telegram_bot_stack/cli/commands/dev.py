"""Run bot in development mode with auto-reload."""

import subprocess
import sys
import time
from pathlib import Path

import click

from telegram_bot_stack.cli.utils import venv
from telegram_bot_stack.cli.utils.venv import find_venv, get_venv_python


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

    # Find and use venv if available
    venv_path = find_venv()
    python_executable = sys.executable

    if venv_path:
        venv_python = get_venv_python(venv_path)
        if venv_python.exists():
            python_executable = str(venv_python)
            click.echo(f"📦 Using virtual environment: {venv_path}\n")
        else:
            click.secho(
                "⚠️  Warning: venv found but Python executable not found", fg="yellow"
            )
    else:
        click.secho(
            "⚠️  Warning: No virtual environment found. Using system Python.",
            fg="yellow",
        )
        click.echo("  Consider running: python -m venv venv\n")

    # Check for .env file
    env_file = Path.cwd() / ".env"
    if not env_file.exists():
        click.secho("⚠️  Warning: .env file not found", fg="yellow")
        click.echo("Create .env with your BOT_TOKEN:")
        click.echo('  echo "BOT_TOKEN=your_token_here" > .env\n')

    # Check if telegram-bot-stack is installed
    try:
        import telegram_bot_stack  # noqa: F401
    except ImportError:
        click.secho("❌ Error: telegram-bot-stack is not installed", fg="red")
        click.echo("\nInstall dependencies:")
        if venv_path:
            click.echo(f"  {venv.get_activation_command(venv_path)}")
            click.echo("  pip install -e .[dev]")
        else:
            click.echo("  pip install -e .[dev]")
        sys.exit(1)

    if reload:
        click.secho(
            "🤖 Starting bot in development mode (auto-reload enabled)...\n", fg="cyan"
        )
        click.echo("Press Ctrl+C to stop\n")

        try:
            # Use watchdog for auto-reload
            _run_with_reload(bot_path, python_executable)
        except ImportError:
            click.secho(
                "⚠️  Warning: watchdog not installed, running without auto-reload",
                fg="yellow",
            )
            _run_bot(bot_path, python_executable)
    else:
        click.secho("🤖 Starting bot...\n", fg="cyan")
        _run_bot(bot_path, python_executable)


def _run_bot(bot_path: Path, python_executable: str = None) -> None:
    """Run the bot without auto-reload.

    Args:
        bot_path: Path to the bot file
        python_executable: Python executable to use (defaults to sys.executable)
    """
    if python_executable is None:
        python_executable = sys.executable

    try:
        subprocess.run([python_executable, str(bot_path)], check=True)
    except KeyboardInterrupt:
        click.echo("\n\n👋 Bot stopped")
    except subprocess.CalledProcessError as e:
        click.secho(f"\n❌ Bot exited with error code {e.returncode}", fg="red")
        sys.exit(e.returncode)


def _run_with_reload(bot_path: Path, python_executable: str = None) -> None:
    """Run the bot with auto-reload using watchdog.

    Args:
        bot_path: Path to the bot file
        python_executable: Python executable to use (defaults to sys.executable)
    """
    if python_executable is None:
        python_executable = sys.executable

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
            [python_executable, str(bot_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,  # Line buffered
        )

    # Start initial bot process
    process = start_bot()
    click.secho("✅ Bot started", fg="green")

    # Setup file watcher
    event_handler = BotReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, path=str(bot_path.parent), recursive=True)
    observer.start()

    # Start reading bot output in background
    import queue
    import threading

    output_queue = queue.Queue()
    output_stopped = threading.Event()

    def read_output():
        """Read and display bot output."""
        try:
            for line in iter(process.stdout.readline, ""):
                if not line:
                    break
                output_queue.put(line.rstrip())
        except Exception:
            pass
        finally:
            output_stopped.set()

    output_thread = threading.Thread(target=read_output, daemon=True)
    output_thread.start()

    try:
        while True:
            # Display any available output
            try:
                while True:
                    line = output_queue.get_nowait()
                    click.echo(line)
            except queue.Empty:
                pass

            # Check if process is still running
            if process.poll() is not None:
                click.secho("\n⚠️  Bot process exited", fg="yellow")
                # Read remaining output
                output_stopped.wait(timeout=0.5)
                try:
                    while True:
                        line = output_queue.get_nowait()
                        click.echo(line)
                except queue.Empty:
                    pass
                # Also try to read any remaining output directly
                try:
                    remaining = process.stdout.read()
                    if remaining:
                        click.echo(remaining)
                except Exception:
                    pass
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
