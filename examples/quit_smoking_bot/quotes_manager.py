"""Motivational quotes management for quit smoking bot."""

import json
import logging
import random
from pathlib import Path
from typing import List

from telegram_bot_stack.storage import StorageBackend

logger = logging.getLogger(__name__)


class QuotesManager:
    """Manages motivational quotes for the quit smoking bot.

    Loads quotes from a JSON file and provides random quote selection.

    Args:
        storage: Storage backend instance
        quotes_file: Path to quotes JSON file (default: data/quotes.json)
    """

    def __init__(self, storage: StorageBackend = None, quotes_file: Path = None):
        """Initialize quotes manager."""
        self.storage = storage
        self.quotes_file = quotes_file or Path(__file__).parent / "data" / "quotes.json"
        self.quotes: List[str] = self._load_quotes()

    def _load_quotes(self) -> List[str]:
        """Load motivational quotes from file."""
        # Try loading from file directly
        if self.quotes_file.exists():
            try:
                with open(self.quotes_file, encoding="utf-8") as f:
                    quotes = json.load(f)
            except Exception as e:
                logger.error(f"Error loading quotes from {self.quotes_file}: {e}")
                quotes = []
        else:
            logger.info(
                f"Quotes file {self.quotes_file} not found, using default quotes"
            )
            quotes = [
                "Each day without cigarettes is a victory over yourself. - Mark Twain",
                "The best time to quit was yesterday. The second best time is now.",
                "Your health is an investment, not an expense.",
            ]

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
