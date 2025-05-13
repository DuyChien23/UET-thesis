"""
Test configuration utilities.
"""
import uuid
import datetime
import logging
import asyncio
from sqlalchemy import insert, select

from src.db.session import get_engine
from src.db.base import Base
from src.db.models.users import Role, User
from src.db.models.algorithms import Algorithm, Curve
from src.utils.password import get_password_hash
from src.services.algorithms import AlgorithmService
from src.services import set_algorithm_service

logger = logging.getLogger(__name__)

async def setup_test_db():
    """Set up the test database with required data."""
    # Get the engine
    engine = get_engine()
    
    logger.info("Setting up test database")
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed test data
    await seed_test_data(engine)
    
    # Initialize services
    await init_test_services(engine)
    
    logger.info("Test database setup complete")

async def seed_test_data(engine):
    """Seed test data into the database."""
    logger.info("Seeding test data")
    
    async with engine.begin() as conn:
        now = datetime.datetime.utcnow()
        
        # Create user role
        user_role_id = str(uuid.uuid4())
        role_stmt = insert(Role).values(
            id=user_role_id,
            name="user",
            description="Regular user",
            created_at=now,
            updated_at=now
        )
        await conn.execute(role_stmt)
        logger.info("Created 'user' role")
        
        # Create admin role
        admin_role_id = str(uuid.uuid4())
        admin_role_stmt = insert(Role).values(
            id=admin_role_id,
            name="admin",
            description="Administrator",
            created_at=now,
            updated_at=now
        )
        await conn.execute(admin_role_stmt)
        
        # Create test algorithms
        ecdsa_id = str(uuid.uuid4())
        ecdsa_stmt = insert(Algorithm).values(
            id=ecdsa_id,
            name="ECDSA",
            type="asymmetric",
            description="Elliptic Curve Digital Signature Algorithm",
            is_default=True,
            status="enabled",
            created_at=now,
            updated_at=now
        )
        await conn.execute(ecdsa_stmt)
        
        # Add secp256k1 curve for ECDSA
        secp256k1_id = str(uuid.uuid4())
        secp256k1_stmt = insert(Curve).values(
            id=secp256k1_id,
            name="secp256k1",
            algorithm_id=ecdsa_id,
            description="SECP256k1 curve (used in Bitcoin)",
            parameters={"bit_size": 256, "hash_algorithm": "SHA256"},
            is_default=True,
            status="enabled",
            created_at=now,
            updated_at=now
        )
        await conn.execute(secp256k1_stmt)
        
        # Add RSA algorithm
        rsa_id = str(uuid.uuid4())
        rsa_stmt = insert(Algorithm).values(
            id=rsa_id,
            name="RSA-SHA256",
            type="asymmetric",
            description="RSA with SHA-256",
            is_default=False,
            status="enabled",
            created_at=now,
            updated_at=now
        )
        await conn.execute(rsa_stmt)
        
        logger.info("Created algorithms and curves")

async def init_test_services(engine):
    """Initialize services for testing."""
    # Create and set algorithm service
    async with engine.begin() as conn:
        # Initialize algorithm service
        algorithm_service = AlgorithmService()
        await algorithm_service.load_algorithms()
        
        # Register the algorithm service globally
        set_algorithm_service(algorithm_service)
        
        logger.info("Initialized services for testing")

async def cleanup_test_db():
    """Clean up the test database."""
    logger.info("Cleaning up test database")
    
    # Get the engine
    engine = get_engine()
    
    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    logger.info("Test database cleanup complete") 