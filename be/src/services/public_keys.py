"""
Service for managing public keys.
Provides functionality for creating, retrieving, and validating public keys.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import base64
import uuid
import hashlib

from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_der_public_key

from src.core.registry import get_algorithm_registry
from src.db.repositories.public_keys import PublicKeyRepository
from src.db.repositories.users import UserRepository
from src.services.base import CachedService

logger = logging.getLogger(__name__)


class PublicKeyService(CachedService[Dict[str, Any]]):
    """
    Service for managing public keys.
    """
    
    def __init__(self, 
                 public_key_repo: PublicKeyRepository,
                 user_repo: UserRepository,
                 cache_client=None):
        """
        Initialize the public key service.
        
        Args:
            public_key_repo: Repository for public keys
            user_repo: Repository for users
            cache_client: Redis cache client
        """
        super().__init__(cache_client)
        self.public_key_repo = public_key_repo
        self.user_repo = user_repo
        self.algorithm_registry = get_algorithm_registry()
    
    def setup(self):
        """Set up the public key service."""
        logger.info("Setting up public key service")
    
    def shutdown(self):
        """Shut down the public key service."""
        logger.info("Shutting down public key service")
    
    def get_cache_key(self, key_id: str) -> str:
        """
        Generate a cache key for a public key.
        
        Args:
            key_id: The public key ID
            
        Returns:
            A cache key
        """
        return f"public_key:{key_id}"
    
    def get_cache_ttl(self) -> int:
        """Get the TTL for cached public keys."""
        return 3600 * 24  # 24 hours
    
    async def create_public_key(self, 
                                key_data: str, 
                                algorithm_name: str,
                                user_id: str,
                                name: Optional[str] = None,
                                description: Optional[str] = None,
                                curve_name: Optional[str] = None,
                                metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new public key.
        
        Args:
            key_data: The public key data (PEM or DER encoded)
            algorithm_name: The algorithm name
            user_id: The ID of the user who owns the key
            name: A name for the key (optional)
            description: A description for the key (optional)
            curve_name: The curve name for ECC algorithms (optional)
            metadata: Additional metadata for the key (optional)
            
        Returns:
            A dictionary with the created public key details
            
        Raises:
            ValueError: If the key data or algorithm is invalid
        """
        # Validate the algorithm
        try:
            algorithm = self.algorithm_registry.get_algorithm(algorithm_name)
        except KeyError:
            raise ValueError(f"Algorithm not supported: {algorithm_name}")
        
        # Validate the user exists
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")
        
        # Validate the public key format
        if not algorithm.validate_public_key(key_data, curve_name):
            raise ValueError("Invalid public key format")
        
        # Create the public key record
        public_key = await self.public_key_repo.create(
            key_data=key_data,
            algorithm_name=algorithm_name,
            user_id=user_id,
            name=name,
            description=description,
            curve_name=curve_name,
            metadata=metadata or {}
        )
        
        # Format the result
        result = self._format_key_result(public_key)
        
        # Cache the result
        await self.set_in_cache(self.get_cache_key(str(public_key.id)), result)
        
        return result
    
    async def get_public_key(self, key_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a public key by ID.
        
        Args:
            key_id: The public key ID
            
        Returns:
            The public key details or None if not found
        """
        # Try to get from cache first
        cache_key = self.get_cache_key(key_id)
        cached_result = await self.get_from_cache(cache_key)
        
        if cached_result:
            logger.info(f"Found cached public key for {key_id}")
            return cached_result
        
        # Get from database if not in cache
        public_key = await self.public_key_repo.get_by_id(key_id)
        if not public_key:
            return None
            
        # Format the result
        result = self._format_key_result(public_key)
        
        # Cache the result
        await self.set_in_cache(cache_key, result)
        
        return result
    
    async def get_user_public_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all public keys for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            A list of public key details
        """
        public_keys = await self.public_key_repo.get_by_user_id(user_id)
        return [self._format_key_result(key) for key in public_keys]
    
    async def delete_public_key(self, key_id: str, user_id: str) -> bool:
        """
        Delete a public key.
        
        Args:
            key_id: The public key ID
            user_id: The ID of the user who owns the key
            
        Returns:
            True if deleted, False otherwise
            
        Raises:
            ValueError: If the user does not own the key
        """
        # Get the key first to check ownership
        public_key = await self.public_key_repo.get_by_id(key_id)
        if not public_key:
            return False
            
        # Check ownership
        if str(public_key.user_id) != user_id:
            raise ValueError("User does not own this public key")
            
        # Delete from database
        success = await self.public_key_repo.delete(key_id)
        
        # Delete from cache if successful
        if success:
            await self.delete_from_cache(self.get_cache_key(key_id))
            
        return success
    
    def _format_key_result(self, public_key) -> Dict[str, Any]:
        """
        Format a public key record into a dictionary.
        
        Args:
            public_key: The public key record
            
        Returns:
            A dictionary with the public key details
        """
        return {
            "id": str(public_key.id),
            "name": public_key.name,
            "description": public_key.description,
            "algorithm_name": public_key.algorithm_name,
            "curve_name": public_key.curve_name,
            "user_id": str(public_key.user_id),
            "created_at": public_key.created_at.isoformat(),
            "updated_at": public_key.updated_at.isoformat() if public_key.updated_at else None,
            "metadata": public_key.metadata,
            # We don't include the actual key data in the response for security
            "key_fingerprint": self._calculate_key_fingerprint(public_key.key_data)
        }
        
    def _calculate_key_fingerprint(self, key_data: str) -> str:
        """
        Calculate a fingerprint for a public key.
        
        Args:
            key_data: The public key data
            
        Returns:
            A fingerprint string
        """
        return hashlib.sha256(key_data.encode()).hexdigest()[:16] 