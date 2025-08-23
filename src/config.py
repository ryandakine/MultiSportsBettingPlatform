"""
Configuration settings for MultiSportsBettingPlatform.
"""

import os
from typing import Optional

class Settings:
    """Application settings."""
    
    def __init__(self):
        # Application
        self.app_name: str = "MultiSportsBettingPlatform"
        self.app_version: str = "1.0.0"
        self.debug: bool = True  # Set to True for development
        
        # Server
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        
        # Database (using SQLite for development)
        self.database_url: str = os.getenv("DATABASE_URL", "sqlite:///./multisports_betting.db")
        
        # Redis (optional for development)
        self.redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # Security
        self.secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
        self.algorithm: str = "HS256"
        self.access_token_expire_minutes: int = 30
        
        # API Keys (use environment variables only)
        self.anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
        self.perplexity_api_key: Optional[str] = os.getenv("PERPLEXITY_API_KEY")
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        
        # Sports APIs (optional for basic functionality)
        self.espn_api_key: Optional[str] = os.getenv("ESPN_API_KEY")
        self.sports_data_api_key: Optional[str] = os.getenv("SPORTS_DATA_API_KEY")

# Global settings instance
settings = Settings() 