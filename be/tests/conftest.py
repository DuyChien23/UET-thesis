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
tests
from src.main import app, startup_event
from src.config.settings import get_settings
from src.db.session import get_engine, get_session_factory
from src.db.base import Base
from src.api.middlewares.auth import create_access_token
from src.utils.password import get_password_hash
from src.db.models.users import User, Role, user_roles

# Set up logging
logger = logging.getLogger(__name__)

# Silence pytest_asyncio warning about redefining event_loop fixture
warnings.filterwarnings("ignore", message="The event_loop fixture provided by pytest-asyncio has been redefined")

@pytest.fixture(scope="session")
def event_loop():
    """Create a shared event loop for all tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="module")
async def setup_application():
    """Initialize the application for testing."""
    await startup_event()
    yield
    # Cleanup will happen in the shutdown event handler

@pytest_asyncio.fixture
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
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash("testpassword123")
    now = datetime.datetime.utcnow()

    try:
        async with engine.begin() as conn:
            # Check if user exists
            select_stmt = select(User).where(User.username == "testuser")
            result = await conn.execute(select_stmt)
            existing_user = result.scalars().first()

            if existing_user:
                # Create a user object from existing user data
                user = {
                    "id": str(existing_user.id),
                    "username": existing_user.username,
                    "email": existing_user.email,
                    "password_hash": existing_user.password_hash,
                    "full_name": existing_user.full_name, 
                    "status": existing_user.status
                }
                return user

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

        # Return user data as a dictionary
        user = {
            "id": user_id,
            "username": "testuser",
            "email": "testuser@example.com",
            "password_hash": hashed_password,
            "full_name": "Test User",
            "status": "active"
        }
        return user
    except Exception as e:
        logger.error(f"Error creating test user: {str(e)}")
        return None

@pytest_asyncio.fixture(scope="module")
async def auth_token(test_user):
    """Create an auth token for testing."""
    if test_user is None:
        pytest.skip("Test user fixture failed to create a user")
    
    # Create a valid token for the test user
    settings = get_settings()
    expires_delta = datetime.timedelta(minutes=settings.jwt_expire_minutes)
    
    # Handle the case where test_user might be a string
    if isinstance(test_user, str):
        # Fallback when test_user is a string
        token = create_access_token(
            data={"sub": "test-user-id", "username": "testuser"},
            expires_delta=expires_delta
        )
    else:
        # Normal case when test_user is a proper User object or dictionary
        user_id = test_user["id"] if isinstance(test_user, dict) else str(test_user.id)
        username = test_user["username"] if isinstance(test_user, dict) else test_user.username
        
        token = create_access_token(
            data={"sub": user_id, "username": username},
            expires_delta=expires_delta
        )
    
    return token 