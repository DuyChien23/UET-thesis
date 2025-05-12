"""
In-memory mock cache implementation for testing and development.
"""

import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class MockCache:
    """
    A simple in-memory cache implementation that mimics a Redis cache.
    Used for testing and development when Redis is not available.
    """
    
    def __init__(self):
        """Initialize the mock cache."""
        self.cache: Dict[str, Dict[str, Any]] = {}
        logger.info("Initialized in-memory mock cache")
    
    async def get(self, key: str) -> Any:
        """
        Get a value from the cache.
        
        Args:
            key (str): The cache key
            
        Returns:
            Any: The cached value, or None if not found or expired
        """
        if key not in self.cache:
            return None
        
        item = self.cache[key]
        
        # Check if expired
        if item["expiry"] and item["expiry"] < time.time():
            del self.cache[key]
            return None
        
        return item["value"]
    
    async def set(self, key: str, value: Any, expire: int = 0) -> bool:
        """
        Set a value in the cache.
        
        Args:
            key (str): The cache key
            value (Any): The value to cache
            expire (int): Expiration time in seconds (0 = no expiration)
            
        Returns:
            bool: True
        """
        expiry = time.time() + expire if expire > 0 else None
        
        self.cache[key] = {
            "value": value,
            "expiry": expiry
        }
        
        return True
    
    async def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key (str): The cache key
            
        Returns:
            bool: True if the key was deleted, False if it didn't exist
        """
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    async def flush(self) -> bool:
        """
        Flush all cached values.
        
        Returns:
            bool: True
        """
        self.cache.clear()
        return True
    
    async def keys(self, pattern: str = "*") -> list[str]:
        """
        Get all keys matching a pattern.
        Only supports exact match or "*" wildcard.
        
        Args:
            pattern (str): Key pattern to match
            
        Returns:
            list[str]: List of matching keys
        """
        if pattern == "*":
            return list(self.cache.keys())
        
        # Very simple pattern matching
        return [k for k in self.cache.keys() if k == pattern or 
                (pattern.endswith('*') and k.startswith(pattern[:-1]))] 