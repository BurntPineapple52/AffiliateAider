import os
from dataclasses import dataclass
from typing import List, Optional
import json

@dataclass
class SERPConfig:
    api_key: str
    provider: str = "scale_serp"
    search_engine: str = "google"
    region: str = "us"
    delay_seconds: float = 2.0
    
@dataclass
class RedditConfig:
    client_id: str
    client_secret: str
    username: str
    password: str
    user_agent: str = "RedditAffiliateBot/1.0"
    delay_seconds: float = 10.0
    max_attempts: int = 3

@dataclass
class AmazonConfig:
    access_key: str
    secret_key: str
    partner_tag: str
    country: str = "US"

@dataclass
class NLPConfig:
    api_key: str
    provider: str = "openai"

@dataclass
class BotConfig:
    serp: SERPConfig
    reddit: List[RedditConfig]  # Multiple accounts
    amazon: AmazonConfig
    nlp: NLPConfig
    denied_subreddits_file: str = "denied_subreddits.json"
    log_file: str = "bot.log"
    
    @classmethod
    def from_json(cls, json_file: str) -> "BotConfig":
        """Load config from JSON file"""
        with open(json_file) as f:
            data = json.load(f)
        
        return cls(
            serp=SERPConfig(**data["serp"]),
            reddit=[RedditConfig(**account) for account in data["reddit"]],
            amazon=AmazonConfig(**data["amazon"]),
            nlp=NLPConfig(**data["nlp"])
        )
