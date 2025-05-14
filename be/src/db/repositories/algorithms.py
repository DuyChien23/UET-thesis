"""
Algorithm repository module.
Provides data access layer for algorithm and curve models.
"""

from typing import List, Optional, Dict, Any
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..base import UUID
from ..models.algorithms import Algorithm, Curve
from .base import BaseRepository


class AlgorithmRepository(BaseRepository[Algorithm]):
    """
    Repository for algorithm operations.
    """
    
    def __init__(self):
        """Initialize the algorithm repository."""
        super().__init__(Algorithm)
        
    async def get_by_id(self, db: AsyncSession, algorithm_id: str) -> Optional[Algorithm]:
        """
        Get an algorithm by ID.
        
        Args:
            db (AsyncSession): Database session
            algorithm_id (str): Algorithm ID
            
        Returns:
            Optional[Algorithm]: Algorithm if found, None otherwise
        """
        query = select(self.model).where(self.model.id == algorithm_id)
        result = await db.execute(query)
        return result.scalars().first()
        
    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Algorithm]:
        """
        Get an algorithm by name.
        
        Args:
            db (AsyncSession): Database session
            name (str): Algorithm name
            
        Returns:
            Optional[Algorithm]: Algorithm if found, None otherwise
        """
        query = select(self.model).where(self.model.name == name)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_with_curves(self, db: AsyncSession, algorithm_id: UUID) -> Optional[Algorithm]:
        """
        Get an algorithm with its curves.
        
        Args:
            db (AsyncSession): Database session
            algorithm_id (UUID): Algorithm ID
            
        Returns:
            Optional[Algorithm]: Algorithm with curves if found, None otherwise
        """
        query = select(self.model).where(self.model.id == algorithm_id)
        result = await db.execute(query)
        algorithm = result.scalars().first()
        
        if algorithm:
            # Load curves explicitly
            await db.refresh(algorithm, ["curves"])
        
        return algorithm


class CurveRepository(BaseRepository[Curve]):
    """
    Repository for curve operations.
    """
    
    def __init__(self):
        """Initialize the curve repository."""
        super().__init__(Curve)
        
    async def get_by_id(self, db: AsyncSession, curve_id: str) -> Optional[Curve]:
        """
        Get a curve by ID.
        
        Args:
            db (AsyncSession): Database session
            curve_id (str): Curve ID
            
        Returns:
            Optional[Curve]: Curve if found, None otherwise
        """
        query = select(self.model).where(self.model.id == curve_id)
        result = await db.execute(query)
        return result.scalars().first()
        
    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Curve]:
        """
        Get a curve by name.
        
        Args:
            db (AsyncSession): Database session
            name (str): Curve name
            
        Returns:
            Optional[Curve]: Curve if found, None otherwise
        """
        query = select(self.model).where(self.model.name == name)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_by_algorithm_id(self, 
                                db: AsyncSession, 
                                algorithm_id: UUID,
                                enabled_only: bool = True) -> List[Curve]:
        """
        Get all curves for an algorithm.
        
        Args:
            db (AsyncSession): Database session
            algorithm_id (UUID): Algorithm ID
            enabled_only (bool): If True, only return enabled curves
            
        Returns:
            List[Curve]: List of curves
        """
        query = select(self.model).where(self.model.algorithm_id == algorithm_id)
        
        if enabled_only:
            query = query.where(self.model.status == "enabled")
            
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_all_with_filters(self, 
                                  db: AsyncSession, 
                                  algorithm_id: Optional[UUID] = None, 
                                  status: Optional[str] = None) -> List[Curve]:
        """
        Get all curves with optional filters.
        
        Args:
            db (AsyncSession): Database session
            algorithm_id (Optional[UUID]): Filter by algorithm ID
            status (Optional[str]): Filter by status (enabled/disabled)
            
        Returns:
            List[Curve]: List of curves matching the filters
        """
        query = select(self.model)
        
        # Apply filters
        if algorithm_id is not None:
            query = query.where(self.model.algorithm_id == algorithm_id)
            
        if status is not None:
            query = query.where(self.model.status == status)
            
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_default_for_algorithm(self, 
                                       db: AsyncSession, 
                                       algorithm_id: UUID) -> Optional[Curve]:
        """
        Get default curve for an algorithm.
        
        Args:
            db (AsyncSession): Database session
            algorithm_id (UUID): Algorithm ID
            
        Returns:
            Optional[Curve]: Default curve if found, None otherwise
        """
        # Get all enabled curves for the algorithm
        curves = await self.get_by_algorithm_id(db, algorithm_id)
        
        # If no curves, return None
        if not curves:
            return None
            
        # Find curve with "default" in parameters or return first curve
        for curve in curves:
            if curve.parameters.get("is_default", False):
                return curve
                
        # If no default curve found, return first one
        return curves[0] 