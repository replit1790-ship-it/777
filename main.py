#!/usr/bin/env python3
"""
Bot initialization and main entry point.
"""

import os
import sys
from typing import Optional


class Bot:
    """Base bot class for initialization and management."""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize the bot with configuration.
        
        Args:
            token: Optional bot token. If not provided, will attempt to load from environment.
        """
        self.token = token or os.getenv('BOT_TOKEN')
        if not self.token:
            raise ValueError("Bot token not provided and BOT_TOKEN environment variable not set")
        
        self.is_running = False
        print("[BOT] Initialization complete")
    
    def start(self) -> None:
        """Start the bot."""
        if self.is_running:
            print("[BOT] Bot is already running")
            return
        
        self.is_running = True
        print("[BOT] Bot started successfully")
    
    def stop(self) -> None:
        """Stop the bot."""
        if not self.is_running:
            print("[BOT] Bot is not running")
            return
        
        self.is_running = False
        print("[BOT] Bot stopped")
    
    def status(self) -> str:
        """Get bot status."""
        return "running" if self.is_running else "stopped"


def main() -> int:
    """
    Main entry point for the bot application.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Initialize bot
        bot = Bot()
        
        # Start bot
        bot.start()
        
        # Log status
        print(f"[MAIN] Bot status: {bot.status()}")
        
        # Keep bot running (in production, this would be an event loop)
        print("[MAIN] Bot is ready")
        
        return 0
    
    except Exception as e:
        print(f"[ERROR] Failed to initialize bot: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
