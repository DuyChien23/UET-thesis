#!/usr/bin/env python
"""
Migration script to seed algorithms, curves, roles, and admin user.
"""

import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.db.session import get_engine, SessionLocal
from src.db.models.algorithms import Algorithm
from src.db.models.users import User
from src.db.utils import seed_database

logger = logging.getLogger(__name__)


async def check_if_migration_needed() -> bool:
    """Check if the migration is needed by looking for existing algorithms and admin user."""
    async with AsyncSession(get_engine()) as session:
        # Check if algorithms already exist
        algorithms = await session.execute(select(Algorithm))
        if algorithms.scalars().first():
            logger.info("Algorithms already exist in the database, skipping algorithm creation")
            has_algorithms = True
        else:
            logger.info("No algorithms found in the database, will create them")
            has_algorithms = False

        # Check if admin user already exists
        admin = await session.execute(select(User).filter(User.username == "admin"))
        if admin.scalars().first():
            logger.info("Admin user already exists, skipping admin user creation")
            has_admin = True
        else:
            logger.info("No admin user found, will create it")
            has_admin = False

        return not (has_algorithms and has_admin)


async def run_migration():
    """Run the migration to seed the database with algorithms, curves, and admin user."""
    try:
        # Check if migration is needed
        if not await check_if_migration_needed():
            logger.info("Migration already applied, skipping")
            return

        logger.info("Starting to seed the database with algorithms, curves, and admin user")
        
        # Create a session for the seed operation
        async with SessionLocal() as session:
            # Use the seed_database function to populate the database
            seed_database(session.sync_session)
        
        logger.info("Database seeded successfully with algorithms, curves, and admin user")
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        raise


def main():
    """Entry point for running the migration."""
    logging.basicConfig(level=logging.INFO)
    logger.info("Running migration to seed algorithms, curves, and admin user")
    asyncio.run(run_migration())


if __name__ == "__main__":
    main() 