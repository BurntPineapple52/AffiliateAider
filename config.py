import os
from dataclasses import dataclass
from typing import List, Optional
import json
from dotenv import load_dotenv

def get_env(key: str, default: Optional[str] = None) -> str:
    """Get environment variable with validation"""
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Missing required environment variable: {key}")
    return value

@dataclass
class SERPConfig:
    api_key: str = get_env('SERP_API_KEY')
    provider: str = "scale_serp"
    search_engine: str = "google"
    region: str = "us"
    delay_seconds: float = 2.0
    
@dataclass
class RedditConfig:
    client_id: str = get_env('REDDIT_CLIENT_ID')
    client_secret: str = get_env('REDDIT_CLIENT_SECRET')
    username: str = get_env('REDDIT_USERNAME')
    password: str = get_env('REDDIT_PASSWORD')
    user_agent: str = get_env('REDDIT_USER_AGENT', 'RedditAffiliateBot/1.0')
    delay_seconds: float = 10.0
    max_attempts: int = 3

@dataclass
class AmazonConfig:
    access_key: str = get_env('AMAZON_ACCESS_KEY')
    secret_key: str = get_env('AMAZON_SECRET_KEY')
    partner_tag: str = get_env('AMAZON_PARTNER_TAG')
    country: str = "US"

@dataclass
class NLPConfig:
    api_key: str = get_env('NLP_API_KEY')
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
        load_dotenv()  # Load environment variables first
        with open(json_file) as f:
            data = json.load(f)
        
        return cls(
            serp=SERPConfig(**data.get("serp", {})),
            reddit=[RedditConfig(**account) for account in data.get("reddit", [])],
            amazon=AmazonConfig(**data.get("amazon", {})),
            nlp=NLPConfig(**data.get("nlp", {}))
        )
