import random
import time
from typing import List, Optional
from dataclasses import dataclass
from loguru import logger

from prawwrapper import RedditWrapper
from config import RedditConfig

@dataclass
class AccountStats:
    account_id: str
    last_used: float
    post_count: int
    success_count: int
    error_count: int

class AccountManager:
    """Manages rotation between multiple Reddit accounts"""
    
    def __init__(self, accounts: List[RedditConfig]):
        self.accounts = accounts
        self.account_stats = []
        # Initialize all accounts
        self.wrappers = [RedditWrapper(config) for config in accounts]
        # Setup stats tracking
        for i, config in enumerate(accounts):
            self.account_stats.append(AccountStats(
                account_id=f"{config.username}",
                last_used=0,
                post_count=0,
                success_count=0,
                error_count=0
            ))
        logger.info(f"Initialized account manager with {len(accounts)} accounts")

    def get_next_account(self, strategy: str = "round_robin") -> Optional[RedditWrapper]:
        """Get next available account wrapper based on rotation strategy"""
        if not self.wrappers:
            return None

        if strategy == "random":
            return random.choice(self.wrappers)

        # Default round-robin strategy
        current_idx = min(
            range(len(self.account_stats)),
            key=lambda i: self.account_stats[i].last_used
        )
        
        # Check rate limits
        if self.account_stats[current_idx].post_count >= config.max_posts_per_account:
            next_available = min(
                range(len(self.account_stats)),
                key=lambda i: self.account_stats[i].post_count
            )
            current_idx = next_available

        self.account_stats[current_idx].post_count += 1
        self.account_stats[current_idx].last_used = time.time()
        return self.wrappers[current_idx]

    def update_stats(self, account_id: str, success: bool = True):
        """Update usage statistics for an account"""
        for stats in self.account_stats:
            if stats.account_id == account_id:
                if success:
                    stats.success_count += 1
                else:
                    stats.error_count += 1
                break
