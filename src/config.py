"""
Configuration settings for MultiSportsBettingPlatform.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings."""
    
    def __init__(self):
        # Application
        self.app_name: str = "MultiSportsBettingPlatform"
        self.app_version: str = "1.0.0"
        self.debug: bool = os.getenv("DEBUG", "False").lower() == "true"
        
        # Server
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        
        # Database (using SQLite for development, Postgres for production)
        self.database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./multisports_betting.db")
        
        # Redis (optional for development)
        self.redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # Security
        self.secret_key: str = os.environ.get("SECRET_KEY")
        if not self.secret_key and not self.debug:
            raise ValueError("SECRET_KEY environment variable is required in production")
        elif not self.secret_key:
            self.secret_key = "dev-secret-key-change-in-production" # Fallback ONLY for debug mode
        self.algorithm: str = "HS256"
        self.access_token_expire_minutes: int = 30
        
        # Auth settings (configurable for different deployments)
        self.session_timeout_hours: int = int(os.getenv("SESSION_TIMEOUT_HOURS", "24"))
        self.remember_me_timeout_days: int = int(os.getenv("REMEMBER_ME_TIMEOUT_DAYS", "30"))
        self.max_login_attempts: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
        self.lockout_duration_minutes: int = int(os.getenv("LOCKOUT_DURATION_MINUTES", "15"))
        self.rate_limit_requests_per_hour: int = int(os.getenv("RATE_LIMIT_REQUESTS_PER_HOUR", "100"))
        
        # API Keys (use environment variables only)
        self.anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
        self.perplexity_api_key: Optional[str] = os.getenv("PERPLEXITY_API_KEY")
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        
        # Sports APIs (optional for basic functionality)
        self.espn_api_key: Optional[str] = os.getenv("ESPN_API_KEY")
        self.sports_data_api_key: Optional[str] = os.getenv("SPORTS_DATA_API_KEY")
        self.the_odds_api_key: Optional[str] = os.getenv("THE_ODDS_API_KEY")

# Global settings instance
settings = Settings() 