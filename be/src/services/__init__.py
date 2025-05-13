"""
Service module initialization.
Provides functions to initialize and access all services.
"""

import logging
from typing import Dict, Any, Optional

from src.services.verification import VerificationService
from src.services.public_keys import PublicKeyService
from src.services.algorithms import AlgorithmService
from src.db.repositories.verification import VerificationRepository
from src.db.repositories.public_keys import PublicKeyRepository
from src.db.repositories.users import UserRepository
from src.db.session import get_db_session
from src.config.settings import get_settings
from src.cache.redis import get_redis_client

logger = logging.getLogger(__name__)

# Global service instances
_verification_service: Optional[VerificationService] = None
_public_key_service: Optional[PublicKeyService] = None
_algorithm_service: Optional[AlgorithmService] = None


async def init_services(db_session=None, cache_client=None):
    """
    Initialize all services.
    
    Args:
        db_session: Optional database session (for testing)
        cache_client: Optional Redis cache client
    """
    global _verification_service, _public_key_service
    
    settings = get_settings()
    
    # Get DB session and repositories
    db = db_session if db_session is not None else await get_db_session()
    
    # Initialize repositories
    public_key_repo = PublicKeyRepository(db)
    verification_repo = VerificationRepository(db)
    user_repo = UserRepository(db)
    
    # Create Redis client if enabled and not provided
    if cache_client is None and settings.redis_enabled:
        try:
            cache_client = await get_redis_client()
        except Exception as e:
            logger.warning(f"Failed to initialize Redis client: {str(e)}")
    
    # Initialize services
    _public_key_service = PublicKeyService(
        public_key_repo=public_key_repo,
        user_repo=user_repo,
        cache_client=cache_client
    )
    
    _verification_service = VerificationService(
        public_key_service=_public_key_service,
        verification_repo=verification_repo,
        public_key_repo=public_key_repo,
        user_repo=user_repo,
        cache_client=cache_client
    )
    
    logger.info("Services initialized")


async def shutdown_services():
    """Shutdown all services."""
    global _verification_service, _public_key_service, _algorithm_service
    
    logger.info("Shutting down services")
    
    if _verification_service:
        _verification_service.shutdown()
        
    if _public_key_service:
        _public_key_service.shutdown()
        
    if _algorithm_service:
        _algorithm_service.shutdown()
    
    logger.info("Services shut down")


def get_verification_service() -> VerificationService:
    """Get the verification service."""
    global _verification_service
    if not _verification_service:
        raise RuntimeError("Verification service not initialized")
    return _verification_service


def get_public_key_service() -> PublicKeyService:
    """Get the public key service."""
    global _public_key_service
    if not _public_key_service:
        raise RuntimeError("Public key service not initialized")
    return _public_key_service


def get_algorithm_service() -> AlgorithmService:
    """Get the algorithm service."""
    global _algorithm_service
    if not _algorithm_service:
        raise RuntimeError("Algorithm service not initialized")
    return _algorithm_service 