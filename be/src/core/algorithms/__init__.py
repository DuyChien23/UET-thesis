"""
Digital signature algorithm initialization module.
This module imports and registers all available algorithm providers.
"""

import logging
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.registry import get_algorithm_registry
from src.core.algorithms.ecdsa.provider import ECDSAProvider
from src.core.algorithms.eddsa.provider import EdDSAProvider
from src.core.algorithms.rsa.provider import RSAProvider
from src.db.session import get_session_factory
from src.db.models.algorithms import Algorithm, Curve

logger = logging.getLogger(__name__)

async def load_algorithms_from_db():
    """
    Load algorithms and their curves from the database.
    
    Returns:
        dict: A dictionary of algorithms and their curves
    """
    result = {}
    
    try:
        # Get session factory
        session_factory = get_session_factory()
        
        # Create a session and load algorithms
        async with session_factory() as session:
            # Query all algorithms with their curves
            query = select(Algorithm).options(selectinload(Algorithm.curves))
            algorithms = await session.execute(query)
            algorithm_list = algorithms.scalars().all()
            
            if not algorithm_list:
                logger.warning("No algorithms found in the database.")
                return result
            
            for algorithm in algorithm_list:
                algorithm_data = {
                    "id": algorithm.id,
                    "name": algorithm.name,
                    "type": algorithm.type,
                    "description": algorithm.description,
                    "curves": {}
                }
                
                for curve in algorithm.curves:
                    curve_data = {
                        "id": curve.id,
                        "name": curve.name,
                        "algorithm_id": str(algorithm.id),
                        "algorithm_name": algorithm.name,
                        "parameters": curve.parameters,
                        "description": curve.description,
                        "status": curve.status
                    }
                    algorithm_data["curves"][curve.name] = curve_data
                
                result[algorithm.name] = algorithm_data
                
            logger.info(f"Loaded {len(result)} algorithms from the database.")
            return result
    except Exception as e:
        logger.error(f"Error loading algorithms from database: {e}")
        return {}

def initialize_algorithms():
    """
    Initialize all available signature algorithm providers.
    This function registers all providers with the central registry.
    """
    logger.info("Initializing signature algorithm providers")
    
    registry = get_algorithm_registry()
    
    # Register ECDSA
    registry.register("ECDSA", ECDSAProvider())
    
    # Register EdDSA
    registry.register("EdDSA", EdDSAProvider())
    
    # Register RSA
    registry.register("RSA-SHA256", RSAProvider())
    
    logger.info(f"Registered {len(registry.providers)} algorithm providers: {', '.join(registry.providers.keys())}")
    
    return registry.providers 