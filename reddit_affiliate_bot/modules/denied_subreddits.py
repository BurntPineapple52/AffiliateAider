import sqlite3
from pathlib import Path
from typing import List, Set

class DeniedSubreddits:
    """Manages a persistent database of subreddits that deny affiliate links."""
    
    def __init__(self, db_path: str = "data/denied_subreddits.db"):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(exist_ok=True)
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database schema if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS denied_subreddits (
                    subreddit TEXT PRIMARY KEY,
                    added_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reason TEXT
                )
            """)
    
    def add(self, subreddit: str, reason: str = "") -> None:
        """Add a subreddit to the denied list."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO denied_subreddits (subreddit, reason) VALUES (?, ?)",
                (subreddit.lower(), reason)
            )
    
    def is_denied(self, subreddit: str) -> bool:
        """Check if a subreddit is in the denied list."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM denied_subreddits WHERE subreddit = ?",
                (subreddit.lower(),)
            )
            return cursor.fetchone() is not None
    
    def get_all(self) -> Set[str]:
        """Get all denied subreddits as a set."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT subreddit FROM denied_subreddits")
            return {row[0] for row in cursor.fetchall()}
