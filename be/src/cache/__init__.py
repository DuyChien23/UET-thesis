"""
Cache module initialization.
Provides functions to initialize and access the cache client.
"""

import logging
from typing import Optional
from .redis import RedisCache

logger = logging.getLogger(__name__)

# Global cache client
_cache_client: Optional[RedisCache] = None


async def init_cache(redis_url: str) -> RedisCache:
    """
    Initialize the cache client.
    
    Args:
        redis_url (str): Redis connection URL
        
    Returns:
        RedisCache: The initialized cache client
    """
    global _cache_client
    
    logger.info("Initializing cache client")
    _cache_client = RedisCache(redis_url)
    await _cache_client.connect()
    logger.info("Cache client initialized")
    
    return _cache_client


async def shutdown_cache() -> None:
    """Shutdown the cache client."""
    global _cache_client
    
    if _cache_client:
        logger.info("Shutting down cache client")
        await _cache_client.disconnect()
        logger.info("Cache client shut down")


def get_cache_client() -> Optional[RedisCache]:
    """
    Get the cache client.
    
    Returns:
        Optional[RedisCache]: The cache client, or None if not initialized
    """
    global _cache_client
    return _cache_client 