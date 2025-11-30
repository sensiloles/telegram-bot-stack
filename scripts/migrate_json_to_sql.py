#!/usr/bin/env python3
"""Migration tool to convert JSON storage to SQL storage.

This script reads data from JSON files and migrates it to a SQL database,
preserving all keys and data structures.

Usage:
    # Dry run (preview migration)
    python scripts/migrate_json_to_sql.py --json-dir data --database-url sqlite:///bot.db --dry-run

    # Actual migration
    python scripts/migrate_json_to_sql.py --json-dir data --database-url sqlite:///bot.db

    # PostgreSQL migration
    python scripts/migrate_json_to_sql.py \\
        --json-dir data \\
        --database-url postgresql://user:pass@localhost/bot_db

    # Verbose output
    python scripts/migrate_json_to_sql.py --json-dir data --database-url sqlite:///bot.db --verbose
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from telegram_bot_stack.storage import SQLStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def discover_json_files(json_dir: Path) -> List[Tuple[str, Path]]:
    """Discover all JSON files in the directory.

    Args:
        json_dir: Directory containing JSON files

    Returns:
        List of tuples (key, filepath) where key is the storage key
    """
    json_files: list[tuple[str, Path]] = []

    if not json_dir.exists():
        logger.error(f"Directory not found: {json_dir}")
        return json_files

    for filepath in json_dir.glob("*.json"):
        # Remove .json extension to get the key
        key = filepath.stem
        json_files.append((key, filepath))

    return json_files


def load_json_data(filepath: Path) -> Dict[Any, Any]:
    """Load data from JSON file.

    Args:
        filepath: Path to JSON file

    Returns:
        Loaded data or empty dict on error
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)  # type: ignore[no-any-return]
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        return {}


def migrate_data(
    json_dir: str,
    database_url: str,
    dry_run: bool = False,
    verbose: bool = False,
) -> Tuple[int, int]:
    """Migrate data from JSON storage to SQL storage.

    Args:
        json_dir: Directory containing JSON files
        database_url: SQLAlchemy database URL
        dry_run: If True, only preview migration without writing
        verbose: Enable verbose logging

    Returns:
        Tuple of (successful_count, failed_count)
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    json_path = Path(json_dir)

    # Discover JSON files
    logger.info(f"Scanning directory: {json_path}")
    json_files = discover_json_files(json_path)

    if not json_files:
        logger.warning("No JSON files found to migrate")
        return 0, 0

    logger.info(f"Found {len(json_files)} JSON file(s) to migrate")

    if dry_run:
        logger.info("DRY RUN MODE - No data will be written to database")
        logger.info("-" * 60)

        for key, filepath in json_files:
            data = load_json_data(filepath)
            data_preview = str(data)[:100]
            if len(str(data)) > 100:
                data_preview += "..."

            logger.info(f"Would migrate: {key}")
            logger.info(f"  Source: {filepath}")
            logger.info(f"  Data preview: {data_preview}")
            logger.info("")

        logger.info("-" * 60)
        logger.info(f"DRY RUN COMPLETE: {len(json_files)} file(s) would be migrated")
        return len(json_files), 0

    # Create SQL storage
    logger.info(f"Connecting to database: {database_url}")
    try:
        sql_storage = SQLStorage(database_url=database_url)
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return 0, len(json_files)

    # Migrate each file
    successful = 0
    failed = 0

    logger.info("Starting migration...")
    logger.info("-" * 60)

    for key, filepath in json_files:
        try:
            # Load data from JSON
            data = load_json_data(filepath)

            if not data:
                logger.warning(f"Skipping empty file: {key}")
                continue

            # Save to SQL
            if sql_storage.save(key, data):
                successful += 1
                logger.info(f"✓ Migrated: {key}")
                if verbose:
                    logger.debug(f"  Data: {data}")
            else:
                failed += 1
                logger.error(f"✗ Failed to migrate: {key}")

        except Exception as e:
            failed += 1
            logger.error(f"✗ Error migrating {key}: {e}")

    # Close SQL connection
    sql_storage.close()

    logger.info("-" * 60)
    logger.info(f"Migration complete: {successful} successful, {failed} failed")

    return successful, failed


def verify_migration(
    json_dir: str, database_url: str, verbose: bool = False
) -> Tuple[int, int]:
    """Verify that migrated data matches source JSON files.

    Args:
        json_dir: Directory containing JSON files
        database_url: SQLAlchemy database URL
        verbose: Enable verbose logging

    Returns:
        Tuple of (matching_count, mismatching_count)
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    json_path = Path(json_dir)

    # Discover JSON files
    json_files = discover_json_files(json_path)

    if not json_files:
        logger.warning("No JSON files found to verify")
        return 0, 0

    # Create storages
    try:
        sql_storage = SQLStorage(database_url=database_url)
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return 0, len(json_files)

    matching = 0
    mismatching = 0

    logger.info("Verifying migration...")
    logger.info("-" * 60)

    for key, filepath in json_files:
        try:
            # Load from JSON
            json_data = load_json_data(filepath)

            # Load from SQL
            sql_data = sql_storage.load(key)

            # Compare
            if json_data == sql_data:
                matching += 1
                logger.info(f"✓ Verified: {key}")
                if verbose:
                    logger.debug(f"  Data matches: {json_data}")
            else:
                mismatching += 1
                logger.error(f"✗ Mismatch: {key}")
                logger.error(f"  JSON: {json_data}")
                logger.error(f"  SQL:  {sql_data}")

        except Exception as e:
            mismatching += 1
            logger.error(f"✗ Error verifying {key}: {e}")

    sql_storage.close()

    logger.info("-" * 60)
    logger.info(
        f"Verification complete: {matching} matching, {mismatching} mismatching"
    )

    return matching, mismatching


def main() -> None:
    """Main entry point for the migration tool."""
    parser = argparse.ArgumentParser(
        description="Migrate JSON storage to SQL storage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (preview migration)
  python scripts/migrate_json_to_sql.py --json-dir data --database-url sqlite:///bot.db --dry-run

  # Migrate to SQLite
  python scripts/migrate_json_to_sql.py --json-dir data --database-url sqlite:///bot.db

  # Migrate to PostgreSQL
  python scripts/migrate_json_to_sql.py \\
      --json-dir data \\
      --database-url postgresql://user:pass@localhost/bot_db

  # Verify migration
  python scripts/migrate_json_to_sql.py \\
      --json-dir data \\
      --database-url sqlite:///bot.db \\
      --verify
        """,
    )

    parser.add_argument(
        "--json-dir",
        type=str,
        required=True,
        help="Directory containing JSON files",
    )

    parser.add_argument(
        "--database-url",
        type=str,
        required=True,
        help="SQLAlchemy database URL (e.g., sqlite:///bot.db)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview migration without writing to database",
    )

    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify migration by comparing JSON and SQL data",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    # Verify SQLAlchemy is installed
    try:
        import sqlalchemy  # noqa: F401
    except ImportError:
        logger.error(
            "SQLAlchemy not installed. Install with: pip install telegram-bot-stack[database]"
        )
        sys.exit(1)

    # Run migration or verification
    if args.verify:
        matching, mismatching = verify_migration(
            args.json_dir, args.database_url, args.verbose
        )
        if mismatching > 0:
            sys.exit(1)
    else:
        successful, failed = migrate_data(
            args.json_dir, args.database_url, args.dry_run, args.verbose
        )
        if failed > 0:
            sys.exit(1)


if __name__ == "__main__":
    main()
