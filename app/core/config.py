from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API details
    PROJECT_NAME: str = "AI Interview Backend"
    DEBUG: bool = True
    VERSION: str = "0.1.0"

    # Database settings
    MONGODB_URL: str
    DB_NAME: str = "interview_db"

    # Security settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Google Gemini API settings
    GEMINI_API_KEY: str
    
    # CORS settings
    ALLOWED_ORIGINS: list = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


@lru_cache
def get_settings() -> Settings:
    """Get settings instance"""
    return settings
