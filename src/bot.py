"""Main entry point for the quit smoking bot.

This module imports and runs the QuitSmokingBot from the new refactored structure.
"""

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from src.quit_smoking.bot import main

if __name__ == "__main__":
    main()
