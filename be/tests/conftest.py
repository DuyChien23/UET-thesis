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

from src.main import app
from src.config.settings import get_settings
from src.db.session import get_engine, get_db_session
from src.db.base import Base
from src.api.middlewares.auth import create_access_token
from src.utils.password import get_password_hash
from src.db.models.users import User, Role, user_roles
from src.algorithms import initialize_algorithms
from src.services import init_services

# Filter out bcrypt warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="passlib.handlers.bcrypt")

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("pytest_fixtures")


@pytest.fixture(scope="session")
def test_app():
    """Create a FastAPI test application."""
    # Use a test database
    os.environ["TESTING"] = "1"
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
    
    logger.debug("Setting up test app with test database")
    
    # Initialize algorithms for testing
    initialize_algorithms()
    
    return app


@pytest_asyncio.fixture(scope="session")
async def initialize_test_services():
    """Initialize services for testing."""
    logger.debug("Initializing test services")
    
    # Get a session for services
    session = await get_db_session()
    
    # Initialize services
    await init_services(session)
    
    yield
    
    # Close the session
    await session.close()


@pytest_asyncio.fixture
async def async_client(test_app, initialize_test_services):
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
    """Create a test user directly using SQLAlchemy."""
    logger.debug("Creating test user using direct SQLAlchemy operations")
    
    # Get session
    engine = get_engine()
    async with engine.begin() as conn:
        # Create role
        role_id = str(uuid.uuid4())
        now = datetime.datetime.utcnow()
        
        role_stmt = insert(Role).values(
            id=role_id,
            name="user",
            description="Regular user",
            created_at=now,
            updated_at=now
        )
        await conn.execute(role_stmt)
        
        # Create user
        user_id = str(uuid.uuid4())
        user_stmt = insert(User).values(
            id=user_id,
            username="testuser",
            email="testuser@example.com",
            password_hash=get_password_hash("testpassword123"),
            full_name="Test User",
            status="active",
            is_superuser=False,
            created_at=now,
            updated_at=now
        )
        await conn.execute(user_stmt)
        
        # Create user-role relationship
        user_role_stmt = insert(user_roles).values(
            user_id=user_id,
            role_id=role_id
        )
        await conn.execute(user_role_stmt)
        
        # Get role from database for the association
        role_select = select(Role).where(Role.id == role_id)
        role_result = await conn.execute(role_select)
        role = role_result.fetchone()
        
        # Get user from database with all the fields needed
        user_select = select(User).where(User.id == user_id)
        user_result = await conn.execute(user_select)
        user = user_result.fetchone()
    
    # Create a simple user object with roles for the tests
    class UserWithRoles:
        def __init__(self, user, roles):
            self.id = user.id
            self.username = user.username
            self.email = user.email
            self.full_name = user.full_name
            self.status = user.status
            self.is_superuser = user.is_superuser
            self.created_at = user.created_at
            self.last_login = user.last_login
            self.roles = roles
    
    # Create role object
    role_obj = type('Role', (), {'id': role.id, 'name': role.name})
    
    user_with_roles = UserWithRoles(user, [role_obj])
    
    logger.debug(f"Test user created with ID: {user_with_roles.id}")
    
    yield user_with_roles


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