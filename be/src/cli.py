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
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the appropriate command
    if args.command == "create-tables":
        asyncio.run(create_tables(drop_first=args.drop_first, specific_tables=args.tables))
    elif args.command == "seed-data":
        asyncio.run(seed_data())
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main() 