from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    ENVIRONMENT: str = "development"
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Expense Sharing API"
    
    # Database settings
    DB_ECHO: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

