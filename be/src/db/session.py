"""
Database session management module.
Provides functions to create and manage SQLAlchemy async database sessions.
"""

import logging
import os
import socket
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
            # Create a database directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            logger.info("Creating file-based SQLite database engine for mock mode")
            _engine = create_async_engine(
                "sqlite+aiosqlite:///data/test.db",
                echo=settings.debug,
                future=True,
            )
        else:
            # Determine if running in Docker or locally
            database_url = settings.database_url
            
            # If the host is 'postgres', check if we're running outside of Docker
            if 'postgres:5432' in database_url:
                # Check if the 'postgres' hostname is not accessible (running locally)
                try:
                    socket.gethostbyname('postgres')
                    logger.info("Running inside Docker network, using 'postgres' as host")
                except socket.gaierror:
                    logger.info("Running locally, replacing 'postgres' with 'localhost' in database URL")
                    database_url = database_url.replace('postgres:5432', 'localhost:5432')
            
            logger.info(f"Creating database engine with URL: {database_url}")
            _engine = create_async_engine(
                database_url,
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