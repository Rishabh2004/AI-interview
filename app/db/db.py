from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import Optional
from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger("db")

mongodb_client: Optional[AsyncIOMotorClient] = None

settings = get_settings()


async def init_db(document_models):
    """Initialize database connection and setup Beanie ODM"""
    global mongodb_client

    logger.info("Connecting to MongoDB")
    mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(
        database=mongodb_client[settings.DB_NAME], document_models=document_models
    )
    logger.info(f"Connected to database: {settings.DB_NAME}")

    return mongodb_client


async def close_db_connection():
    """Close database connection"""
    global mongodb_client
    if mongodb_client is not None:
        mongodb_client.close()
