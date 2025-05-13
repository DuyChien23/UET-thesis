import os
import asyncio
import logging
import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient
import uuid

from src.main import app
from src.config.settings import get_settings
from src.db.session import get_engine, get_db_session
from src.db.base import Base
from src.api.middlewares.auth import create_access_token
from src.utils.password import get_password_hash
from src.db.repositories.users import UserRepository

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("pytest_fixtures")


@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_app():
    """Create a FastAPI test application."""
    # Use a test database
    os.environ["TESTING"] = "1"
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
    
    logger.debug("Setting up test app with test database")
    return app


@pytest_asyncio.fixture
async def async_client(test_app):
    """Create an async test client."""
    logger.debug("Creating async client for testing")
    base_url = "http://test"
    
    # Use AsyncClient for async tests
    async with AsyncClient(app=test_app, base_url=base_url) as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def init_test_db():
    """Initialize test database."""
    logger.debug("Initializing test database")
    
    # Get the engine
    engine = get_engine()
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    logger.debug("Test database initialized")
    yield
    
    # Clean up
    logger.debug("Cleaning up test database")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def test_user(init_test_db):
    """Create a test user."""
    logger.debug("Creating test user")
    session = await get_db_session()
    user_repo = UserRepository(session)
    
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash("testpassword123")
    
    try:
        # First create role
        logger.debug("Creating test role")
        role = await user_repo.create_role(session, obj_in={
            "name": "user", 
            "description": "Regular user"
        })
        logger.debug(f"Created role with ID: {role.id}")
        
        # Create the test user
        user = await user_repo.create(session, obj_in={
            "id": user_id,
            "username": "testuser",
            "email": "testuser@example.com",
            "password_hash": hashed_password,
            "full_name": "Test User",
            "status": "active",
            "is_active": True,
            "is_superuser": False
        })
        
        # Add role to user
        logger.debug(f"Adding role {role.id} to user {user.id}")
        await user_repo.add_role_to_user(user.id, role.id)
        
        # Verify the role was added
        user_with_roles = await user_repo.get_user_with_roles(user.id)
        logger.debug(f"User roles: {[r.name for r in user_with_roles.roles]}")
        
        logger.debug(f"Test user created with ID: {user.id}")
        yield user_with_roles
    except Exception as e:
        logger.error(f"Error creating test user: {str(e)}")
        raise


@pytest.fixture
def auth_token(test_user):
    """Create authentication token for the test user."""
    logger.debug(f"Creating auth token for user: {test_user.id}")
    settings = get_settings()
    token = create_access_token(
        data={"sub": str(test_user.id)}, 
        expires_delta=None
    )
    return token 