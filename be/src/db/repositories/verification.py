"""
Repository for verification records.
"""

import uuid
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload, joinedload

from src.db.models.verification import VerificationRecord, VerificationStatus, BatchVerification, BatchVerificationItem
from src.db.repositories.base import BaseRepository


class VerificationRepository(BaseRepository[VerificationRecord]):
    """
    Repository for verification record operations.
    """
    
    def __init__(self, session_factory: async_sessionmaker):
        """
        Initialize the repository.
        
        Args:
            session_factory (async_sessionmaker): The database session factory
        """
        super().__init__(VerificationRecord)
        self.session_factory = session_factory
    
    async def create(
        self,
        public_key_id: str,
        document_hash: str,
        signature: str,
        algorithm_name: str,
        status: VerificationStatus,
        verified_at: datetime,
        user_id: Optional[str] = None,
        document_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> VerificationRecord:
        """
        Create a new verification record.
        
        Args:
            public_key_id (str): ID of the public key used
            document_hash (str): Hash of the document
            signature (str): Signature that was verified
            algorithm_name (str): Name of the algorithm used
            status (VerificationStatus): Verification status
            verified_at (datetime): Timestamp of verification
            user_id (Optional[str]): ID of the user who performed the verification
            document_id (Optional[str]): ID of the document
            metadata (Optional[Dict[str, Any]]): Additional metadata
            
        Returns:
            VerificationRecord: The created verification record
        """
        verification_data = {
            "public_key_id": uuid.UUID(public_key_id),
            "document_hash": document_hash,
            "signature": signature,
            "algorithm_name": algorithm_name,
            "status": status,
            "verified_at": verified_at,
            "verification_metadata": metadata or {}
        }
        
        if user_id:
            verification_data["user_id"] = uuid.UUID(user_id)
            
        if document_id:
            verification_data["document_id"] = document_id
        
        async with self.session_factory() as session:
            return await super().create(session, verification_data)
    
    async def get_by_id(self, verification_id: str) -> Optional[VerificationRecord]:
        """
        Get a verification record by ID.
        
        Args:
            verification_id (str): The verification record ID
            
        Returns:
            Optional[VerificationRecord]: The verification record if found, None otherwise
        """
        async with self.session_factory() as session:
            return await super().get(session, uuid.UUID(verification_id))
    
    async def get_by_user_id(
        self, 
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[VerificationRecord]:
        """
        Get verification records for a user.
        
        Args:
            user_id (str): The user ID
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            List[VerificationRecord]: List of verification records
        """
        query = (
            select(VerificationRecord)
            .where(VerificationRecord.user_id == uuid.UUID(user_id))
            .order_by(VerificationRecord.verified_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        async with self.session_factory() as session:
            result = await session.execute(query)
            return result.scalars().all()
    
    async def get_by_public_key_id(
        self, 
        public_key_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[VerificationRecord]:
        """
        Get verification records for a public key.
        
        Args:
            public_key_id (str): The public key ID
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            List[VerificationRecord]: List of verification records
        """
        query = (
            select(VerificationRecord)
            .where(VerificationRecord.public_key_id == uuid.UUID(public_key_id))
            .order_by(VerificationRecord.verified_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        async with self.session_factory() as session:
            result = await session.execute(query)
            return result.scalars().all()
    
    async def get_by_document_id(
        self, 
        document_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[VerificationRecord]:
        """
        Get verification records for a document.
        
        Args:
            document_id (str): The document ID
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            List[VerificationRecord]: List of verification records
        """
        query = (
            select(VerificationRecord)
            .where(VerificationRecord.document_id == document_id)
            .order_by(VerificationRecord.verified_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        async with self.session_factory() as session:
            result = await session.execute(query)
            return result.scalars().all()
    
    async def get_by_document_hash(
        self, 
        document_hash: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[VerificationRecord]:
        """
        Get verification records for a document hash.
        
        Args:
            document_hash (str): The document hash
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            List[VerificationRecord]: List of verification records
        """
        query = (
            select(VerificationRecord)
            .where(VerificationRecord.document_hash == document_hash)
            .order_by(VerificationRecord.verified_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        async with self.session_factory() as session:
            result = await session.execute(query)
            return result.scalars().all()
    
    async def get_filtered_records(
        self,
        filters: Dict[str, Any],
        limit: int = 20,
        offset: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        order_by: str = "verified_at",
        order_desc: bool = True
    ) -> List[VerificationRecord]:
        """
        Get verification records with filters.
        
        Args:
            filters (Dict[str, Any]): Filters to apply
            limit (int): Maximum number of records to return
            offset (int): Number of records to skip
            start_date (Optional[datetime]): Filter by verified_at (start date)
            end_date (Optional[datetime]): Filter by verified_at (end date)
            order_by (str): Field to order by
            order_desc (bool): Whether to order in descending order
            
        Returns:
            List[VerificationRecord]: List of verification records
        """
        conditions = []
        
        # Process standard filters
        for key, value in filters.items():
            if hasattr(VerificationRecord, key):
                if key == "user_id" and isinstance(value, str):
                    value = uuid.UUID(value)
                conditions.append(getattr(VerificationRecord, key) == value)
        
        # Process date range filter
        if start_date:
            conditions.append(VerificationRecord.verified_at >= start_date)
        if end_date:
            conditions.append(VerificationRecord.verified_at <= end_date)
        
        # Build the query
        query = select(VerificationRecord)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Apply ordering
        if hasattr(VerificationRecord, order_by):
            order_attr = getattr(VerificationRecord, order_by)
            if order_desc:
                query = query.order_by(desc(order_attr))
            else:
                query = query.order_by(order_attr)
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        # Execute the query
        async with self.session_factory() as session:
            result = await session.execute(query)
            return result.scalars().all()
    
    async def count(
        self,
        filters: Dict[str, Any],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """
        Count verification records with filters.
        
        Args:
            filters (Dict[str, Any]): Filters to apply
            start_date (Optional[datetime]): Filter by verified_at (start date)
            end_date (Optional[datetime]): Filter by verified_at (end date)
            
        Returns:
            int: Count of verification records
        """
        conditions = []
        
        # Process standard filters
        for key, value in filters.items():
            if hasattr(VerificationRecord, key):
                if key == "user_id" and isinstance(value, str):
                    value = uuid.UUID(value)
                conditions.append(getattr(VerificationRecord, key) == value)
        
        # Process date range filter
        if start_date:
            conditions.append(VerificationRecord.verified_at >= start_date)
        if end_date:
            conditions.append(VerificationRecord.verified_at <= end_date)
        
        # Build the query
        query = select(func.count()).select_from(VerificationRecord)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Execute the query
        async with self.session_factory() as session:
            result = await session.execute(query)
            return result.scalar() or 0 