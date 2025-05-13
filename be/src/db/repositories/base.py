from typing import Generic, TypeVar, Type, Optional, List, Dict, Any, Union
import uuid
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from ..base import Base

# Define a TypeVar for the model
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository with common CRUD operations
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Initialize the repository with a model.
        
        Args:
            model (Type[ModelType]): The SQLAlchemy model to use
        """
        self.model = model
    
    async def create(self, db: AsyncSession, obj_in: Dict[str, Any]) -> ModelType:
        """
        Create a new record.
        
        Args:
            db (AsyncSession): Database session
            obj_in (Dict[str, Any]): Data to create the record
            
        Returns:
            ModelType: The created record
        """
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        try:
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except Exception as e:
            await db.rollback()
            raise e
    
    async def get(self, db: AsyncSession, id: uuid.UUID) -> Optional[ModelType]:
        """
        Get a record by ID.
        
        Args:
            db (AsyncSession): Database session
            id (uuid.UUID): Record ID
            
        Returns:
            Optional[ModelType]: The record if found, None otherwise
        """
        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_multi(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and filtering.
        
        Args:
            db (AsyncSession): Database session
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            filters (Optional[Dict[str, Any]]): Filters to apply
            
        Returns:
            List[ModelType]: List of records
        """
        query = select(self.model).offset(skip).limit(limit)
        
        # Apply filters if provided
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        id: uuid.UUID, 
        obj_in: Dict[str, Any]
    ) -> Optional[ModelType]:
        """
        Update a record.
        
        Args:
            db (AsyncSession): Database session
            id (uuid.UUID): Record ID
            obj_in (Dict[str, Any]): Data to update the record
            
        Returns:
            Optional[ModelType]: The updated record if found, None otherwise
        """
        # Get the record to update
        db_obj = await self.get(db, id)
        if not db_obj:
            return None
        
        # Update the attributes
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(self, db: AsyncSession, id: uuid.UUID) -> bool:
        """
        Delete a record.
        
        Args:
            db (AsyncSession): Database session
            id (uuid.UUID): Record ID
            
        Returns:
            bool: True if the record was deleted, False otherwise
        """
        db_obj = await self.get(db, id)
        if not db_obj:
            return False
        
        await db.delete(db_obj)
        await db.commit()
        return True
    
    async def count(
        self, 
        db: AsyncSession, 
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count records.
        
        Args:
            db (AsyncSession): Database session
            filters (Optional[Dict[str, Any]]): Filters to apply
            
        Returns:
            int: Number of records
        """
        query = select(self.model)
        
        # Apply filters if provided
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
        
        result = await db.execute(select(db.func.count()).select_from(query.subquery()))
        return result.scalar_one()
    
    def build_query(self) -> Select:
        """
        Build a base SELECT query for this model.
        
        Returns:
            Select: Base SELECT query
        """
        return select(self.model) 