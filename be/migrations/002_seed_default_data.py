#!/usr/bin/env python
"""
Migration script to seed default data for tables.
"""

import logging
import asyncio
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from werkzeug.security import generate_password_hash

from src.db.session import get_engine, SessionLocal
from src.db.models.algorithms import Algorithm, Curve
from src.db.models.users import User, Role, Permission
from src.db.models.public_keys import PublicKey
from src.db.models.verification import VerificationRecord, BatchVerification

logger = logging.getLogger(__name__)


async def check_if_migration_needed() -> bool:
    """Check if the migration is needed by looking for existing seed data."""
    async with AsyncSession(get_engine()) as session:
        # Check if sample public keys exist
        public_keys = await session.execute(select(PublicKey))
        if public_keys.scalars().first():
            logger.info("Sample public keys already exist in the database, skipping data seeding")
            return False
        else:
            logger.info("No sample data found, will create it")
            return True


async def run_migration():
    """Run the migration to seed default data for tables."""
    try:
        # Check if migration is needed
        if not await check_if_migration_needed():
            logger.info("Migration already applied, skipping")
            return

        logger.info("Starting to seed default data for tables")
        
        # Create a session for the seed operation
        async with SessionLocal() as session:
            # Get admin user
            admin_user = await session.execute(select(User).filter(User.username == "admin"))
            admin_user = admin_user.scalars().first()
            
            if not admin_user:
                logger.error("Admin user not found. Please run 001_seed_algorithms_and_admin.py first")
                return
                
            # Get algorithms and curves
            ecdsa_algo = await session.execute(select(Algorithm).filter(Algorithm.name == "ECDSA"))
            ecdsa_algo = ecdsa_algo.scalars().first()
            
            secp256r1_curve = await session.execute(
                select(Curve).filter(Curve.name == "secp256r1", Curve.algorithm_id == ecdsa_algo.id)
            )
            secp256r1_curve = secp256r1_curve.scalars().first()
            
            # Add sample public keys
            public_key1 = PublicKey(
                id=str(uuid.uuid4()),
                name="Sample ECDSA Key",
                user_id=admin_user.id,
                key_data="LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowREFRY0RRZ0FFdFY1SGdWcVlsMHd5VVdFSmRIaENDOTE0UHZpbgphRGJvK1NxVUprMDJRNFJWRjQ4cHc1MnpYeXg5bnEreDFDNFVDaUlCNnJ1ZzNCTExTbDVobDY2V0NBPT0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t",
                algorithm_id=ecdsa_algo.id,
                curve_id=secp256r1_curve.id,
                key_format="PEM",
                status="active",
                description="Sample ECDSA secp256r1 key for testing",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(public_key1)
            
            # Add sample verification records
            verification1 = VerificationRecord(
                id=str(uuid.uuid4()),
                user_id=admin_user.id,
                document_hash="c2FtcGxlLWhhc2gtZGF0YQ==",
                signature="c2FtcGxlLXNpZ25hdHVyZS1kYXRh",
                public_key_id=public_key1.id,
                algorithm_id=ecdsa_algo.id,
                curve_id=secp256r1_curve.id,
                verification_result=True,
                verification_time=datetime.utcnow() - timedelta(days=1),
                created_at=datetime.utcnow() - timedelta(days=1),
                updated_at=datetime.utcnow() - timedelta(days=1)
            )
            session.add(verification1)
            
            verification2 = VerificationRecord(
                id=str(uuid.uuid4()),
                user_id=admin_user.id,
                document_hash="c2FtcGxlLWhhc2gtZGF0YS0y",
                signature="c2FtcGxlLXNpZ25hdHVyZS1kYXRhLTI=",
                public_key_id=public_key1.id,
                algorithm_id=ecdsa_algo.id,
                curve_id=secp256r1_curve.id,
                verification_result=False,
                verification_time=datetime.utcnow() - timedelta(hours=12),
                created_at=datetime.utcnow() - timedelta(hours=12),
                updated_at=datetime.utcnow() - timedelta(hours=12)
            )
            session.add(verification2)
            
            # Add sample batch verification
            batch = BatchVerification(
                id=str(uuid.uuid4()),
                user_id=admin_user.id,
                name="Sample Batch",
                description="Sample batch verification for testing",
                status="completed",
                total_documents=2,
                verified_documents=1,
                failed_documents=1,
                created_at=datetime.utcnow() - timedelta(days=1),
                updated_at=datetime.utcnow() - timedelta(days=1),
                completed_at=datetime.utcnow() - timedelta(days=1)
            )
            session.add(batch)
            
            # Add regular test user
            test_user = User(
                id=str(uuid.uuid4()),
                username="testuser",
                email="test@example.com",
                password_hash=generate_password_hash("test123"),
                full_name="Test User",
                status="active",
                is_superuser=False,
                last_login=datetime.utcnow() - timedelta(days=3)
            )
            session.add(test_user)
            
            # Add user role to test user
            user_role = await session.execute(select(Role).filter(Role.name == "user"))
            user_role = user_role.scalars().first()
            
            test_user.roles.append(user_role)
            
            # Commit the session to save all entities
            await session.commit()
        
        logger.info("Default data seeded successfully")
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        raise


def main():
    """Entry point for running the migration."""
    logging.basicConfig(level=logging.INFO)
    logger.info("Running migration to seed default data")
    asyncio.run(run_migration())


if __name__ == "__main__":
    main() 