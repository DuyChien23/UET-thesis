"""
Service for managing digital signature algorithms.
Provides information about available algorithms and their capabilities.
"""

import logging
from typing import Dict, Any, List, Optional

from core.registry import get_algorithm_registry
from services.base import CachedService

logger = logging.getLogger(__name__)


class AlgorithmService(CachedService[Dict[str, Any]]):
    """
    Service for providing information about supported algorithms.
    """
    
    def __init__(self, cache_client=None):
        """
        Initialize the algorithm service.
        
        Args:
            cache_client: Redis cache client
        """
        super().__init__(cache_client)
        self.algorithm_registry = get_algorithm_registry()
    
    def setup(self):
        """Set up the algorithm service."""
        logger.info("Setting up algorithm service")
    
    def shutdown(self):
        """Shut down the algorithm service."""
        logger.info("Shutting down algorithm service")
    
    def get_cache_key(self, algorithm_name: Optional[str] = None) -> str:
        """
        Generate a cache key for algorithm information.
        
        Args:
            algorithm_name: The algorithm name or None for all algorithms
            
        Returns:
            A cache key
        """
        if algorithm_name:
            return f"algorithm:{algorithm_name}"
        return "algorithms:all"
    
    def get_cache_ttl(self) -> int:
        """Get the TTL for cached algorithm information."""
        return 3600 * 24  # 24 hours since algorithm info rarely changes
    
    async def get_all_algorithms(self) -> List[Dict[str, Any]]:
        """
        Get information about all supported algorithms.
        
        Returns:
            A list of algorithm information dictionaries
        """
        # Try to get from cache first
        cache_key = self.get_cache_key()
        cached_result = await self.get_from_cache(cache_key)
        
        if cached_result:
            logger.info("Found cached algorithm list")
            return cached_result
        
        # Get the information from the registry
        algorithm_names = self.algorithm_registry.get_registered_algorithms()
        algorithms = []
        
        for name in algorithm_names:
            algorithm_info = await self.get_algorithm_info(name)
            algorithms.append(algorithm_info)
        
        # Cache the result
        await self.set_in_cache(cache_key, algorithms)
        
        return algorithms
    
    async def get_algorithm_info(self, algorithm_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific algorithm.
        
        Args:
            algorithm_name: The name of the algorithm
            
        Returns:
            A dictionary with algorithm details
            
        Raises:
            KeyError: If the algorithm is not found
        """
        # Try to get from cache first
        cache_key = self.get_cache_key(algorithm_name)
        cached_result = await self.get_from_cache(cache_key)
        
        if cached_result:
            logger.info(f"Found cached algorithm info for {algorithm_name}")
            return cached_result
        
        # Get the algorithm provider
        try:
            algorithm = self.algorithm_registry.get_algorithm(algorithm_name)
        except KeyError:
            raise KeyError(f"Algorithm not found: {algorithm_name}")
        
        # Get algorithm details
        supported_curves = algorithm.get_supported_curves()
        
        # Build the result
        result = {
            "name": algorithm.get_algorithm_name(),
            "type": algorithm.get_algorithm_type(),
            "is_default": self.algorithm_registry.get_default_algorithm().get_algorithm_name() == algorithm_name,
            "curves": [
                {
                    "name": curve_name,
                    "bit_size": curve_info.get("bit_size"),
                    "description": curve_info.get("description")
                } 
                for curve_name, curve_info in supported_curves.items()
            ],
            "supported_key_formats": algorithm.get_supported_formats() if hasattr(algorithm, "get_supported_formats") else []
        }
        
        # Cache the result
        await self.set_in_cache(cache_key, result)
        
        return result
    
    async def get_default_algorithm(self) -> Dict[str, Any]:
        """
        Get information about the default algorithm.
        
        Returns:
            A dictionary with algorithm details
        """
        default_algorithm = self.algorithm_registry.get_default_algorithm()
        if not default_algorithm:
            raise ValueError("No default algorithm is configured")
            
        return await self.get_algorithm_info(default_algorithm.get_algorithm_name()) 