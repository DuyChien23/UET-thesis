"""
Database session management module.
Provides functions to create and manage SQLAlchemy async database sessions.
"""

import logging
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.pool import NullPool

from src.config.settings import get_settings

logger = logging.getLogger(__name__)

# Global engine and session factory
_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker] = None


def get_engine() -> AsyncEngine:
    """
    Get the SQLAlchemy engine instance.
    Creates a new one if it doesn't exist.
    
    Returns:
        AsyncEngine: The SQLAlchemy engine
    """
    global _engine
    
    if _engine is None:
        settings = get_settings()
        
        if settings.mock_services:
            logger.info("Creating in-memory SQLite database engine for mock mode")
            _engine = create_async_engine(
                "sqlite+aiosqlite:///:memory:",
                echo=settings.debug,
                future=True,
            )
        else:
            logger.info(f"Creating database engine with URL: {settings.database_url}")
            _engine = create_async_engine(
                settings.database_url,
                echo=settings.debug,
                future=True,
                poolclass=NullPool if settings.debug else None,
            )
    
    return _engine


def get_session_factory() -> async_sessionmaker:
    """
    Get the SQLAlchemy session factory.
    Creates a new one if it doesn't exist.
    
    Returns:
        async_sessionmaker: The SQLAlchemy session factory
    """
    global _session_factory
    
    if _session_factory is None:
        engine = get_engine()
        
        logger.info("Creating database session factory")
        
        _session_factory = async_sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
    
    return _session_factory


async def get_db_session() -> AsyncSession:
    """
    Get a new database session.
    
    Returns:
        AsyncSession: A new database session
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        logger.debug("Created new database session")
        return session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that yields a database session.
    For use with FastAPI's dependency injection system.
    
    Yields:
        AsyncSession: A database session
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            logger.debug("Database session opened")
            yield session
        finally:
            logger.debug("Database session closed")


async def close_db_connection() -> None:
    """
    Close the database connection.
    """
    global _engine
    
    if _engine is not None:
        logger.info("Closing database connection")
        await _engine.dispose()
        _engine = None
        logger.info("Database connection closed") 