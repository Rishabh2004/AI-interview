import logging
from functools import lru_cache

from prisma import Prisma

# Setup logging
logger = logging.getLogger(__name__)


# Use lru_cache for singleton pattern
@lru_cache(maxsize=1)
def get_prisma() -> Prisma:
    """Get the Prisma client singleton instance."""
    return Prisma()


# For backward compatibility


async def connect_db():
    """Connect to the database. Called during application startup."""
    try:
        await prisma.connect()
        logger.info("Connected to Prisma database")
    except Exception as e:
        logger.error(f"Failed to connect to Prisma: {e}")
        raise


async def disconnect_db():
    """Disconnect from the database. Called during application shutdown."""
    try:
        await prisma.disconnect()
        logger.info("Disconnected from Prisma database")
    except Exception as e:
        logger.error(f"Error disconnecting from Prisma: {e}")


prisma = get_prisma()

__all__ = ["prisma", "get_prisma", "connect_db", "disconnect_db"]
