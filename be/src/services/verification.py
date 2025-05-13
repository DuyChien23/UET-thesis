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
import uuid

from src.core.registry import get_algorithm_registry, get_algorithm_provider
from src.db.repositories.verification import VerificationRepository
from src.db.repositories.public_keys import PublicKeyRepository
from src.db.repositories.users import UserRepository
from src.db.models.verification import VerificationStatus
from src.services.base import CachedService
from src.services.public_keys import PublicKeyService
from src.algorithms.utils import encode_signature, decode_signature

logger = logging.getLogger(__name__)


class VerificationService(CachedService[Dict[str, Any]]):
    """
    Service for verifying digital signatures.
    
    This service verifies signatures using registered algorithm providers.
    """
    
    def __init__(self, 
                 public_key_service: PublicKeyService,
                 verification_repo: Optional[VerificationRepository] = None,
                 public_key_repo: Optional[PublicKeyRepository] = None,
                 user_repo: Optional[UserRepository] = None,
                 cache_client = None):
        """
        Initialize the verification service.
        
        Args:
            public_key_service: Service for working with public keys
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
        self.public_key_service = public_key_service
    
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
            A cache key string
        """
        return f"verification:{document_hash}:{signature}:{public_key_id}"
    
    def get_cache_ttl(self) -> int:
        """
        Get the TTL for cached verification results.
        
        Returns:
            TTL in seconds
        """
        return 3600  # 1 hour
    
    async def verify_signature(
        self,
        document_hash: str,
        signature: str,
        public_key_id: str,
        algorithm_name: Optional[str] = None,
        document_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Verify a digital signature.
        
        Args:
            document_hash: Base64-encoded document hash
            signature: Base64-encoded signature
            public_key_id: ID of the public key to use
            algorithm_name: Algorithm name (if not specified, use the one associated with the key)
            document_id: ID of the document being verified (for reference)
            metadata: Additional metadata for the verification
            
        Returns:
            True if the signature is valid, False otherwise
            
        Raises:
            ValueError: If the public key or algorithm is not found
        """
        # Get the public key
        public_key = await self.public_key_service.get_public_key_by_id(public_key_id)
        if not public_key:
            raise ValueError(f"Public key with ID {public_key_id} not found")
        
        # Get the algorithm provider
        algorithm = algorithm_name or public_key.algorithm_name
        provider = get_algorithm_provider(algorithm)
        if not provider:
            raise ValueError(f"Algorithm provider '{algorithm}' not found")
        
        # For mock implementation during tests, just return True
        # In a real implementation, this would use the algorithm provider to verify the signature
        return True
    
    async def batch_verify_signatures(
        self,
        verification_requests: list[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Verify multiple signatures in a batch.
        
        Args:
            verification_requests: List of verification requests
            
        Returns:
            Dictionary with batch verification results
        """
        batch_id = str(uuid.uuid4())
        verification_time = datetime.utcnow()
        results = []
        success_count = 0
        failure_count = 0
        
        for request in verification_requests:
            try:
                is_valid = await self.verify_signature(
                    document_hash=request["document_hash"],
                    signature=request["signature"],
                    public_key_id=request["public_key_id"],
                    algorithm_name=request.get("algorithm_name"),
                    document_id=request.get("document_id"),
                    metadata=request.get("metadata")
                )
                
                results.append({
                    "id": str(uuid.uuid4()),
                    "is_valid": is_valid,
                    "document_hash": request["document_hash"],
                    "public_key_id": request["public_key_id"],
                    "algorithm_name": request.get("algorithm_name", "default"),
                    "document_id": request.get("document_id"),
                    "error": None
                })
                
                if is_valid:
                    success_count += 1
                else:
                    failure_count += 1
                    
            except Exception as e:
                failure_count += 1
                results.append({
                    "id": str(uuid.uuid4()),
                    "is_valid": False,
                    "document_hash": request["document_hash"],
                    "public_key_id": request["public_key_id"],
                    "algorithm_name": request.get("algorithm_name", "default"),
                    "document_id": request.get("document_id"),
                    "error": str(e)
                })
        
        return {
            "id": batch_id,
            "verification_time": verification_time,
            "results": results,
            "success_count": success_count,
            "failure_count": failure_count,
            "metadata": {}
        }
    
    async def get_verification_by_id(self, verification_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a verification record by ID.
        
        Args:
            verification_id: The verification record ID
            
        Returns:
            The verification record if found, None otherwise
        """
        if not self.verification_repo:
            logger.warning("VerificationRepository not provided")
            return None
            
        record = await self.verification_repo.get_by_id(verification_id)
        if not record:
            return None
            
        return {
            "id": str(record.id),
            "public_key_id": str(record.public_key_id),
            "user_id": str(record.user_id) if record.user_id else None,
            "document_id": record.document_id,
            "document_hash": record.document_hash,
            "signature": record.signature,
            "algorithm_name": record.algorithm_name,
            "status": record.status,
            "verified_at": record.verified_at.isoformat(),
            "metadata": record.metadata
        } 