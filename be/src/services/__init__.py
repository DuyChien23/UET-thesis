"""
Service module initialization.
Provides functions to initialize and access all services.
"""

import logging
from typing import Dict, Any, Optional

from services.verification import VerificationService
from services.public_keys import PublicKeyService
from services.algorithms import AlgorithmService
from db.repositories.verification import VerificationRepository
from db.repositories.public_keys import PublicKeyRepository
from db.repositories.users import UserRepository

logger = logging.getLogger(__name__)

# Global service instances
_verification_service: Optional[VerificationService] = None
_public_key_service: Optional[PublicKeyService] = None
_algorithm_service: Optional[AlgorithmService] = None


def init_services(db_session, cache_client=None):
    """
    Initialize all services.
    
    Args:
        db_session: The database session
        cache_client: The Redis cache client (optional)
    """
    global _verification_service, _public_key_service, _algorithm_service
    
    logger.info("Initializing services")
    
    # Create repositories
    verification_repo = VerificationRepository(db_session)
    public_key_repo = PublicKeyRepository(db_session)
    user_repo = UserRepository(db_session)
    
    # Create services
    _verification_service = VerificationService(
        verification_repo=verification_repo,
        public_key_repo=public_key_repo,
        user_repo=user_repo,
        cache_client=cache_client
    )
    
    _public_key_service = PublicKeyService(
        public_key_repo=public_key_repo,
        user_repo=user_repo,
        cache_client=cache_client
    )
    
    _algorithm_service = AlgorithmService(cache_client=cache_client)
    
    # Initialize each service
    _verification_service.setup()
    _public_key_service.setup()
    _algorithm_service.setup()
    
    logger.info("Services initialized")


def shutdown_services():
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