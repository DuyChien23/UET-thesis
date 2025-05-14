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
        # Clear cache first to force update
        cache_key = self.get_cache_key()
        if self.cache_client:
            try:
                await self.cache_client.delete(cache_key)
                logger.info("Cleared algorithm cache to force update")
            except Exception as e:
                logger.warning(f"Failed to clear algorithm cache: {e}")
        
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
                                "algorithm_id": str(algorithm_with_curves.id),
                                "algorithm_name": algorithm_with_curves.name,
                                "description": curve.description,
                                "parameters": curve.parameters
                            }
                            algorithm_info["curves"].append(curve_info)
                    
                    algorithms.append(algorithm_info)
        
        # Update the cache
        await self.set_in_cache(cache_key, algorithms)
        
        return algorithms
    
    async def get_all_curves(self) -> List[Dict[str, Any]]:
        """
        Get information about all curves across all algorithms.
        Returns data in a format suitable for the signing API.
        
        Returns:
            A list of algorithm information dictionaries with their curves
        """
        # Get all algorithms from database
        algorithms = await self.get_all_algorithms()
        
        # Reformat the data for curve lookup
        result = []
        for algorithm in algorithms:
            curve_dict = {}
            for curve in algorithm["curves"]:
                curve_dict[curve["name"]] = {
                    "id": curve["id"],
                    "algorithm_id": curve["algorithm_id"],
                    "algorithm_name": curve["algorithm_name"],
                    "description": curve["description"],
                    "parameters": curve["parameters"]
                }
                
            if curve_dict:  # Only include algorithms that have curves
                result.append({
                    "algorithm_name": algorithm["name"],
                    "algorithm_type": algorithm["type"],
                    "curves": curve_dict
                })
                
        return result
    
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
                        "algorithm_id": str(algorithm_with_curves.id),
                        "algorithm_name": algorithm_with_curves.name,
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
    
    async def create_algorithm(self, algorithm_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new algorithm in the database.
        
        Args:
            algorithm_data: Dictionary with algorithm data
            
        Returns:
            The created algorithm data
            
        Raises:
            ValueError: If an algorithm with the same name already exists
        """
        async with self.session_factory() as session:
            # Check if algorithm with this name already exists
            existing_algorithm = await self.algorithm_repository.get_by_name(
                session, algorithm_data["name"]
            )
            
            if existing_algorithm:
                raise ValueError(f"Algorithm with name '{algorithm_data['name']}' already exists")
            
            # Create algorithm ID
            algorithm_id = str(uuid.uuid4())
            
            # Prepare algorithm data
            algorithm_entity = {
                "id": algorithm_id,
                "name": algorithm_data["name"],
                "type": algorithm_data["type"],
                "description": algorithm_data.get("description", ""),
                "is_default": algorithm_data.get("is_default", False),
                "status": "enabled"  # New algorithms are enabled by default
            }
            
            # Insert into database
            created_algorithm = await self.algorithm_repository.create(session, algorithm_entity)
            await session.commit()
            
            # Clear cache
            if self.cache_client:
                await self.cache_client.delete(self.get_cache_key())
                await self.cache_client.delete(self.get_cache_key(algorithm_data["name"]))
            
            # Format response
            result = {
                "id": str(created_algorithm.id),
                "name": created_algorithm.name,
                "type": created_algorithm.type,
                "description": created_algorithm.description,
                "is_default": created_algorithm.is_default,
                "status": created_algorithm.status,
                "curves": []  # New algorithm has no curves
            }
            
            return result
    
    async def update_algorithm(self, algorithm_id: str, algorithm_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing algorithm.
        
        Args:
            algorithm_id: The ID of the algorithm to update
            algorithm_data: Dictionary with algorithm update data
            
        Returns:
            The updated algorithm data
            
        Raises:
            KeyError: If the algorithm is not found
            ValueError: If updating to a name that already exists
        """
        async with self.session_factory() as session:
            # Get the algorithm
            algorithm = await self.algorithm_repository.get(session, algorithm_id)
            
            if not algorithm:
                raise KeyError(f"Algorithm with ID {algorithm_id} not found")
            
            # Check name uniqueness if name is being updated
            if "name" in algorithm_data and algorithm_data["name"] != algorithm.name:
                existing = await self.algorithm_repository.get_by_name(
                    session, algorithm_data["name"]
                )
                if existing:
                    raise ValueError(f"Algorithm with name '{algorithm_data['name']}' already exists")
            
            # Clear cache before update
            if self.cache_client:
                await self.cache_client.delete(self.get_cache_key())
                await self.cache_client.delete(self.get_cache_key(algorithm.name))
            
            # Prepare update data
            update_data = {}
            for field in ["name", "type", "description", "is_default", "status"]:
                if field in algorithm_data and algorithm_data[field] is not None:
                    update_data[field] = algorithm_data[field]
            
            # Update algorithm
            updated_algorithm = await self.algorithm_repository.update(
                session, algorithm.id, update_data
            )
            await session.commit()
            
            # Format response
            algorithm_with_curves = await self.algorithm_repository.get_with_curves(
                session, str(updated_algorithm.id)
            )
            
            result = {
                "id": str(updated_algorithm.id),
                "name": updated_algorithm.name,
                "type": updated_algorithm.type,
                "description": updated_algorithm.description,
                "is_default": updated_algorithm.is_default,
                "status": updated_algorithm.status,
                "curves": []
            }
            
            # Add curves information
            if algorithm_with_curves and algorithm_with_curves.curves:
                for curve in algorithm_with_curves.curves:
                    if curve.status == "enabled":
                        curve_info = {
                            "id": str(curve.id),
                            "name": curve.name,
                            "algorithm_id": str(algorithm_with_curves.id),
                            "algorithm_name": algorithm_with_curves.name,
                            "description": curve.description,
                            "parameters": curve.parameters
                        }
                        result["curves"].append(curve_info)
            
            return result
    
    async def delete_algorithm(self, algorithm_id: str) -> Dict[str, Any]:
        """
        Delete (disable) an algorithm.
        
        Args:
            algorithm_id: The ID of the algorithm to delete
            
        Returns:
            A dictionary with deletion status
            
        Raises:
            KeyError: If the algorithm is not found
        """
        async with self.session_factory() as session:
            # Get the algorithm
            algorithm = await self.algorithm_repository.get(session, algorithm_id)
            
            if not algorithm:
                raise KeyError(f"Algorithm with ID {algorithm_id} not found")
            
            # Get algorithm name before deletion (for cache clearing)
            algorithm_name = algorithm.name
            
            # Update the algorithm to disabled status (logical deletion)
            await self.algorithm_repository.update(
                session, algorithm.id, {"status": "disabled"}
            )
            
            # Disable all curves associated with this algorithm
            await self.curve_repository.disable_all_by_algorithm(session, algorithm_id)
            
            await session.commit()
            
            # Clear cache
            if self.cache_client:
                await self.cache_client.delete(self.get_cache_key())
                await self.cache_client.delete(self.get_cache_key(algorithm_name))
            
            return {
                "id": str(algorithm.id),
                "name": algorithm.name,
                "status": "disabled",
                "message": f"Algorithm '{algorithm.name}' has been disabled"
            }
    
    async def create_curve(self, curve_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new curve for an algorithm.
        
        Args:
            curve_data: Dictionary with curve data
            
        Returns:
            The created curve data
            
        Raises:
            KeyError: If the algorithm is not found
            ValueError: If a curve with the same name already exists for this algorithm
        """
        async with self.session_factory() as session:
            # Check if algorithm exists
            algorithm = await self.algorithm_repository.get(
                session, curve_data["algorithm_id"]
            )
            
            if not algorithm:
                raise KeyError(f"Algorithm with ID {curve_data['algorithm_id']} not found")
            
            # Check if curve with this name already exists for this algorithm
            existing_curve = await self.curve_repository.get_by_name_and_algorithm(
                session, curve_data["name"], curve_data["algorithm_id"]
            )
            
            if existing_curve:
                raise ValueError(
                    f"Curve with name '{curve_data['name']}' already exists for algorithm '{algorithm.name}'"
                )
            
            # Create curve ID
            curve_id = str(uuid.uuid4())
            
            # Prepare curve data
            curve_entity = {
                "id": curve_id,
                "name": curve_data["name"],
                "algorithm_id": curve_data["algorithm_id"],
                "description": curve_data.get("description", ""),
                "parameters": curve_data["parameters"],
                "status": "enabled"  # New curves are enabled by default
            }
            
            # Insert into database
            created_curve = await self.curve_repository.create(session, curve_entity)
            await session.commit()
            
            # Clear cache
            if self.cache_client:
                await self.cache_client.delete(self.get_cache_key())
                await self.cache_client.delete(self.get_cache_key(algorithm.name))
            
            # Format response
            result = {
                "id": str(created_curve.id),
                "name": created_curve.name,
                "algorithm_id": str(algorithm.id),
                "algorithm_name": algorithm.name,
                "description": created_curve.description,
                "parameters": created_curve.parameters,
                "status": created_curve.status
            }
            
            return result
    
    async def update_curve(self, curve_id: str, curve_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing curve.
        
        Args:
            curve_id: The ID of the curve to update
            curve_data: Dictionary with curve update data
            
        Returns:
            The updated curve data
            
        Raises:
            KeyError: If the curve is not found
            ValueError: If updating to a name that already exists
        """
        async with self.session_factory() as session:
            # Get the curve
            curve = await self.curve_repository.get(session, curve_id)
            
            if not curve:
                raise KeyError(f"Curve with ID {curve_id} not found")
            
            # Get the algorithm
            algorithm = await self.algorithm_repository.get(session, str(curve.algorithm_id))
            
            if not algorithm:
                raise KeyError(f"Algorithm with ID {curve.algorithm_id} not found")
            
            # Check name uniqueness if name is being updated
            if "name" in curve_data and curve_data["name"] != curve.name:
                existing = await self.curve_repository.get_by_name_and_algorithm(
                    session, curve_data["name"], str(curve.algorithm_id)
                )
                if existing:
                    raise ValueError(
                        f"Curve with name '{curve_data['name']}' already exists for algorithm '{algorithm.name}'"
                    )
            
            # Clear cache before update
            if self.cache_client:
                await self.cache_client.delete(self.get_cache_key())
                await self.cache_client.delete(self.get_cache_key(algorithm.name))
            
            # Prepare update data
            update_data = {}
            for field in ["name", "description", "parameters", "status"]:
                if field in curve_data and curve_data[field] is not None:
                    update_data[field] = curve_data[field]
            
            # Update curve
            updated_curve = await self.curve_repository.update(
                session, curve.id, update_data
            )
            await session.commit()
            
            # Format response
            result = {
                "id": str(updated_curve.id),
                "name": updated_curve.name,
                "algorithm_id": str(algorithm.id),
                "algorithm_name": algorithm.name,
                "description": updated_curve.description,
                "parameters": updated_curve.parameters,
                "status": updated_curve.status
            }
            
            return result
    
    async def delete_curve(self, curve_id: str) -> Dict[str, Any]:
        """
        Delete (disable) a curve.
        
        Args:
            curve_id: The ID of the curve to delete
            
        Returns:
            A dictionary with deletion status
            
        Raises:
            KeyError: If the curve is not found
        """
        async with self.session_factory() as session:
            # Get the curve
            curve = await self.curve_repository.get(session, curve_id)
            
            if not curve:
                raise KeyError(f"Curve with ID {curve_id} not found")
            
            # Get the algorithm for cache clearing
            algorithm = await self.algorithm_repository.get(session, str(curve.algorithm_id))
            
            # Update the curve to disabled status (logical deletion)
            await self.curve_repository.update(
                session, curve.id, {"status": "disabled"}
            )
            await session.commit()
            
            # Clear cache
            if self.cache_client and algorithm:
                await self.cache_client.delete(self.get_cache_key())
                await self.cache_client.delete(self.get_cache_key(algorithm.name))
            
            return {
                "id": str(curve.id),
                "name": curve.name,
                "status": "disabled",
                "message": f"Curve '{curve.name}' has been disabled"
            }
    
    async def get_algorithm_by_id(self, algorithm_id: str) -> Dict[str, Any]:
        """
        Get algorithm information by ID.
        
        Args:
            algorithm_id: Algorithm ID
            
        Returns:
            Algorithm information
            
        Raises:
            KeyError: If algorithm with the given ID is not found
        """
        async with self.session_factory() as session:
            algorithm = await self.algorithm_repository.get_by_id(session, algorithm_id)
            
            if not algorithm:
                raise KeyError(f"Algorithm with id '{algorithm_id}' not found")
            
            # Get all curves for this algorithm
            curves = await self.curve_repository.get_by_algorithm_id(session, algorithm_id)
            
            result = {
                "id": algorithm.id,
                "name": algorithm.name,
                "type": algorithm.type,
                "description": algorithm.description,
                "is_default": algorithm.is_default,
                "status": algorithm.status,
                "curves": [{"id": curve.id, "name": curve.name, "status": curve.status} for curve in curves]
            }
            
            return result
    
    async def get_curves(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Get all curves with optional filtering.
        
        Args:
            filters: Optional filters such as algorithm_id, status
            
        Returns:
            List of curves
        """
        if filters is None:
            filters = {}
            
        async with self.session_factory() as session:
            curves = await self.curve_repository.get_all_with_filters(session, **filters)
            
            result = []
            for curve in curves:
                # Get algorithm info
                algorithm = await self.algorithm_repository.get_by_id(session, str(curve.algorithm_id))
                
                curve_data = {
                    "id": str(curve.id),
                    "name": curve.name,
                    "algorithm_id": str(curve.algorithm_id),
                    "algorithm_name": algorithm.name if algorithm else None,
                    "description": curve.description,
                    "parameters": curve.parameters,
                    "status": curve.status,
                    "created_at": curve.created_at.isoformat() if curve.created_at else None
                }
                result.append(curve_data)
                
            return result
    
    async def get_curve_by_id(self, curve_id: str) -> Dict[str, Any]:
        """
        Get curve information by ID.
        
        Args:
            curve_id: Curve ID
            
        Returns:
            Curve information
            
        Raises:
            KeyError: If curve with the given ID is not found
        """
        async with self.session_factory() as session:
            curve = await self.curve_repository.get_by_id(session, curve_id)
            
            if not curve:
                raise KeyError(f"Curve with id '{curve_id}' not found")
                
            # Get algorithm info
            algorithm = await self.algorithm_repository.get_by_id(session, str(curve.algorithm_id))
            
            result = {
                "id": str(curve.id),
                "name": curve.name,
                "algorithm_id": str(curve.algorithm_id),
                "algorithm_name": algorithm.name if algorithm else None,
                "description": curve.description,
                "parameters": curve.parameters,
                "status": curve.status,
                "created_at": curve.created_at.isoformat() if curve.created_at else None
            }
            
            return result 