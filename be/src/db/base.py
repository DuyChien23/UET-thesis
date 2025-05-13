"""
Database base module.
Provides the base model class for SQLAlchemy models.
"""

import uuid
import json
import importlib
import pkgutil
import inspect
from datetime import datetime
from typing import Any, List, Type

from sqlalchemy import Column, DateTime, String, TypeDecorator, JSON, Table
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.dialects.postgresql import JSONB as PostgresJSONB
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped
from src.config.settings import get_settings


# Custom UUID type that uses String for SQLite
class UUID(TypeDecorator):
    """Platform-independent UUID type.
    
    Uses PostgreSQL's UUID type when using PostgreSQL, but uses
    String for SQLite.
    """
    
    impl = String
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgresUUID())
        else:
            return dialect.type_descriptor(String(36))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            return value
    
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            return value


# Custom JSONB type that uses JSON for SQLite
class JSONB(TypeDecorator):
    """Platform-independent JSONB type.
    
    Uses PostgreSQL's JSONB type when using PostgreSQL, but uses
    JSON for SQLite.
    """
    
    impl = JSON
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgresJSONB())
        else:
            return dialect.type_descriptor(JSON())
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return value
    
    def process_result_value(self, value, dialect):
        if value is None:
            return {}
        return value


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    Provides common columns and functionality.
    """
    
    # Use UUIDs as primary keys
    id: Mapped[uuid.UUID] = Column(
        UUID, 
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


def load_all_models() -> None:
    """
    Dynamically import all models from the models directory.
    This ensures all models are loaded and registered with the Base.metadata.
    """
    import src.db.models
    
    # Walk through all modules in the models package
    for _, module_name, is_pkg in pkgutil.iter_modules(src.db.models.__path__, src.db.models.__name__ + '.'):
        if not is_pkg:
            importlib.import_module(module_name)


def get_all_models() -> List[Type[Base]]:
    """
    Get all SQLAlchemy model classes defined in the models directory.
    
    Returns:
        List[Type[Base]]: List of model classes
    """
    load_all_models()
    
    # Find all classes that inherit from Base
    models = []
    
    for module_info in pkgutil.iter_modules(['src/db/models'], 'src.db.models.'):
        module = importlib.import_module(module_info.name)
        
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            
            # Check if it's a class and inherits from Base
            if (
                inspect.isclass(attr) and 
                issubclass(attr, Base) and 
                attr != Base and
                not attr.__name__.startswith('_')
            ):
                models.append(attr)
    
    return models


def get_all_tables() -> List[Table]:
    """
    Get all SQLAlchemy tables defined in the models directory.
    
    Returns:
        List[Table]: List of SQLAlchemy tables
    """
    load_all_models()
    return [table for table in Base.metadata.tables.values()] 