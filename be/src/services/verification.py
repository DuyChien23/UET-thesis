"""
Verification service for digital signatures.
Provides functionality for verifying signatures and logging verification attempts.
"""

import json
import hashlib
import logging
import base64
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from core.registry import get_algorithm_registry
from db.repositories.verification import VerificationRepository
from db.repositories.public_keys import PublicKeyRepository
from db.repositories.users import UserRepository
from db.models.verification import VerificationStatus
from services.base import CachedService

logger = logging.getLogger(__name__)


class VerificationService(CachedService[Dict[str, Any]]):
    """
    Service for verification of digital signatures.
    """
    
    def __init__(self, 
                 verification_repo: VerificationRepository,
                 public_key_repo: PublicKeyRepository,
                 user_repo: UserRepository,
                 cache_client=None):
        """
        Initialize the verification service.
        
        Args:
            verification_repo: Repository for verification records
            public_key_repo: Repository for public keys
            user_repo: Repository for users
            cache_client: Redis cache client
        """
        super().__init__(cache_client)
        self.verification_repo = verification_repo
        self.public_key_repo = public_key_repo
        self.user_repo = user_repo
        self.algorithm_registry = get_algorithm_registry()
    
    def setup(self):
        """Set up the verification service."""
        logger.info("Setting up verification service")
    
    def shutdown(self):
        """Shut down the verification service."""
        logger.info("Shutting down verification service")
    
    def get_cache_key(self, document_hash: str, signature: str, public_key_id: str) -> str:
        """
        Generate a cache key for a verification request.
        
        Args:
            document_hash: The document hash
            signature: The signature
            public_key_id: The public key ID
            
        Returns:
            A unique cache key for the verification
        """
        composite_key = f"{document_hash}:{signature}:{public_key_id}"
        return f"verification:{hashlib.sha256(composite_key.encode()).hexdigest()}"
    
    def get_cache_ttl(self) -> int:
        """Get the TTL for cached verification results."""
        return 3600  # 1 hour
    
    async def verify_signature(self, 
                              document_hash: str, 
                              signature: str,
                              public_key_id: str,
                              algorithm_name: Optional[str] = None,
                              user_id: Optional[str] = None,
                              document_id: Optional[str] = None,
                              metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Verify a digital signature.
        
        Args:
            document_hash: The hash of the document (base64 encoded)
            signature: The signature to verify (base64 encoded)
            public_key_id: The ID of the public key to use
            algorithm_name: The name of the algorithm to use (optional)
            user_id: The ID of the user performing the verification (optional)
            document_id: The ID of the document being verified (optional)
            metadata: Additional metadata for the verification (optional)
            
        Returns:
            A dictionary containing the verification result and details
        """
        # Try to get from cache first
        cache_key = self.get_cache_key(document_hash, signature, public_key_id)
        cached_result = await self.get_from_cache(cache_key)
        
        if cached_result:
            logger.info(f"Found cached verification result for {cache_key}")
            return cached_result
        
        # Get the public key from the database
        public_key_record = await self.public_key_repo.get_by_id(public_key_id)
        if not public_key_record:
            logger.warning(f"Public key not found: {public_key_id}")
            return self._create_error_result("Public key not found")
        
        # Determine which algorithm to use
        if algorithm_name is None:
            algorithm_name = public_key_record.algorithm_name
        
        try:
            algorithm = self.algorithm_registry.get_algorithm(algorithm_name)
        except KeyError:
            logger.warning(f"Algorithm not supported: {algorithm_name}")
            return self._create_error_result(f"Algorithm not supported: {algorithm_name}")
        
        # Extract necessary parameters for verification
        try:
            curve_name = public_key_record.curve_name if hasattr(public_key_record, 'curve_name') else None
            public_key_value = public_key_record.key_data
            
            # Verify the signature
            verification_success = algorithm.verify(
                document_hash=document_hash,
                signature=signature,
                public_key=public_key_value,
                curve_name=curve_name
            )
            
            # Prepare the result
            timestamp = datetime.utcnow()
            status = VerificationStatus.SUCCESS if verification_success else VerificationStatus.FAILURE
            
            # Log the verification result to the database
            verification_record = await self.verification_repo.create(
                public_key_id=public_key_id,
                user_id=user_id,
                document_id=document_id,
                document_hash=document_hash,
                signature=signature,
                algorithm_name=algorithm_name,
                status=status,
                verified_at=timestamp,
                metadata=metadata or {}
            )
            
            # Create the result
            result = {
                "success": verification_success,
                "timestamp": timestamp.isoformat(),
                "verification_id": str(verification_record.id),
                "public_key_id": public_key_id,
                "algorithm": algorithm_name,
                "document_hash": document_hash
            }
            
            # Cache the result
            await self.set_in_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.exception(f"Error during signature verification: {str(e)}")
            return self._create_error_result(f"Verification error: {str(e)}")
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """
        Create an error result dictionary.
        
        Args:
            error_message: The error message
            
        Returns:
            A dictionary with error details
        """
        return {
            "success": False,
            "error": error_message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    async def get_verification_by_id(self, verification_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a verification record by ID.
        
        Args:
            verification_id: The verification record ID
            
        Returns:
            The verification record details or None if not found
        """
        record = await self.verification_repo.get_by_id(verification_id)
        if not record:
            return None
            
        return {
            "verification_id": str(record.id),
            "public_key_id": str(record.public_key_id),
            "user_id": str(record.user_id) if record.user_id else None,
            "document_id": str(record.document_id) if record.document_id else None,
            "document_hash": record.document_hash,
            "signature": record.signature,
            "algorithm_name": record.algorithm_name,
            "status": record.status.value,
            "verified_at": record.verified_at.isoformat(),
            "metadata": record.metadata
        } 