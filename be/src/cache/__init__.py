"""
Cache module initialization.
Provides functions to initialize and access cache clients.
"""

import logging
from typing import Optional

from .redis import RedisCache
from .mock import MockCache
from src.config.settings import get_settings

logger = logging.getLogger(__name__)

# Global cache client
_cache_client = None


async def init_cache(redis_url: str = None):
    """
    Initialize the cache.
    
    Args:
        redis_url (str, optional): Redis connection URL. If not provided, it will be taken from settings.
        
    Returns:
        The cache client
    """
    global _cache_client
    
    if _cache_client is not None:
        logger.warning("Cache already initialized")
        return _cache_client
    
    settings = get_settings()
    
    if settings.mock_services:
        logger.info("Using in-memory mock cache")
        _cache_client = MockCache()
    else:
        if redis_url is None:
            redis_url = settings.redis_url
            
        logger.info(f"Initializing Redis cache with URL: {redis_url}")
        _cache_client = RedisCache(redis_url)
        await _cache_client.connect()
    
    return _cache_client


async def shutdown_cache():
    """Shutdown the cache."""
    global _cache_client
    
    if _cache_client is not None:
        logger.info("Shutting down cache")
        
        if isinstance(_cache_client, RedisCache):
            await _cache_client.disconnect()
            
        _cache_client = None
        
        logger.info("Cache shut down")


def get_cache_client():
    """
    Get the cache client.
    
    Returns:
        The cache client
    """
    global _cache_client
    
    if _cache_client is None:
        raise RuntimeError("Cache not initialized")
    
    return _cache_client 