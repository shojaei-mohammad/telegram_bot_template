"""
redis_tools.py

This module contains utility functions to interact with a Redis database using the aioredis library.
It provides asynchronous functions to set, get, and delete shared data, making it particularly suited
for applications like chatbots.

For connection management, it exposes two main functions: `initialize_redis` and `close_redis`
to establish and terminate the connection, respectively.

Note: Ensure that Redis server is running and reachable at the specified REDIS_URL.
"""
from typing import Optional, Any

import aioredis

from data import config
from utils.logger import configure_logger

logger = configure_logger(f"{__name__}.log")

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
        redis = aioredis.from_url(config.REDIS_URL)
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


async def set_shared_data(chat_id: int, key: str, value: Any) -> None:
    """
    Store data associated with a chat_id and key in Redis.

    Args:
        chat_id (int): Identifier for the chat session.
        key (str): The key under which data is stored.
        value (Any): The data to be stored.

    Raises:
        aioredis.RedisError: If there's an issue setting data in Redis.
    """
    redis_key = f"{chat_id}:{key}"
    try:
        await redis.set(redis_key, str(value))
    except aioredis.RedisError as e:
        logger.error(f"Error setting data for key '{redis_key}': {e}")
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
            return value.decode("utf-8")
        return None
    except aioredis.RedisError as e:
        logger.error(f"Error fetching data for key '{redis_key}': {e}")
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
        else:
            keys = await redis.keys(f"{chat_id}:*")
            for k in keys:
                await redis.delete(k)
    except aioredis.RedisError as e:
        logger.error(
            f"Error deleting data for chat_id '{chat_id}' and key '{key}': {e}"
        )
        raise


__all__ = [
    "initialize_redis",
    "set_shared_data",
    "get_shared_data",
    "delete_shared_data",
    "close_redis",
]
