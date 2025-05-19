from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API details
    PROJECT_NAME: str = "AI Interview Backend"

    # Database settings
    DB_URL: str
    DB_NAME: str = "interview_db"

    # Security settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Google Gemini API settings
    GEMINI_API_KEY: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_CLIENT_ID: str
    # CORS settings

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


@lru_cache
def get_settings() -> Settings:
    """Get settings instance"""
    return settings
