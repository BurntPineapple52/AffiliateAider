import os
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
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
class ProxyConfig:
    host: str = get_env('PROXY_HOST', '')
    port: int = int(get_env('PROXY_PORT', '0'))
    username: str = get_env('PROXY_USERNAME', '')
    password: str = get_env('PROXY_PASSWORD', '')
    protocol: str = get_env('PROXY_PROTOCOL', 'http')
    enabled: bool = bool(get_env('PROXY_ENABLED', 'False').lower() == 'true')

@dataclass
class RedditConfig:
    client_id: str = get_env('REDDIT_CLIENT_ID')
    client_secret: str = get_env('REDDIT_CLIENT_SECRET')
    username: str = get_env('REDDIT_USERNAME')
    password: str = get_env('REDDIT_PASSWORD')
    user_agent: str = get_env('REDDIT_USER_AGENT', 'RedditAffiliateBot/1.0')
    redirect_uri: str = get_env('REDDIT_REDIRECT_URI', 'http://localhost:8080')
    refresh_token: str = get_env('REDDIT_REFRESH_TOKEN', '')
    delay_seconds: float = 10.0
    max_attempts: int = 3
    auth_method: str = 'password'  # 'password' or 'refresh_token'
    proxy: ProxyConfig = ProxyConfig()

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
    account_rotation_strategy: str = "round_robin"  # or "random" or "least_used"
    max_posts_per_account: int = 10  # per hour
    
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
