"""
Redis cache client for the application.
Provides async Redis client for caching operations.
"""

import json
import logging
from typing import Any, Optional, Union
import aioredis
from aioredis import Redis

logger = logging.getLogger(__name__)


class RedisCache:
    """
    Redis cache client for the application.
    """
    
    def __init__(self, redis_url: str):
        """
        Initialize the Redis cache client.
        
        Args:
            redis_url (str): Redis connection URL
        """
        self.redis_url = redis_url
        self.redis: Optional[Redis] = None
    
    async def connect(self) -> None:
        """
        Connect to Redis.
        """
        logger.info(f"Connecting to Redis at {self.redis_url}")
        self.redis = await aioredis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        logger.info("Connected to Redis")
    
    async def disconnect(self) -> None:
        """
        Disconnect from Redis.
        """
        if self.redis:
            logger.info("Disconnecting from Redis")
            await self.redis.close()
            logger.info("Disconnected from Redis")
    
    async def get(self, key: str) -> Any:
        """
        Get a value from the cache.
        
        Args:
            key (str): The cache key
            
        Returns:
            Any: The cached value, or None if not found
        """
        if not self.redis:
            logger.warning("Redis not connected")
            return None
        
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting value from Redis: {str(e)}")
            return None
    
    async def set(self, key: str, value: Any, expire: int = 0) -> bool:
        """
        Set a value in the cache.
        
        Args:
            key (str): The cache key
            value (Any): The value to cache
            expire (int): Expiration time in seconds (0 = no expiration)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.redis:
            logger.warning("Redis not connected")
            return False
        
        try:
            serialized_value = json.dumps(value)
            if expire > 0:
                await self.redis.setex(key, expire, serialized_value)
            else:
                await self.redis.set(key, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Error setting value in Redis: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key (str): The cache key
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.redis:
            logger.warning("Redis not connected")
            return False
        
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting value from Redis: {str(e)}")
            return False
    
    async def flush(self) -> bool:
        """
        Flush all cached values.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.redis:
            logger.warning("Redis not connected")
            return False
        
        try:
            await self.redis.flushdb()
            return True
        except Exception as e:
            logger.error(f"Error flushing Redis: {str(e)}")
            return False
    
    async def keys(self, pattern: str = "*") -> list[str]:
        """
        Get all keys matching a pattern.
        
        Args:
            pattern (str): Key pattern to match
            
        Returns:
            list[str]: List of matching keys
        """
        if not self.redis:
            logger.warning("Redis not connected")
            return []
        
        try:
            return await self.redis.keys(pattern)
        except Exception as e:
            logger.error(f"Error getting keys from Redis: {str(e)}")
            return [] 