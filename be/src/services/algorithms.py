"""
Service for managing digital signature algorithms.
Provides information about available algorithms and their capabilities.
"""

import logging
from typing import Dict, Any, List, Optional
import uuid

from sqlalchemy.ext.asyncio import async_sessionmaker

from src.core.registry import get_algorithm_registry
from src.services.base import CachedService
from src.db.repositories.algorithms import AlgorithmRepository, CurveRepository
from src.db.session import get_session_factory

logger = logging.getLogger(__name__)


class AlgorithmService(CachedService[Dict[str, Any]]):
    """
    Service for providing information about supported algorithms.
    """
    
    def __init__(self, db_session=None, cache_client=None):
        """
        Initialize the algorithm service.
        
        Args:
            db_session: Database session factory
            cache_client: Redis cache client
        """
        super().__init__(cache_client)
        self.algorithm_registry = get_algorithm_registry()
        self.algorithm_repository = AlgorithmRepository()
        self.curve_repository = CurveRepository()
        self.session_factory = db_session if db_session is not None else get_session_factory()
    
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
    
    async def load_algorithms(self):
        """
        Load algorithms from the database and cache them.
        Used for testing purposes.
        """
        # Clear any existing cache
        if self.cache_client:
            try:
                await self.cache_client.delete(self.get_cache_key())
            except Exception as e:
                logger.warning(f"Failed to clear algorithm cache: {e}")
        
        # Load algorithms from database
        algorithms = await self.get_all_algorithms()
        logger.info(f"Loaded {len(algorithms)} algorithms")
        
        return algorithms
    
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
        
        # Get the information from the database
        async with self.session_factory() as session:
            # Query all algorithms from the database
            algorithm_entities = await self.algorithm_repository.get_multi(session)
            
            # Convert to dictionaries and include curves information
            algorithms = []
            for algorithm_entity in algorithm_entities:
                algorithm_with_curves = await self.algorithm_repository.get_with_curves(
                    session, algorithm_entity.id
                )
                
                if algorithm_with_curves:
                    # Create algorithm info dict
                    algorithm_info = {
                        "id": str(algorithm_with_curves.id),
                        "name": algorithm_with_curves.name,
                        "type": algorithm_with_curves.type,
                        "description": algorithm_with_curves.description,
                        "is_default": algorithm_with_curves.is_default,
                        "status": algorithm_with_curves.status,
                        "curves": []
                    }
                    
                    # Add curves information
                    for curve in algorithm_with_curves.curves:
                        if curve.status == "enabled":
                            curve_info = {
                                "id": str(curve.id),
                                "name": curve.name,
                                "description": curve.description,
                                "parameters": curve.parameters
                            }
                            algorithm_info["curves"].append(curve_info)
                    
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
        
        # Get the algorithm from database
        async with self.session_factory() as session:
            algorithm_entity = await self.algorithm_repository.get_by_name(session, algorithm_name)
            
            if not algorithm_entity:
                raise KeyError(f"Algorithm not found: {algorithm_name}")
            
            # Get the algorithm with its curves
            algorithm_with_curves = await self.algorithm_repository.get_with_curves(
                session, algorithm_entity.id
            )
            
            # Build the result dictionary
            result = {
                "id": str(algorithm_with_curves.id),
                "name": algorithm_with_curves.name,
                "type": algorithm_with_curves.type,
                "description": algorithm_with_curves.description,
                "is_default": algorithm_with_curves.is_default,
                "status": algorithm_with_curves.status,
                "curves": []
            }
            
            # Add curves information
            for curve in algorithm_with_curves.curves:
                if curve.status == "enabled":
                    curve_info = {
                        "id": str(curve.id),
                        "name": curve.name,
                        "description": curve.description,
                        "parameters": curve.parameters
                    }
                    result["curves"].append(curve_info)
        
        # Cache the result
        await self.set_in_cache(cache_key, result)
        
        return result
    
    async def get_default_algorithm(self) -> Dict[str, Any]:
        """
        Get information about the default algorithm.
        
        Returns:
            A dictionary with algorithm details
        """
        # Try to get from cache first
        cache_key = self.get_cache_key("default")
        cached_result = await self.get_from_cache(cache_key)
        
        if cached_result:
            logger.info("Found cached default algorithm")
            return cached_result
        
        # Try to get the default algorithm from registry
        try:
            default_provider = self.algorithm_registry.get_default_algorithm()
            if default_provider:
                default_algorithm_name = default_provider.get_algorithm_name()
                
                # Get algorithm info
                return await self.get_algorithm_info(default_algorithm_name)
        except Exception as e:
            logger.warning(f"Error getting default algorithm from registry: {e}")
        
        # If no default from registry, get all algorithms
        algorithms = await self.get_all_algorithms()
        
        # If any algorithms exist, return the first one
        if algorithms:
            return algorithms[0]
            
        # No algorithms found
        raise ValueError("No algorithms found in the database") 