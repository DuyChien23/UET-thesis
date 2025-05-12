"""
Base module for services.
Contains the base class for all services.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

T = TypeVar('T')


class Service(ABC):
    """
    Base abstract class for all services.
    """
    
    @abstractmethod
    def setup(self):
        """
        Set up the service. This method is called during application startup.
        """
        pass
    
    @abstractmethod
    def shutdown(self):
        """
        Shut down the service. This method is called during application shutdown.
        """
        pass


class CachedService(Service, Generic[T]):
    """
    Base abstract class for services with caching support.
    """
    
    def __init__(self, cache_client=None):
        """
        Initialize the cached service.
        
        Args:
            cache_client: The cache client to use
        """
        self.cache_client = cache_client
    
    @abstractmethod
    def get_cache_key(self, *args, **kwargs) -> str:
        """
        Get the cache key for the given parameters.
        
        Returns:
            str: The cache key
        """
        pass
    
    @abstractmethod
    def get_cache_ttl(self) -> int:
        """
        Get the time-to-live (TTL) for cached items in seconds.
        
        Returns:
            int: The TTL in seconds
        """
        pass
    
    async def get_from_cache(self, cache_key: str) -> Optional[T]:
        """
        Get an item from the cache.
        
        Args:
            cache_key (str): The cache key
            
        Returns:
            Optional[T]: The cached item, or None if not in cache
        """
        if not self.cache_client:
            return None
            
        return await self.cache_client.get(cache_key)
    
    async def set_in_cache(self, cache_key: str, value: T) -> bool:
        """
        Set an item in the cache.
        
        Args:
            cache_key (str): The cache key
            value (T): The value to cache
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.cache_client:
            return False
            
        return await self.cache_client.set(cache_key, value, expire=self.get_cache_ttl())
    
    async def delete_from_cache(self, cache_key: str) -> bool:
        """
        Delete an item from the cache.
        
        Args:
            cache_key (str): The cache key
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.cache_client:
            return False
            
        return await self.cache_client.delete(cache_key)
    
    async def flush_cache(self) -> bool:
        """
        Flush all cached items.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.cache_client:
            return False
            
        return await self.cache_client.flush() 