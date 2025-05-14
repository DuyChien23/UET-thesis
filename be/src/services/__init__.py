"""
Service module initialization.
Provides functions to initialize and access all services.
"""

import logging
from typing import Dict, Any, Optional

from src.services.verification import VerificationService
from src.services.public_keys import PublicKeyService
from src.services.algorithms import AlgorithmService
from src.services.signing import SigningService
from src.db.repositories.verification import VerificationRepository
from src.db.repositories.public_keys import PublicKeyRepository
from src.db.repositories.users import UserRepository
from src.db.session import get_session_factory
from src.config.settings import get_settings
from src.cache.redis import get_redis_client

logger = logging.getLogger(__name__)

# Global service instances
_verification_service: Optional[VerificationService] = None
_public_key_service: Optional[PublicKeyService] = None
_algorithm_service: Optional[AlgorithmService] = None
_signing_service: Optional[SigningService] = None


async def init_services(session_factory=None, cache_client=None):
    """
    Initialize all services.
    
    Args:
        session_factory: Optional database session factory (for testing)
        cache_client: Optional Redis cache client
    """
    global _verification_service, _public_key_service, _algorithm_service, _signing_service
    
    settings = get_settings()
    
    # Get session factory
    factory = session_factory if session_factory is not None else get_session_factory()
    
    # Create Redis client if enabled and not provided
    if cache_client is None and settings.redis_enabled:
        try:
            cache_client = await get_redis_client()
        except Exception as e:
            logger.warning(f"Failed to initialize Redis client: {str(e)}")
    
    # Create a temporary session for initializing services
    async with factory() as db:
        # Initialize repositories
        public_key_repo = PublicKeyRepository(factory)
        verification_repo = VerificationRepository(factory)
        user_repo = UserRepository(factory)
        
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
        
        # Initialize algorithm service
        _algorithm_service = AlgorithmService(
            db_session=factory,
            cache_client=cache_client
        )
        
        # Initialize signing service
        _signing_service = SigningService(
            algorithm_service=_algorithm_service
        )
    
    logger.info("Services initialized")


async def shutdown_services():
    """Shutdown all services."""
    global _verification_service, _public_key_service, _algorithm_service, _signing_service
    
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


def get_signing_service() -> SigningService:
    """Get the signing service."""
    global _signing_service
    if not _signing_service:
        raise RuntimeError("Signing service not initialized")
    return _signing_service


def set_algorithm_service(service: AlgorithmService):
    """Set the algorithm service (for testing)."""
    global _algorithm_service
    _algorithm_service = service 