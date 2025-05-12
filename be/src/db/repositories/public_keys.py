"""
Repository for public keys.
"""

import uuid
from typing import List, Optional, Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.public_keys import PublicKey
from db.repositories.base import BaseRepository


class PublicKeyRepository(BaseRepository[PublicKey]):
    """
    Repository for public key operations.
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize the repository.
        
        Args:
            db_session (AsyncSession): The database session
        """
        super().__init__(PublicKey)
        self.db = db_session
    
    async def create(
        self,
        key_data: str,
        algorithm_name: str,
        user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        curve_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PublicKey:
        """
        Create a new public key.
        
        Args:
            key_data (str): The public key data
            algorithm_name (str): The algorithm name
            user_id (str): The ID of the user who owns the key
            name (Optional[str]): A name for the key
            description (Optional[str]): A description for the key
            curve_name (Optional[str]): The curve name for ECC algorithms
            metadata (Optional[Dict[str, Any]]): Additional metadata
            
        Returns:
            PublicKey: The created public key
        """
        public_key_data = {
            "key_data": key_data,
            "algorithm_name": algorithm_name,
            "user_id": uuid.UUID(user_id),
            "name": name,
            "description": description,
            "curve_name": curve_name,
            "metadata": metadata or {}
        }
        
        return await super().create(self.db, public_key_data)
    
    async def get_by_id(self, key_id: str) -> Optional[PublicKey]:
        """
        Get a public key by ID.
        
        Args:
            key_id (str): The public key ID
            
        Returns:
            Optional[PublicKey]: The public key if found, None otherwise
        """
        return await super().get(self.db, uuid.UUID(key_id))
    
    async def get_by_user_id(
        self, 
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[PublicKey]:
        """
        Get public keys for a user.
        
        Args:
            user_id (str): The user ID
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            List[PublicKey]: List of public keys
        """
        query = (
            select(PublicKey)
            .where(PublicKey.user_id == uuid.UUID(user_id))
            .order_by(PublicKey.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_by_algorithm(
        self, 
        algorithm_name: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[PublicKey]:
        """
        Get public keys for a specific algorithm.
        
        Args:
            algorithm_name (str): The algorithm name
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            List[PublicKey]: List of public keys
        """
        query = (
            select(PublicKey)
            .where(PublicKey.algorithm_name == algorithm_name)
            .order_by(PublicKey.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_by_curve(
        self, 
        curve_name: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[PublicKey]:
        """
        Get public keys for a specific curve.
        
        Args:
            curve_name (str): The curve name
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            List[PublicKey]: List of public keys
        """
        query = (
            select(PublicKey)
            .where(PublicKey.curve_name == curve_name)
            .order_by(PublicKey.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def delete(self, key_id: str) -> bool:
        """
        Delete a public key.
        
        Args:
            key_id (str): The public key ID
            
        Returns:
            bool: True if the key was deleted, False otherwise
        """
        return await super().delete(self.db, uuid.UUID(key_id)) 