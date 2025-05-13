import os
import asyncio
import logging
import pytest
import pytest_asyncio
import warnings
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient
import uuid
import datetime
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app, startup_event
from src.config.settings import get_settings
from src.db.session import get_engine, get_session_factory
from src.db.base import Base
from src.api.middlewares.auth import create_access_token
from src.utils.password import get_password_hash
from src.db.models.users import User, Role, user_roles

# Set up logging
logger = logging.getLogger(__name__)


@pytest_asyncio.fixture(scope="module")
async def setup_application():
    """Initialize the application for testing."""
    await startup_event()
    yield
    # Cleanup will happen in the shutdown event handler


@pytest_asyncio.fixture(scope="function")
async def async_client(setup_application):
    """Create an async client for testing."""
    logger.debug("Creating async client for testing")
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(scope="module")
async def test_user():
    """Create a test user for auth testing."""
    # Get a database engine
    engine = get_engine()
    
    # Create a user in the database
    user_id = uuid.uuid4()
    hashed_password = get_password_hash("testpassword123")
    now = datetime.datetime.utcnow()
    
    async with engine.begin() as conn:
        # Check if user exists
        select_stmt = select(User).where(User.username == "testuser")
        result = await conn.execute(select_stmt)
        existing_user = result.scalars().first()
        
        if existing_user:
            return existing_user
            
        # Create the user
        insert_stmt = insert(User).values(
            id=user_id,
            username="testuser",
            email="testuser@example.com",
            password_hash=hashed_password,
            full_name="Test User",
            status="active",
            created_at=now,
            updated_at=now
        )
        await conn.execute(insert_stmt)
        
        # Get role ID
        select_role = select(Role.id).where(Role.name == "user")
        role_result = await conn.execute(select_role)
        role_id = role_result.scalar_one_or_none()
        
        if role_id:
            # Create user-role relationship
            user_role_stmt = insert(user_roles).values(
                user_id=user_id,
                role_id=role_id
            )
            await conn.execute(user_role_stmt)
    
    # Fetch the user with SQLAlchemy
    async with engine.begin() as conn:
        user_stmt = select(User).where(User.id == user_id)
        result = await conn.execute(user_stmt)
        user = result.scalars().first()
        return user


@pytest_asyncio.fixture(scope="module")
async def auth_token(test_user):
    """Create an auth token for testing."""
    if test_user is None or isinstance(test_user, str):
        # Return a dummy token for tests that don't need a valid one
        return "dummy_token_for_tests"
        
    token = create_access_token(
        data={"sub": str(test_user.id), "username": test_user.username}
    )
    return token 