"""
Backup and restore utilities for bot data.

Handles creating backups, listing backups, and restoring from backups.
"""

import shlex
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from rich.console import Console

from telegram_bot_stack.cli.utils.vps import VPSConnection, get_docker_compose_command

console = Console()


class BackupManager:
    """Manages backup and restore operations for bot data."""

    def __init__(self, bot_name: str, remote_dir: str):
        """Initialize backup manager.

        Args:
            bot_name: Bot name (for container and backup naming)
            remote_dir: Remote directory on VPS (e.g., /opt/bot_name)
        """
        self.bot_name = bot_name
        self.remote_dir = remote_dir
        self.backups_dir = f"{remote_dir}/backups"

    def create_backup(
        self,
        vps: VPSConnection,
        auto_backup: bool = False,
    ) -> Optional[str]:
        """Create a backup of bot data.

        Args:
            vps: VPS connection object
            auto_backup: If True, this is an automatic backup (less verbose)

        Returns:
            Backup filename if successful, None otherwise
        """
        if not auto_backup:
            console.print("📦 [bold cyan]Creating backup...[/bold cyan]\n")

        # Create backups directory
        vps.run_command(f"mkdir -p {shlex.quote(self.backups_dir)}", hide=True)

        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_filename = f"backup-{timestamp}.tar.gz"
        backup_path = f"{self.backups_dir}/{backup_filename}"

        # Stop bot container temporarily (if running)
        container_running = False
        if not auto_backup:
            console.print("[cyan]Checking bot status...[/cyan]")

        # Get appropriate docker compose command (v2 or v1)
        compose_cmd = get_docker_compose_command(vps.connect())

        # Check if container is running
        result = vps.connect().run(
            f"cd {shlex.quote(self.remote_dir)} && {compose_cmd} ps -q",
            hide=True,
        )
        if result.ok and result.stdout.strip():
            container_running = True
            if not auto_backup:
                console.print("[cyan]Stopping bot container temporarily...[/cyan]")
            vps.run_command(
                f"cd {shlex.quote(self.remote_dir)} && {compose_cmd} stop",
                hide=True,
            )

        try:
            # Create backup tarball
            # Backup data directory and .env file (if exists)
            data_dir = f"{self.remote_dir}/data"
            env_file = f"{self.remote_dir}/.env"
            secrets_file = f"{self.remote_dir}/.secrets.env.encrypted"

            # Build tar command with files that exist
            tar_files = []
            if vps.run_command(f"test -d {shlex.quote(data_dir)}", hide=True):
                tar_files.append("data")
            if vps.run_command(f"test -f {shlex.quote(env_file)}", hide=True):
                tar_files.append(".env")
            if vps.run_command(f"test -f {shlex.quote(secrets_file)}", hide=True):
                tar_files.append(".secrets.env.encrypted")

            if not tar_files:
                if not auto_backup:
                    console.print(
                        "[yellow]⚠️  No data to backup (data directory and .env not found)[/yellow]"
                    )
                return None

            # Create tar command
            tar_cmd = (
                f"cd {shlex.quote(self.remote_dir)} && "
                f"tar -czf {shlex.quote(backup_path)} {' '.join(shlex.quote(f) for f in tar_files)}"
            )

            if not auto_backup:
                console.print("[cyan]Backing up data...[/cyan]")
            if not vps.run_command(tar_cmd, hide=True):
                if not auto_backup:
                    console.print("[red]❌ Failed to create backup[/red]")
                return None

            # Get backup size
            size_cmd = f"du -h {shlex.quote(backup_path)} | cut -f1"
            result = vps.connect().run(size_cmd, hide=True)
            backup_size = result.stdout.strip() if result.ok else "unknown"

            if not auto_backup:
                console.print(f"[green]✓ Backup created: {backup_filename}[/green]")
                console.print(f"[dim]   Size: {backup_size}[/dim]")
                console.print(f"[dim]   Location: {backup_path}[/dim]")
            else:
                console.print(f"[dim]✓ Auto-backup created: {backup_filename}[/dim]")

            return backup_filename

        finally:
            # Restart bot container if it was running
            if container_running:
                if not auto_backup:
                    console.print("[cyan]Starting bot container...[/cyan]")
                vps.run_command(
                    f"cd {shlex.quote(self.remote_dir)} && make up",
                    hide=True,
                )
                if not auto_backup:
                    console.print("[green]✓ Bot container restarted[/green]\n")

        if not auto_backup:
            console.print("\n[green]✅ Backup created successfully![/green]")
            console.print(f"[bold]Location:[/bold] {backup_path}")

        return backup_filename

    def list_backups(self, vps: VPSConnection) -> List[dict]:
        """List all available backups.

        Args:
            vps: VPS connection object

        Returns:
            List of backup dictionaries with filename, size, and date
        """
        # Check if backups directory exists
        if not vps.run_command(f"test -d {shlex.quote(self.backups_dir)}", hide=True):
            return []

        # List backups with details
        list_cmd = (
            f"ls -lh {shlex.quote(self.backups_dir)}/backup-*.tar.gz 2>/dev/null | "
            f"awk '{{print $9, $5, $6, $7, $8}}'"
        )
        result = vps.connect().run(list_cmd, hide=True)

        backups = []
        if result.ok and result.stdout.strip():
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        filename = Path(parts[0]).name
                        size = parts[1]
                        # Try to parse date from filename (backup-YYYYMMDD-HHMMSS.tar.gz)
                        try:
                            date_str = filename.replace("backup-", "").replace(
                                ".tar.gz", ""
                            )
                            date_obj = datetime.strptime(date_str, "%Y%m%d-%H%M%S")
                            backups.append(
                                {
                                    "filename": filename,
                                    "size": size,
                                    "date": date_obj,
                                    "path": parts[0],
                                }
                            )
                        except ValueError:
                            # If date parsing fails, still include backup
                            backups.append(
                                {
                                    "filename": filename,
                                    "size": size,
                                    "date": None,
                                    "path": parts[0],
                                }
                            )

        # Sort by date (newest first)
        backups.sort(key=lambda x: x["date"] or datetime.min, reverse=True)
        return backups

    def restore_backup(
        self, vps: VPSConnection, backup_filename: str, confirm: bool = True
    ) -> bool:
        """Restore bot data from backup.

        Args:
            vps: VPS connection object
            backup_filename: Name of backup file to restore
            confirm: If True, ask for confirmation before restoring

        Returns:
            True if restore successful, False otherwise
        """
        console.print("🔄 [bold cyan]Restoring from backup...[/bold cyan]\n")

        backup_path = f"{self.backups_dir}/{backup_filename}"

        # Check if backup exists
        if not vps.run_command(f"test -f {shlex.quote(backup_path)}", hide=True):
            console.print(f"[red]❌ Backup not found: {backup_filename}[/red]")
            return False

        if confirm:
            console.print(
                "[yellow]⚠️  WARNING: This will replace current bot data![/yellow]"
            )
            from rich.prompt import Confirm as RichConfirm

            if not RichConfirm.ask(
                "[yellow]Are you sure you want to restore from this backup?[/yellow]",
                default=False,
            ):
                console.print("[yellow]Restore cancelled[/yellow]")
                return False

        # Get appropriate docker compose command (v2 or v1)
        compose_cmd = get_docker_compose_command(vps.connect())

        # Stop bot container
        console.print("[cyan]Stopping bot container...[/cyan]")
        vps.run_command(
            f"cd {shlex.quote(self.remote_dir)} && {compose_cmd} stop",
            hide=True,
        )
        console.print("[green]✓ Bot container stopped[/green]\n")

        try:
            # Extract backup
            console.print("[cyan]Extracting backup...[/cyan]")
            extract_cmd = (
                f"cd {shlex.quote(self.remote_dir)} && "
                f"tar -xzf {shlex.quote(backup_path)}"
            )
            if not vps.run_command(extract_cmd, hide=True):
                console.print("[red]❌ Failed to extract backup[/red]")
                return False
            console.print("[green]✓ Backup extracted[/green]\n")

            # Restart bot container
            console.print("[cyan]Starting bot container...[/cyan]")
            vps.run_command(
                f"cd {shlex.quote(self.remote_dir)} && make up",
                hide=True,
            )
            console.print("[green]✓ Bot container started[/green]\n")

            console.print("[green]✅ Backup restored successfully![/green]")
            return True

        except Exception as e:
            console.print(f"[red]❌ Restore failed: {e}[/red]")
            return False

    def download_backup(
        self, vps: VPSConnection, backup_filename: str, local_path: Path
    ) -> bool:
        """Download backup from VPS to local machine.

        Args:
            vps: VPS connection object
            backup_filename: Name of backup file to download
            local_path: Local directory to save backup

        Returns:
            True if download successful, False otherwise
        """
        console.print(
            f"📥 [bold cyan]Downloading backup: {backup_filename}[/bold cyan]\n"
        )

        backup_path = f"{self.backups_dir}/{backup_filename}"

        # Check if backup exists
        if not vps.run_command(f"test -f {shlex.quote(backup_path)}", hide=True):
            console.print(f"[red]❌ Backup not found: {backup_filename}[/red]")
            return False

        # Ensure local directory exists
        local_path.mkdir(parents=True, exist_ok=True)
        local_file = local_path / backup_filename

        # Use scp to download file
        console.print("[cyan]Downloading backup...[/cyan]")
        try:
            conn = vps.connect()
            conn.get(backup_path, str(local_file))
            console.print(f"[green]✓ Backup downloaded to: {local_file}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]❌ Download failed: {e}[/red]")
            return False

    def cleanup_old_backups(
        self,
        vps: VPSConnection,
        retention_days: int = 7,
        max_backups: int = 10,
    ) -> int:
        """Clean up old backups based on retention policy.

        Args:
            vps: VPS connection object
            retention_days: Keep backups newer than this many days
            max_backups: Maximum number of backups to keep

        Returns:
            Number of backups deleted
        """
        backups = self.list_backups(vps)

        if not backups:
            return 0

        deleted_count = 0
        now = datetime.now()

        # Delete backups older than retention_days
        for backup in backups:
            if backup["date"]:
                age_days = (now - backup["date"]).days
                if age_days > retention_days:
                    backup_path = backup["path"]
                    if vps.run_command(f"rm {shlex.quote(backup_path)}", hide=True):
                        deleted_count += 1

        # If still too many backups, delete oldest ones
        remaining_backups = self.list_backups(vps)
        if len(remaining_backups) > max_backups:
            # Sort by date (oldest first) and delete excess
            remaining_backups.sort(key=lambda x: x["date"] or datetime.min)
            excess = len(remaining_backups) - max_backups
            for backup in remaining_backups[:excess]:
                backup_path = backup["path"]
                if vps.run_command(f"rm {shlex.quote(backup_path)}", hide=True):
                    deleted_count += 1

        return deleted_count
