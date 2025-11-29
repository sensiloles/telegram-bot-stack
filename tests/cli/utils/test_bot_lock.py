"""Tests for bot lock manager."""

import json
import os
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

from telegram_bot_stack.cli.utils.bot_lock import BotLockManager


class TestBotLockManager:
    """Tests for BotLockManager class."""

    def test_acquire_lock_success(self, tmp_path: Path) -> None:
        """Test acquiring lock when no lock exists."""
        manager = BotLockManager(tmp_path)

        assert manager.acquire_lock() is True
        assert manager.lock_file.exists()

        # Verify lock content
        with open(manager.lock_file) as f:
            lock_data = json.load(f)

        assert lock_data["pid"] == os.getpid()
        assert "started_at" in lock_data
        assert "timestamp" in lock_data

    def test_acquire_lock_with_running_process(self, tmp_path: Path) -> None:
        """Test acquiring lock when another process is running."""
        # Create a lock with current PID (simulating another instance)
        lock_file = tmp_path / ".bot.lock"
        lock_data = {
            "pid": os.getpid(),
            "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": time.time(),
        }

        with open(lock_file, "w") as f:
            json.dump(lock_data, f)

        # Try to acquire lock with different PID
        manager = BotLockManager(tmp_path)
        with patch.object(manager, "current_pid", os.getpid() + 1):
            result = manager.acquire_lock()

        assert result is False
        assert lock_file.exists()  # Lock should still exist

    def test_acquire_lock_with_dead_process(self, tmp_path: Path) -> None:
        """Test acquiring lock when process is dead (stale lock)."""
        # Create a lock with a non-existent PID
        lock_file = tmp_path / ".bot.lock"
        dead_pid = 999999  # Assuming this PID doesn't exist
        lock_data = {
            "pid": dead_pid,
            "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": time.time(),
        }

        with open(lock_file, "w") as f:
            json.dump(lock_data, f)

        manager = BotLockManager(tmp_path)

        # Mock is_process_running to return False for dead process
        with patch.object(manager, "is_process_running", return_value=False):
            result = manager.acquire_lock()

        assert result is True
        assert lock_file.exists()

        # Verify new lock was created with current PID
        with open(lock_file) as f:
            new_lock = json.load(f)

        assert new_lock["pid"] == os.getpid()

    def test_acquire_lock_with_corrupted_lock(self, tmp_path: Path) -> None:
        """Test acquiring lock when lock file is corrupted."""
        lock_file = tmp_path / ".bot.lock"

        # Create corrupted lock file
        with open(lock_file, "w") as f:
            f.write("not valid json {}")

        manager = BotLockManager(tmp_path)
        result = manager.acquire_lock()

        assert result is True
        assert lock_file.exists()

        # Verify new valid lock was created
        with open(lock_file) as f:
            lock_data = json.load(f)

        assert lock_data["pid"] == os.getpid()

    def test_acquire_lock_force_mode(self, tmp_path: Path) -> None:
        """Test force mode kills existing process and acquires lock."""
        lock_file = tmp_path / ".bot.lock"
        mock_pid = 12345
        lock_data = {
            "pid": mock_pid,
            "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": time.time(),
        }

        with open(lock_file, "w") as f:
            json.dump(lock_data, f)

        manager = BotLockManager(tmp_path)

        # Mock process running and kill
        with (
            patch.object(manager, "is_process_running", return_value=True),
            patch("os.kill") as mock_kill,
        ):
            result = manager.acquire_lock(force=True)

        assert result is True
        # Should attempt to kill the process
        assert mock_kill.call_count >= 1
        assert lock_file.exists()

        # Verify new lock with current PID
        with open(lock_file) as f:
            new_lock = json.load(f)

        assert new_lock["pid"] == os.getpid()

    def test_release_lock(self, tmp_path: Path) -> None:
        """Test releasing lock."""
        manager = BotLockManager(tmp_path)

        # Acquire lock first
        manager.acquire_lock()
        assert manager.lock_file.exists()

        # Release lock
        manager.release_lock()
        assert not manager.lock_file.exists()

    def test_release_lock_wrong_pid(self, tmp_path: Path) -> None:
        """Test releasing lock doesn't remove lock from another process."""
        # Create lock with different PID
        lock_file = tmp_path / ".bot.lock"
        other_pid = os.getpid() + 1
        lock_data = {
            "pid": other_pid,
            "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": time.time(),
        }

        with open(lock_file, "w") as f:
            json.dump(lock_data, f)

        manager = BotLockManager(tmp_path)
        manager.release_lock()

        # Lock should still exist (wasn't our lock)
        assert lock_file.exists()

    def test_is_process_running_current_process(self) -> None:
        """Test checking if current process is running."""
        manager = BotLockManager(Path.cwd())

        # Current process should be running
        assert manager.is_process_running(os.getpid()) is True

    def test_is_process_running_nonexistent(self) -> None:
        """Test checking if non-existent process is running."""
        manager = BotLockManager(Path.cwd())

        # Very high PID unlikely to exist
        assert manager.is_process_running(999999) is False

    def test_lock_file_path(self, tmp_path: Path) -> None:
        """Test lock file is created in correct location."""
        manager = BotLockManager(tmp_path)

        expected_path = tmp_path / ".bot.lock"
        assert manager.lock_file == expected_path

    def test_multiple_acquire_attempts(self, tmp_path: Path) -> None:
        """Test multiple attempts to acquire lock."""
        manager1 = BotLockManager(tmp_path)
        manager2 = BotLockManager(tmp_path)

        # First manager acquires lock
        assert manager1.acquire_lock() is True

        # Second manager with different PID should fail
        with patch.object(manager2, "current_pid", os.getpid() + 1):
            assert manager2.acquire_lock() is False

        # After releasing, second manager should succeed
        manager1.release_lock()

        with patch.object(manager2, "current_pid", os.getpid() + 1):
            assert manager2.acquire_lock() is True

    def test_lock_survives_quick_restart(self, tmp_path: Path) -> None:
        """Test lock behavior during quick restart."""
        manager1 = BotLockManager(tmp_path)

        # Acquire and release
        assert manager1.acquire_lock() is True
        manager1.release_lock()

        # Immediately acquire again (simulating restart)
        manager2 = BotLockManager(tmp_path)
        assert manager2.acquire_lock() is True

    @patch("builtins.open", side_effect=OSError("Permission denied"))
    def test_acquire_lock_permission_error(
        self, mock_open: MagicMock, tmp_path: Path
    ) -> None:
        """Test acquiring lock handles permission errors gracefully."""
        manager = BotLockManager(tmp_path)

        # Should not crash, returns True to not block bot
        result = manager.acquire_lock()
        assert result is True

    def test_force_kill_stubborn_process(self, tmp_path: Path) -> None:
        """Test force mode uses SIGKILL if SIGTERM fails."""
        lock_file = tmp_path / ".bot.lock"
        mock_pid = 12345
        lock_data = {
            "pid": mock_pid,
            "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": time.time(),
        }

        with open(lock_file, "w") as f:
            json.dump(lock_data, f)

        manager = BotLockManager(tmp_path)

        # Mock process that survives SIGTERM but dies to SIGKILL
        # First call: returns True (process running before force)
        # Second call: returns True (still running after SIGTERM)
        # After SIGKILL it's not checked again due to code flow
        is_running_results = [True, True]

        with (
            patch.object(manager, "is_process_running", side_effect=is_running_results),
            patch("os.kill") as mock_kill,
            patch("time.sleep"),
        ):
            result = manager.acquire_lock(force=True)

        assert result is True
        # Should call both SIGTERM (15) and SIGKILL (9)
        assert mock_kill.call_count == 2
        assert mock_kill.call_args_list[0][0] == (mock_pid, 15)  # SIGTERM
        assert mock_kill.call_args_list[1][0] == (mock_pid, 9)  # SIGKILL
