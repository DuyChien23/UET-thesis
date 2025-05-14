"""
CLI utility module for the application.
Provides command-line tools for database operations and other tasks.
"""

import logging
import asyncio
import argparse
import sys
import importlib.util
import os
import glob
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncEngine

from src.db.base import Base, get_all_models, load_all_models
from src.db.session import get_engine, close_db_connection
from src.config.logging import setup_logging
from src.config.settings import get_settings

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


async def create_tables(drop_first: bool = False, 
                        specific_tables: Optional[List[str]] = None) -> None:
    """
    Create database tables based on SQLAlchemy models.
    
    Args:
        drop_first: Whether to drop existing tables before creating new ones
        specific_tables: List of specific table names to create/drop (if None, all tables are processed)
    """
    logger.info("Loading all models")
    load_all_models()
    
    # Get all models
    models = get_all_models()
    logger.info(f"Found {len(models)} models: " + ", ".join([m.__name__ for m in models]))
    
    # Get database engine
    engine: AsyncEngine = get_engine()
    
    # Filter tables if specific ones were requested
    if specific_tables:
        filtered_tables = []
        for table_name in specific_tables:
            # Look up the table in Base.metadata
            if table_name in Base.metadata.tables:
                filtered_tables.append(Base.metadata.tables[table_name])
            else:
                logger.warning(f"Table {table_name} not found in models")
        tables = filtered_tables
        logger.info(f"Processing {len(tables)} specific tables: {', '.join(specific_tables)}")
    else:
        tables = Base.metadata.tables.values()
        logger.info(f"Processing all {len(Base.metadata.tables)} tables")
    
    async with engine.begin() as conn:
        if drop_first:
            logger.info("Dropping existing tables")
            await conn.run_sync(lambda sync_conn: Base.metadata.drop_all(
                sync_conn, 
                tables=tables
            ))
        
        logger.info("Creating tables")
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(
            sync_conn,
            tables=tables
        ))
    
    logger.info("Table creation completed successfully")
    await close_db_connection()


async def seed_data() -> None:
    """
    Seed the database with initial data including algorithms, curves, roles, admin user
    and sample data for testing.
    """
    logger.info("Starting data seeding process")
    
    # Directly use the seed_database function from utils
    from src.db.utils import seed_database
    
    try:
        logger.info("Starting to seed the database with algorithms, curves, and admin user")
        
        # Create a session for the seed operation
        from sqlalchemy.orm import Session
        from sqlalchemy import create_engine
        from src.config.settings import get_settings
        
        settings = get_settings()
        sync_engine = create_engine(settings.database_url.replace("+asyncpg", ""))
        with Session(sync_engine) as session:
            # Use the seed_database function to populate the database
            seed_database(session)
        
        logger.info("Database seeded successfully with algorithms, curves, and admin user")
    except Exception as e:
        logger.error(f"Error seeding data: {e}")
        raise
    finally:
        await close_db_connection()


async def create_admin_user(username: str = "admin", email: str = "admin@example.com") -> None:
    """
    Create an admin user and role.
    
    Args:
        username: Admin username (default: admin)
        password: Admin password (default: admin123)
        email: Admin email (default: admin@example.com)
    """
    logger.info(f"Creating admin user: {username}")
    
    try:
        # Create a session
        from sqlalchemy.ext.asyncio import AsyncSession
        from src.db.repositories.users import UserRepository
        from src.utils.password import get_password_hash
        from src.db.models.users import Role, User, user_roles
        from sqlalchemy import select, insert, inspect
        import uuid
        import datetime
        
        # Get database engine
        engine = get_engine()
        
        # Check if tables exist
        from sqlalchemy.schema import MetaData
        metadata = MetaData()
        async with engine.connect() as conn:
            # Check if the roles table exists
            try:
                await conn.execute(select(1).select_from(Role.__table__))
                logger.info("Tables already exist")
            except Exception as e:
                logger.warning(f"Tables don't exist, creating them: {e}")
                # Create tables if they don't exist
                await create_tables()
                # Seed basic data
                await seed_data()
        
        async with AsyncSession(engine) as session:
            # Create a session factory that returns the session
            session_factory = lambda: session
            user_repo = UserRepository(session_factory)
            
            # Check if admin role exists
            admin_role = await user_repo.get_role_by_name('admin')
            if not admin_role:
                logger.info('Creating admin role...')
                now = datetime.datetime.utcnow()
                admin_role_id = str(uuid.uuid4())
                admin_role_stmt = insert(Role).values(
                    id=admin_role_id,
                    name='admin',
                    description='Administrator with full system access',
                    created_at=now,
                    updated_at=now
                )
                await session.execute(admin_role_stmt)
                await session.commit()
                admin_role = await user_repo.get_role_by_name('admin')
                logger.info('Admin role created successfully!')
            else:
                logger.info('Admin role already exists')
            
            # Check if admin user exists
            admin_user = await user_repo.get_by_username(username)
            if not admin_user:
                logger.info('Creating admin user...')
                admin_user = await user_repo.create(session, obj_in={
                    'username': username,
                    'email': email,
                    'password_hash': '$2b$12$WMUO584qliC2ell5l0YKKuIK2sgVnEdONTrWFIgh29fWr9alqSHiO',
                    'full_name': 'System Administrator',
                    'status': 'active'
                })
                
                # Add admin role to admin user using direct table insert
                # This avoids the async issue with lazy loading of user.roles
                role_user_stmt = insert(user_roles).values(
                    user_id=admin_user.id,
                    role_id=admin_role.id
                )
                await session.execute(role_user_stmt)
                await session.commit()
                
                logger.info('Admin user created successfully!')
            else:
                logger.info('Admin user already exists')
                
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        raise
    finally:
        await close_db_connection()


async def force_seed_algorithms() -> None:
    """
    Force seed the algorithms and curves directly to the database,
    bypassing the registry system.
    """
    logger.info("Force seeding algorithms and curves directly")
    
    try:
        import uuid
        import datetime
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy import insert
        from src.db.models.algorithms import Algorithm, Curve
        
        # Get database engine
        engine = get_engine()
        
        async with AsyncSession(engine) as session:
            # Define the algorithms
            now = datetime.datetime.utcnow()
            
            # ECDSA
            ecdsa_id = str(uuid.uuid4())
            ecdsa_algo = {
                "id": ecdsa_id,
                "name": "ECDSA",
                "type": "elliptic-curve",
                "description": "Elliptic Curve Digital Signature Algorithm",
                "is_default": True,
                "status": "enabled",
                "created_at": now,
                "updated_at": now
            }
            
            # Create ECDSA curves
            secp256k1_curve = {
                "id": str(uuid.uuid4()),
                "name": "secp256k1",
                "algorithm_id": ecdsa_id,
                "description": "SECG curve used in Bitcoin and blockchain applications",
                "parameters": {
                    "bit_size": 256,
                    "hash_algorithm": "SHA256",
                    "is_default": True,
                    "p": 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F,
                    "a": 0,
                    "b": 7,
                    "g": (
                        0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
                        0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
                    ),
                    "n": 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,
                },
                "status": "enabled",
                "created_at": now,
                "updated_at": now
            }
            
            secp256r1_curve = {
                "id": str(uuid.uuid4()),
                "name": "secp256r1",
                "algorithm_id": ecdsa_id,
                "description": "NIST curve P-256, widely used for general purpose applications",
                "parameters": {
                    "bit_size": 256,
                    "hash_algorithm": "SHA256"
                },
                "status": "enabled",
                "created_at": now,
                "updated_at": now
            }
            
            # EdDSA
            eddsa_id = str(uuid.uuid4())
            eddsa_algo = {
                "id": eddsa_id,
                "name": "EdDSA",
                "type": "edwards-curve",
                "description": "Edwards-curve Digital Signature Algorithm",
                "is_default": False,
                "status": "enabled",
                "created_at": now,
                "updated_at": now
            }
            
            # Create EdDSA curve
            ed25519_curve = {
                "id": str(uuid.uuid4()),
                "name": "ed25519",
                "algorithm_id": eddsa_id,
                "description": "Edwards curve 25519, fast and secure for general use",
                "parameters": {
                    "bit_size": 256,
                    "hash_algorithm": "SHA512"
                },
                "status": "enabled",
                "created_at": now,
                "updated_at": now
            }
            
            # RSA
            rsa_id = str(uuid.uuid4())
            rsa_algo = {
                "id": rsa_id,
                "name": "RSA-SHA256",
                "type": "asymmetric",
                "description": "RSA Signature Algorithm with SHA-256",
                "is_default": False,
                "status": "enabled",
                "created_at": now,
                "updated_at": now
            }
            
            # Create RSA parameters
            rsa_2048_params = {
                "id": str(uuid.uuid4()),
                "name": "rsa-2048",
                "algorithm_id": rsa_id,
                "description": "RSA with 2048-bit key length",
                "parameters": {
                    "bit_size": 2048,
                    "hash_algorithm": "SHA256"
                },
                "status": "enabled",
                "created_at": now,
                "updated_at": now
            }
            
            rsa_4096_params = {
                "id": str(uuid.uuid4()),
                "name": "rsa-4096",
                "algorithm_id": rsa_id,
                "description": "RSA with 4096-bit key length",
                "parameters": {
                    "bit_size": 4096,
                    "hash_algorithm": "SHA256"
                },
                "status": "enabled",
                "created_at": now,
                "updated_at": now
            }
            
            # Insert algorithms
            for algo in [ecdsa_algo, eddsa_algo, rsa_algo]:
                try:
                    stmt = insert(Algorithm).values(**algo)
                    await session.execute(stmt)
                except Exception as e:
                    logger.warning(f"Could not insert algorithm {algo['name']}: {e}")
            
            # Insert curves
            for curve in [secp256k1_curve, secp256r1_curve, ed25519_curve, rsa_2048_params, rsa_4096_params]:
                try:
                    stmt = insert(Curve).values(**curve)
                    await session.execute(stmt)
                except Exception as e:
                    logger.warning(f"Could not insert curve {curve['name']}: {e}")
            
            await session.commit()
            
            logger.info("Successfully force seeded algorithms and curves")
            
    except Exception as e:
        logger.error(f"Error force seeding algorithms: {e}")
        raise
    finally:
        await close_db_connection()


def main() -> None:
    """
    Main CLI entrypoint.
    """
    parser = argparse.ArgumentParser(description="UET Thesis Backend CLI")
    
    # Add a subparser for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # create-tables command
    create_tables_parser = subparsers.add_parser(
        "create-tables", 
        help="Create database tables from SQLAlchemy models"
    )
    create_tables_parser.add_argument(
        "--drop-first", 
        action="store_true", 
        help="Drop existing tables before creating new ones"
    )
    create_tables_parser.add_argument(
        "--tables", 
        nargs="+", 
        help="Specific tables to create (space-separated)"
    )
    
    # seed-data command
    seed_data_parser = subparsers.add_parser(
        "seed-data",
        help="Seed the database with initial data (algorithms, curves, roles, admin user and sample data)"
    )
    
    # create-admin command
    create_admin_parser = subparsers.add_parser(
        "create-admin",
        help="Create an admin user and role"
    )
    create_admin_parser.add_argument(
        "--username", 
        default="admin",
        help="Admin username (default: admin)"
    )
    create_admin_parser.add_argument(
        "--password", 
        default="admin123",
        help="Admin password (default: admin123)"
    )
    create_admin_parser.add_argument(
        "--email", 
        default="admin@example.com",
        help="Admin email (default: admin@example.com)"
    )
    
    # force-seed-algorithms command
    force_seed_algorithms_parser = subparsers.add_parser(
        "force-seed-algorithms",
        help="Force seed algorithms and curves directly into the database"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the appropriate command
    if args.command == "create-tables":
        asyncio.run(create_tables(drop_first=args.drop_first, specific_tables=args.tables))
    elif args.command == "seed-data":
        asyncio.run(seed_data())
    elif args.command == "create-admin":
        asyncio.run(create_admin_user(
            username=args.username,
            email=args.email
        ))
    elif args.command == "force-seed-algorithms":
        asyncio.run(force_seed_algorithms())
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main() 