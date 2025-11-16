"""Motivational quotes management for quit smoking bot."""

import logging
import random
from typing import List

from src.config import QUOTES_FILE
from src.core.storage import Storage

logger = logging.getLogger(__name__)


class QuotesManager:
    """Manages motivational quotes for the quit smoking bot."""

    def __init__(self, storage: Storage = None):
        """Initialize quotes manager.

        Args:
            storage: Optional Storage instance. If not provided, loads directly from file.
        """
        self.storage = storage
        self.quotes: List[str] = self._load_quotes()

    def _load_quotes(self) -> List[str]:
        """Load motivational quotes from file."""
        if self.storage:
            quotes = self.storage.load(QUOTES_FILE.name, [])
        else:
            # Fallback to direct file loading for backwards compatibility
            import json
            from pathlib import Path

            filepath = Path(QUOTES_FILE)
            if filepath.exists():
                try:
                    with open(filepath, encoding="utf-8") as f:
                        quotes = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading quotes from {filepath}: {e}")
                    quotes = []
            else:
                logger.info(f"Quotes file {filepath} not found, using empty list")
                quotes = []

        # Create extended quotes list to cover 20 years (240 months)
        if quotes and len(quotes) < 240:
            extended_quotes = quotes.copy()
            for i in range(len(quotes), 240):
                extended_quotes.append(quotes[i % len(quotes)])
            return extended_quotes
        return quotes

    def get_random_quote(self, user_id: str = "global") -> str:
        """Get a random motivational quote.

        Args:
            user_id: User ID (for future per-user quote tracking)

        Returns:
            Random quote string
        """
        if not self.quotes:
            return (
                "Each day without cigarettes is a victory over yourself. - Mark Twain"
            )

        # Select a random quote
        return random.choice(self.quotes)
