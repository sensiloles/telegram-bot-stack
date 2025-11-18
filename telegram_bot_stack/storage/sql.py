"""SQL-based storage backend using SQLAlchemy."""

import json
import logging
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, String, Text, create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .base import StorageBackend

logger = logging.getLogger(__name__)

Base = declarative_base()


class StorageRecord(Base):
    """SQLAlchemy model for storage records.

    Table structure:
        - key: Primary key, unique identifier for the data
        - data: JSON-serialized data
        - created_at: Timestamp when record was created
        - updated_at: Timestamp when record was last updated
    """

    __tablename__ = "storage"

    key = Column(String(255), primary_key=True, nullable=False)
    data = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        """String representation of the record."""
        return f"<StorageRecord(key='{self.key}', updated_at='{self.updated_at}')>"


class SQLStorage(StorageBackend):
    """SQL-based storage backend using SQLAlchemy.

    This backend stores data in SQL databases (SQLite or PostgreSQL).
    Each key corresponds to a row in the storage table.

    Args:
        database_url: SQLAlchemy database URL
            - SQLite: "sqlite:///path/to/database.db" or "sqlite:///:memory:"
            - PostgreSQL: "postgresql://user:password@host:port/database"
        echo: Enable SQL query logging (default: False)
        pool_size: Connection pool size for PostgreSQL (default: 5)
        max_overflow: Max overflow connections for PostgreSQL (default: 10)

    Example:
        >>> # SQLite (file-based)
        >>> storage = SQLStorage(database_url="sqlite:///bot.db")
        >>> storage.save("users", {"user1": {"name": "John"}})
        >>> storage.load("users")
        {"user1": {"name": "John"}}
        >>>
        >>> # SQLite (in-memory, for testing)
        >>> storage = SQLStorage(database_url="sqlite:///:memory:")
        >>>
        >>> # PostgreSQL (production)
        >>> storage = SQLStorage(
        ...     database_url="postgresql://user:pass@localhost/bot_db",
        ...     pool_size=10
        ... )
    """

    def __init__(
        self,
        database_url: str,
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ):
        """Initialize SQL storage with database connection."""
        self.database_url = database_url
        self.echo = echo

        # Create engine with appropriate settings
        engine_kwargs = {"echo": echo}

        # Add connection pooling for PostgreSQL
        if database_url.startswith("postgresql"):
            engine_kwargs["pool_size"] = pool_size
            engine_kwargs["max_overflow"] = max_overflow

        self.engine = create_engine(database_url, **engine_kwargs)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        # Create tables if they don't exist
        self._create_tables()

        logger.debug(f"Initialized SQLStorage with database_url: {database_url}")

    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        try:
            inspector = inspect(self.engine)
            if not inspector.has_table("storage"):
                Base.metadata.create_all(bind=self.engine)
                logger.info("Created storage table")
            else:
                logger.debug("Storage table already exists")
        except SQLAlchemyError as e:
            logger.error(f"Error creating tables: {e}")
            raise

    def _get_session(self) -> Session:
        """Get a new database session.

        Returns:
            SQLAlchemy session instance
        """
        return self.SessionLocal()

    def save(self, key: str, data: Any) -> bool:
        """Save data to SQL database.

        Args:
            key: Unique identifier for the data
            data: Data to save (must be JSON serializable)

        Returns:
            True if save was successful, False otherwise
        """
        session = self._get_session()
        try:
            # Serialize data to JSON
            json_data = json.dumps(data, ensure_ascii=False)

            # Check if record exists
            record = session.query(StorageRecord).filter_by(key=key).first()

            if record:
                # Update existing record
                record.data = json_data
                record.updated_at = datetime.utcnow()
                logger.debug(f"Updated record with key: {key}")
            else:
                # Create new record
                record = StorageRecord(key=key, data=json_data)
                session.add(record)
                logger.debug(f"Created new record with key: {key}")

            session.commit()
            return True

        except (SQLAlchemyError, TypeError, ValueError) as e:
            session.rollback()
            logger.error(f"Error saving data for key '{key}': {e}")
            return False
        finally:
            session.close()

    def load(self, key: str, default: Any = None) -> Any:
        """Load data from SQL database.

        Args:
            key: Unique identifier for the data
            default: Default value to return if key doesn't exist

        Returns:
            Loaded data or default value
        """
        session = self._get_session()
        try:
            record = session.query(StorageRecord).filter_by(key=key).first()

            if record:
                data = json.loads(record.data)
                logger.debug(f"Loaded data for key: {key}")
                return data
            else:
                logger.debug(f"Key '{key}' not found, using default value")
                return default if default is not None else []

        except (SQLAlchemyError, json.JSONDecodeError) as e:
            logger.error(f"Error loading data for key '{key}': {e}")
            return default if default is not None else []
        finally:
            session.close()

    def exists(self, key: str) -> bool:
        """Check if data exists in database.

        Args:
            key: Unique identifier for the data

        Returns:
            True if data exists, False otherwise
        """
        session = self._get_session()
        try:
            exists = session.query(StorageRecord).filter_by(key=key).first() is not None
            return exists
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence for key '{key}': {e}")
            return False
        finally:
            session.close()

    def delete(self, key: str) -> bool:
        """Delete data from database.

        Args:
            key: Unique identifier for the data

        Returns:
            True if deletion was successful, False otherwise
        """
        session = self._get_session()
        try:
            record = session.query(StorageRecord).filter_by(key=key).first()

            if record:
                session.delete(record)
                session.commit()
                logger.info(f"Deleted record with key: {key}")
                return True
            else:
                logger.debug(f"Key '{key}' not found, nothing to delete")
                return False

        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error deleting data for key '{key}': {e}")
            return False
        finally:
            session.close()

    def close(self) -> None:
        """Close database connections and dispose of the engine.

        This method should be called when the storage is no longer needed,
        especially in long-running applications.
        """
        try:
            self.engine.dispose()
            logger.info("Closed database connections")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")

    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            self.close()
        except Exception:
            pass  # Ignore errors during cleanup
