from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API details
    PROJECT_NAME: str = "AI Interview Backend"

    # Database settings
    DATABASE_URL: str
    # Security settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Google Gemini API settings
    GEMINI_API_KEY: str

    # Google OAuth2 settings
    GOOGLE_REDIRECT_URI: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_CLIENT_ID: str
    ELEVENLABS_API_KEY: str
    DATABASE_URL: str
    OPENAI_API_KEY: str
    ASSEMBLYAI_API_KEY: str

    ELEVENLABS_API_KEY: str
    # CORS settings

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


@lru_cache
def get_settings() -> Settings:
    """Get settings instance"""
    print(settings.GOOGLE_REDIRECT_URI)
    return settings
