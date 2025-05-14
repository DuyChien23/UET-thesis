"""
Verification service for digital signatures.
Provides functionality for verifying signatures and logging verification attempts.
"""

import json
import hashlib
import logging
import base64
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
import uuid

from src.core.registry import get_algorithm_registry, get_algorithm_provider
from src.db.repositories.verification import VerificationRepository
from src.db.repositories.public_keys import PublicKeyRepository
from src.db.repositories.users import UserRepository
from src.db.models.verification import VerificationStatus
from src.services.base import CachedService
from src.services.public_keys import PublicKeyService
from src.core.algorithms.utils import encode_signature, decode_signature
from src.core.algorithms.ecdsa.provider import ECDSAProvider
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
        document: str,
        signature: str,
        public_key: str,
        algorithm_name: str,
        curve_name: str,
    ) -> Tuple[bool, Dict[str, Any]]:
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
            Tuple[bool, Dict[str, Any]]: True if the signature is valid, False otherwise
            
        Raises:
            ValueError: If the public key or algorithm is not found
        """

        provider = get_algorithm_provider(algorithm_name)
        if not provider:
            raise ValueError(f"Algorithm provider '{algorithm_name}' not found")
        
        return provider.verify(document, signature, public_key, curve_name)
    
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
            "document_hash": record.document_hash,
            "signature": record.signature,
            "algorithm_name": record.algorithm_name,
            "curve_name": record.curve_name,
            "public_key_id": str(record.public_key_id),
            "status": record.status,
            "verified_at": record.verified_at,
            "verification_metadata": record.verification_metadata
        }
    
    async def get_user_verification_history(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get verification history for a user.
        
        Args:
            user_id: The user ID
            limit: Maximum number of records to return
            offset: Number of records to skip
            status: Filter by verification status
            start_date: Filter by verified_at (start date)
            end_date: Filter by verified_at (end date)
            
        Returns:
            Dictionary with verification records and pagination metadata
        """
        if not self.verification_repo:
            logger.warning("VerificationRepository not provided")
            return {"items": [], "total_count": 0, "offset": offset, "limit": limit}
            
        filters = {"user_id": user_id}
        
        if status:
            filters["status"] = status
            
        # Get total count first
        total_count = await self.verification_repo.count(
            filters=filters,
            start_date=start_date,
            end_date=end_date
        )
        
        # Get records with pagination
        records = await self.verification_repo.get_filtered_records(
            filters=filters,
            limit=limit,
            offset=offset,
            start_date=start_date,
            end_date=end_date,
            order_by="verified_at",
            order_desc=True
        )
        
        # Transform records to API schema format
        items = []
        for record in records:
            items.append({
                "id": str(record.id),
                "document_hash": record.document_hash,
                "public_key_id": str(record.public_key_id),
                "algorithm_name": record.algorithm_name,
                "curve_name": record.curve_name,
                "status": record.status,
                "verified_at": record.verified_at,
                "metadata": record.verification_metadata
            })
            
        return {
            "items": items,
            "total_count": total_count,
            "offset": offset,
            "limit": limit
        }
        
    async def delete_verification_record(self, record_id: str) -> bool:
        """
        Delete a verification record.
        
        Args:
            record_id: The ID of the verification record to delete
            
        Returns:
            bool: True if the record was deleted, False otherwise
        """
        if not self.verification_repo:
            logger.warning("VerificationRepository not provided")
            return False
            
        try:
            # Convert string ID to UUID if needed
            try:
                record_uuid = uuid.UUID(record_id)
            except ValueError:
                logger.error(f"Invalid UUID format for record_id: {record_id}")
                return False
                
            # Delete the record
            success = await self.verification_repo.delete(record_uuid)
            
            return success
        except Exception as e:
            logger.error(f"Error deleting verification record: {str(e)}")
            return False 