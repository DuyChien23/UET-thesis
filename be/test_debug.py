"""
Debug script for auth API.
"""
import os
import asyncio
import logging
import json
import uuid
import datetime
from sqlalchemy import insert

from src.db.session import get_engine, get_db_session
from src.db.base import Base
from src.db.models.users import Role, User, user_roles
from src.utils.password import get_password_hash
from src.db.repositories.users import UserRepository
from src.api.routes import auth

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def setup_database():
    """Set up a test database with required data."""
    # Use a test database
    os.environ["TESTING"] = "1"
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_debug.db"
    
    # Get the engine
    engine = get_engine()
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Create a role
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
    
    logger.info("Database setup complete")
    return engine

async def test_user_registration():
    """Test user registration directly."""
    # Set up database
    engine = await setup_database()
    
    # Get a database session
    session = await get_db_session()
    
    # Create a user repository
    user_repo = UserRepository(session)
    
    # User data
    username = "testuser"
    email = "testuser@example.com"
    password = "testpassword123"
    full_name = "Test User"
    
    # Create the user directly
    try:
        logger.info("Creating user")
        
        # Hash the password
        hashed_password = get_password_hash(password)
        
        # Create the user
        user = await user_repo.create(session, obj_in={
            "username": username,
            "email": email, 
            "password_hash": hashed_password,
            "full_name": full_name,
            "status": "active"
        })
        
        logger.info(f"User created: {user.id}")
        
        # Add default role
        default_role = await user_repo.get_role_by_name("user")
        if default_role:
            await user_repo.add_role_to_user(user.id, default_role.id)
            logger.info("Added 'user' role")
        else:
            logger.error("User role not found")
            
        # Get user with roles
        user_with_roles = await user_repo.get_user_with_roles(user.id)
        
        # Format the response
        logger.info(f"User with roles: {user_with_roles}")
        logger.info(f"Roles: {[role.name for role in user_with_roles.roles if user_with_roles.roles]}")
        
        logger.info("Test completed successfully")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(test_user_registration()) 