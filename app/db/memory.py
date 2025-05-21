from mem0 import AsyncMemory
from app.core.config import get_settings
# from app.core.logger import logger
from mem0.configs.base import MemoryConfig
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import PayloadSchemaType
from typing import Optional, List, Dict, Any

settings = get_settings()

config = {
    "embedder": {
        "provider": "openai",
        "config": {
            "api_key": settings.OPENAI_API_KEY,
            "model": "text-embedding-3-small",
        },
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "url": settings.QDRANT_HOST,
            "api_key": settings.QDRANT_API_KEY,
            "collection_name": "resume",
        },
    },
    "llm": {
        "provider": "gemini",
        "config": {"api_key": settings.GEMINI_API_KEY, "model": "gemini-1.5-flash"},
    },
    "history_db_path": "./mem0_resume_history.sqlite"
}

mem_client: Optional[AsyncMemory] = None


async def init_mem0():
    global mem_client
    try:
        mem_client = await AsyncMemory.from_config(config)
        print(f"Mem0 history DB path: {mem_client.db.db_path}")
        client = AsyncQdrantClient(
            url=settings.QDRANT_HOST, api_key=settings.QDRANT_API_KEY
        )
        await client.create_payload_index(
            collection_name="resume",
            field_name="user_id",
            field_schema=PayloadSchemaType.UUID,
        )
        print("Successfully connected to Mem0")
    except Exception as e:
        print(f"Error initializing Mem0: {str(e)}")
        raise e


async def add_memory(
    user_id: str,
    message: str,
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs
) -> bool:
    if not mem_client:
        await init_mem0()

    try:
        print("MEssage========================>", message)
        await mem_client.add(
            messages={"content": message, "role": "user"},
            user_id=user_id,
            metadata=metadata or {},
        )
        print(f"Memory added for user {user_id}")
        return True
    except Exception as e:
        print(f"Error adding memory for user {user_id}: {str(e)}")
        return False


async def retrieve_memories(
    user_id: str,
    query: str,
    limit: int = 5,
):
    if not mem_client:
        await init_mem0()

    try:
        print("Query========================>", query)
        results = await mem_client.search(
            query=query,
            user_id=user_id,
            limit=limit,
        )
        print("Results========================>", results)
        memories = results.get("results", [])

        return [
        {
            "memory": result["memory"],
            "score": result["score"],
            "metadata": result.get("metadata", {})
        }
        for result in memories
        ]
    except Exception as e:
        print(f"Error retrieving memories for user {user_id}: {str(e)}")
        return []


async def clear_user_memories(user_id: str) -> bool:
    if not mem_client:
        await init_mem0()

    try:
        await mem_client.delete(filters={"user_id": user_id})
        print(f"Cleared all memories for user {user_id}")
        return True
    except Exception as e:
        print(f"Error clearing memories for user {user_id}: {str(e)}")
        return False


def get_mem0():
    return mem_client