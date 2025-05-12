"""
Database base module.
Provides the base model class for SQLAlchemy models.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    Provides common columns and functionality.
    """
    
    # Use UUIDs as primary keys
    id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4, 
        index=True
    )
    
    # Timestamps for creation and updates
    created_at: Mapped[datetime] = Column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False
    )
    
    updated_at: Mapped[datetime] = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=True
    )
    
    # Table naming convention
    @declared_attr
    def __tablename__(cls) -> str:
        """
        Convert class name to snake_case for table name.
        
        Returns:
            str: The table name
        """
        # Convert camel case to snake case
        name = cls.__name__
        return ''.join(['_' + c.lower() if c.isupper() else c for c in name]).lstrip('_')
    
    def dict(self) -> dict[str, Any]:
        """
        Convert model instance to dictionary.
        
        Returns:
            dict[str, Any]: Dictionary of model attributes
        """
        result = {}
        for key in self.__mapper__.c.keys():
            value = getattr(self, key)
            
            # Convert UUID to string
            if isinstance(value, uuid.UUID):
                value = str(value)
            
            # Convert datetime to ISO format
            elif isinstance(value, datetime):
                value = value.isoformat()
                
            result[key] = value
        return result
        
    def __repr__(self) -> str:
        """
        String representation of the model instance.
        
        Returns:
            str: String representation
        """
        model_name = self.__class__.__name__
        id_str = str(self.id)
        return f"<{model_name} {id_str}>" 