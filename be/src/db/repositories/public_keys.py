"""
Repository for public keys.
"""

import uuid
from typing import List, Optional, Dict, Any

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from src.db.models.public_keys import PublicKey
from src.db.repositories.base import BaseRepository


class PublicKeyRepository(BaseRepository[PublicKey]):
    """
    Repository for public key operations.
    """
    
    def __init__(self, session_factory: async_sessionmaker):
        """
        Initialize the repository.
        
        Args:
            session_factory (async_sessionmaker): The database session factory
        """
        super().__init__(PublicKey)
        self.session_factory = session_factory
    
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
            "key_metadata": metadata or {}
        }
        
        async with self.session_factory() as session:
            return await super().create(session, public_key_data)
    
    async def get_by_id(self, key_id: str) -> Optional[PublicKey]:
        """
        Get a public key by ID.
        
        Args:
            key_id (str): The public key ID
            
        Returns:
            Optional[PublicKey]: The public key if found, None otherwise
        """
        async with self.session_factory() as session:
            return await super().get(session, uuid.UUID(key_id))
    
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
        
        async with self.session_factory() as session:
            result = await session.execute(query)
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
        
        async with self.session_factory() as session:
            result = await session.execute(query)
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
        
        async with self.session_factory() as session:
            result = await session.execute(query)
            return result.scalars().all()
    
    async def delete(self, key_id: str) -> bool:
        """
        Delete a public key.
        
        Args:
            key_id (str): The public key ID
            
        Returns:
            bool: True if the key was deleted, False otherwise
        """
        async with self.session_factory() as session:
            return await super().delete(session, uuid.UUID(key_id))
    
    async def get_user_keys(
        self, 
        user_id: uuid.UUID, 
        algorithm_name: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PublicKey]:
        """
        Get public keys for a specific user.
        
        Args:
            user_id (uuid.UUID): User ID to get keys for
            algorithm_name (Optional[str]): Filter by algorithm name
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            List[PublicKey]: List of public keys for the user
        """
        # Base query for user's keys
        query = select(PublicKey).where(PublicKey.user_id == user_id)
        
        # Add algorithm filter if provided
        if algorithm_name:
            query = query.where(PublicKey.algorithm_name == algorithm_name)
        
        # Add pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        async with self.session_factory() as session:
            result = await session.execute(query)
            return result.scalars().all()
    
    async def get_by_fingerprint(self, fingerprint: str) -> Optional[PublicKey]:
        """
        Get a public key by its fingerprint.
        
        Args:
            fingerprint (str): Key fingerprint
            
        Returns:
            Optional[PublicKey]: The public key if found, None otherwise
        """
        query = select(PublicKey).where(PublicKey.fingerprint == fingerprint)
        
        async with self.session_factory() as session:
            result = await session.execute(query)
            return result.scalars().first()
    
    async def search_keys(
        self,
        user_id: Optional[uuid.UUID] = None,
        algorithm_name: Optional[str] = None,
        curve_name: Optional[str] = None,
        name_contains: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PublicKey]:
        """
        Search for public keys with various filters.
        
        Args:
            user_id (Optional[uuid.UUID]): Filter by user ID
            algorithm_name (Optional[str]): Filter by algorithm name
            curve_name (Optional[str]): Filter by curve name
            name_contains (Optional[str]): Filter by key name containing this string
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            List[PublicKey]: List of matching public keys
        """
        # Start with base query
        query = select(PublicKey)
        
        # Apply filters
        filters = []
        
        if user_id:
            filters.append(PublicKey.user_id == user_id)
        
        if algorithm_name:
            filters.append(PublicKey.algorithm_name == algorithm_name)
            
        if curve_name:
            filters.append(PublicKey.curve_name == curve_name)
            
        if name_contains:
            filters.append(PublicKey.name.ilike(f"%{name_contains}%"))
            
        if filters:
            query = query.where(and_(*filters))
            
        # Add pagination
        query = query.order_by(PublicKey.created_at.desc()).offset(skip).limit(limit)
        
        # Execute query
        async with self.session_factory() as session:
            result = await session.execute(query)
            return result.scalars().all() 