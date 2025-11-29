"""Bot instance lock file management for dev mode."""

import json
import os
import time
from pathlib import Path

import click


class BotLockManager:
    """Manage lock file to prevent multiple bot instances in dev mode.

    Uses PID-based locking to ensure only one bot instance runs at a time
    in local development. Automatically cleans up stale locks from dead processes.
    """

    def __init__(self, bot_dir: Path):
        """Initialize lock manager.

        Args:
            bot_dir: Directory where bot is running (contains bot.py)
        """
        self.bot_dir = bot_dir
        self.lock_file = bot_dir / ".bot.lock"
        self.current_pid = os.getpid()

    def is_process_running(self, pid: int) -> bool:
        """Check if process with given PID is running.

        Args:
            pid: Process ID to check

        Returns:
            True if process is running, False otherwise
        """
        try:
            # Send signal 0 - doesn't kill, just checks if process exists
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False

    def acquire_lock(self, force: bool = False) -> bool:
        """Try to acquire lock.

        Args:
            force: If True, forcefully acquire lock even if another instance is running

        Returns:
            True if lock acquired, False if another instance is running
        """
        # Check if lock file exists
        if self.lock_file.exists():
            try:
                with open(self.lock_file) as f:
                    lock_data = json.load(f)

                existing_pid = lock_data.get("pid")
                started_at = lock_data.get("started_at")

                # Check if process is still running
                if existing_pid and self.is_process_running(existing_pid):
                    if force:
                        # Force mode: kill existing process and take over
                        click.secho(
                            f"\n⚠️  Forcing lock acquisition (killing PID: {existing_pid})",
                            fg="yellow",
                        )
                        try:
                            os.kill(existing_pid, 15)  # SIGTERM
                            time.sleep(0.5)  # Give it time to cleanup
                            # If still running, force kill
                            if self.is_process_running(existing_pid):
                                os.kill(existing_pid, 9)  # SIGKILL
                            click.echo("   Process terminated")
                        except (OSError, ProcessLookupError) as e:
                            click.secho(
                                f"   Warning: Could not kill process: {e}", fg="yellow"
                            )
                        # Remove lock file and continue to create new lock
                        try:
                            self.lock_file.unlink()
                        except OSError:
                            pass  # File may already be gone
                        # Fall through to create new lock below
                    else:
                        # Another instance is running
                        click.secho(
                            f"\n❌ Error: Bot is already running (PID: {existing_pid})",
                            fg="red",
                        )
                        click.echo(f"   Started at: {started_at}")
                        click.echo(f"   Lock file: {self.lock_file}")
                        click.echo("\n💡 Options:")
                        click.echo(f"   1. Stop existing process: kill {existing_pid}")
                        click.echo("   2. Use existing dev session in another terminal")
                        click.echo(
                            "   3. Force restart: telegram-bot-stack dev --force"
                        )
                        click.echo(
                            "\n📝 Tip: Use 'ps aux | grep python' to see all Python processes\n"
                        )
                        return False
                else:
                    # Process is dead, clean up stale lock
                    click.secho(
                        f"🧹 Cleaning up stale lock (dead process: {existing_pid})",
                        fg="yellow",
                    )
                    self.lock_file.unlink()

            except (json.JSONDecodeError, KeyError, OSError) as e:
                # Corrupted lock file, remove it
                click.secho(f"⚠️  Corrupted lock file ({e}), removing it", fg="yellow")
                self.lock_file.unlink()

        # Create new lock
        lock_data = {
            "pid": self.current_pid,
            "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": time.time(),
        }

        try:
            with open(self.lock_file, "w") as f:
                json.dump(lock_data, f, indent=2)
            return True
        except OSError as e:
            click.secho(f"⚠️  Failed to create lock file: {e}", fg="yellow")
            return True  # Don't block if we can't create lock

    def release_lock(self) -> None:
        """Release lock by removing lock file."""
        if self.lock_file.exists():
            try:
                # Only remove if it's our lock
                with open(self.lock_file) as f:
                    lock_data = json.load(f)

                if lock_data.get("pid") == self.current_pid:
                    self.lock_file.unlink()
            except (json.JSONDecodeError, KeyError, OSError):
                # If we can't read it, just try to remove
                try:
                    self.lock_file.unlink()
                except OSError:
                    pass


def with_bot_lock(func):  # type: ignore[no-untyped-def]
    """Decorator to wrap function with bot lock management.

    Usage:
        @with_bot_lock
        def run_bot():
            # Bot code here
            pass
    """

    def wrapper(*args, **kwargs):  # type: ignore[no-untyped-def]
        bot_dir = Path.cwd()
        lock_manager = BotLockManager(bot_dir)

        # Try to acquire lock
        if not lock_manager.acquire_lock():
            return  # Another instance is running

        try:
            # Run the function
            return func(*args, **kwargs)
        finally:
            # Always release lock on exit
            lock_manager.release_lock()

    return wrapper
