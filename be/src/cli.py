"""
CLI utility module for the application.
Provides command-line tools for database operations and other tasks.
"""

import logging
import asyncio
import argparse
import sys
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
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the appropriate command
    if args.command == "create-tables":
        asyncio.run(create_tables(drop_first=args.drop_first, specific_tables=args.tables))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main() 