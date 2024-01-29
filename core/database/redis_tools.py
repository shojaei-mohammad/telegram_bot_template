"""
redis_tools.py

This module contains utility functions to interact with a Redis database using the aioredis library.
It provides asynchronous functions to set, get, and delete shared data, making it particularly suited
for applications like chatbots.

For connection management, it exposes two main functions: `initialize_redis` and `close_redis`
to establish and terminate the connection, respectively.

Note: Ensure that Redis server is running and reachable at the specified REDIS_URL.
"""
import json
from typing import Optional, Any

import aioredis

from core.data import settings
from core.utils.logger import LoggerSingleton

logger = LoggerSingleton.get_logger()

# Create a global Redis pool. We'll initialize this in the app startup.
redis: Optional[aioredis.Redis] = None


async def initialize_redis():
    """
    Initialize the Redis connection.

    Raises:
        aioredis.RedisError: If there's an issue connecting to the Redis server.
    """
    global redis
    try:
        redis = aioredis.from_url(settings.REDIS_URL)
        logger.info("Successfully initialized redis database")
    except aioredis.RedisError as e:
        logger.error(f"Error initializing Redis: {e}")
        raise


async def close_redis():
    """
    Close the Redis connection.

    Raises:
        aioredis.RedisError: If there's an issue closing the connection.
    """
    if redis:
        try:
            await redis.close()
            logger.info("Redis connection closed.")
        except aioredis.RedisError as e:
            logger.error(f"Error closing Redis connection: {e}")
            raise


async def set_shared_data(
    chat_id: int,
    key: str,
    value: Any,
    cache_time: int = 86400,
    persistent: bool = False,
) -> None:
    """
    Store data associated with a chat_id and key in Redis with an optional expiration time.

    Args:
        chat_id (int): Identifier for the chat session.
        key (str): The key under which data is stored.
        value (Any): The data to be stored.
        cache_time (int, optional): Expiration time in seconds. Defaults to 86400 seconds (24 hours).
        persistent (bool, optional): If True, the data will be persistent and not expire. Defaults to False.

    Raises:
        aioredis.RedisError: If there's an issue setting data in Redis.
    """
    redis_key = f"{chat_id}:{key}"
    try:
        serialized_value = json.dumps(value)
        if persistent:
            await redis.set(redis_key, serialized_value)
            logger.info(f"Persistently set data for key '{redis_key}'")
        else:
            await redis.setex(redis_key, cache_time, serialized_value)
            logger.info(
                f"Set data for key '{redis_key}' with expiration of {cache_time} seconds"
            )
    except aioredis.RedisError as e:
        logger.error(f"Error setting data for key '{redis_key}': {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error when setting data for key '{redis_key}': {e}")
        raise


async def get_shared_data(chat_id: int, key: str) -> Optional[Any]:
    """
    Fetch data associated with a chat_id and key from Redis.

    Args:
        chat_id (int): Identifier for the chat session.
        key (str): The key under which data is stored.

    Returns:
        Optional[Any]: The fetched data, or None if the key doesn't exist.

    Raises:
        aioredis.RedisError: If there's an issue fetching data from Redis.
    """
    redis_key = f"{chat_id}:{key}"
    try:
        value = await redis.get(redis_key)
        if value is not None:
            deserialized_value = json.loads(value.decode("utf-8"))
            logger.info(f"Fetched data for key '{redis_key}'")
            return deserialized_value
        else:
            logger.info(f"No data found for key '{redis_key}'")
            return None
    except aioredis.RedisError as e:
        logger.error(f"Error fetching data for key '{redis_key}': {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error when fetching data for key '{redis_key}': {e}")
        raise


async def delete_shared_data(chat_id: int, key: Optional[str] = None) -> None:
    """
    Delete data associated with a chat_id and optionally a specific key from Redis.

    Args:
        chat_id (int): Identifier for the chat session.
        key (Optional[str]): The key under which data is stored.
                             If None, all keys associated with the chat_id will be deleted.

    Raises:
        aioredis.RedisError: If there's an issue deleting data from Redis.
    """
    try:
        if key:
            redis_key = f"{chat_id}:{key}"
            await redis.delete(redis_key)
            logger.info(f"Deleted data for key '{redis_key}'")
        else:
            keys = await redis.keys(f"{chat_id}:*")
            for k in keys:
                await redis.delete(k)
            logger.info(f"Deleted all data for chat_id '{chat_id}'")
    except aioredis.RedisError as e:
        logger.error(
            f"Error deleting data for chat_id '{chat_id}' and key '{key}': {e}"
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error when deleting data for chat_id '{chat_id}' and key '{key}': {e}"
        )
        raise


__all__ = [
    "initialize_redis",
    "set_shared_data",
    "get_shared_data",
    "delete_shared_data",
    "close_redis",
]
