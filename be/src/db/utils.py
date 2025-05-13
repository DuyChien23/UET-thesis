"""
Database utility functions for data seeding and management.
"""

import uuid
import logging
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash
import copy

from src.algorithms.ecdsa.provider import ECDSAProvider
from src.algorithms.eddsa.provider import EdDSAProvider
from src.algorithms.rsa.provider import RSAProvider
from src.db.models.algorithms import Algorithm, Curve
from src.db.models.users import User, Role, Permission

logger = logging.getLogger(__name__)

def seed_database(session: Session) -> None:
    """
    Utility function to seed initial data into the database.
    This function can be used in migrations or initial setup.
    
    Args:
        session: A database session object
    """
    # Seed algorithms and their curves
    seed_algorithms_and_curves(session)
    
    # Seed roles and admin user
    seed_roles_and_admin(session)
    
    # Commit all changes
    session.commit()
    logger.info("Database seeding completed successfully")


def make_json_serializable(params):
    """
    Make a copy of the parameters dictionary with any non-JSON-serializable objects 
    converted to string representations.
    
    Args:
        params: Dictionary of parameters
        
    Returns:
        Dictionary with JSON-serializable values
    """
    result = {}
    for key, value in params.items():
        if key == 'hash_algorithm':
            # Convert hash algorithm objects to their string names
            if hasattr(value, 'name'):
                result[key] = value.name
            else:
                result[key] = str(value)
        elif isinstance(value, dict):
            result[key] = make_json_serializable(value)
        else:
            result[key] = value
    return result


def seed_algorithms_and_curves(session: Session) -> None:
    """
    Seed algorithms and curves from the providers into the database.
    
    Args:
        session: A database session object
    """
    logger.info("Seeding algorithms and curves")
    
    # ECDSA
    ecdsa_provider = ECDSAProvider()
    ecdsa_algo = Algorithm(
        id=str(uuid.uuid4()),
        name=ecdsa_provider.get_algorithm_name(),
        type=ecdsa_provider.get_algorithm_type(),
        description="Elliptic Curve Digital Signature Algorithm"
    )
    session.add(ecdsa_algo)
    
    for name, params in ecdsa_provider.get_supported_curves().items():
        # Make a copy of params to avoid modifying the original
        safe_params = make_json_serializable(params)
        
        curve = Curve(
            id=str(uuid.uuid4()),
            name=name,
            algorithm_id=ecdsa_algo.id,
            parameters=safe_params,
            description=params.get("description", ""),
            status="enabled"
        )
        session.add(curve)
    
    # EdDSA
    eddsa_provider = EdDSAProvider()
    eddsa_algo = Algorithm(
        id=str(uuid.uuid4()),
        name=eddsa_provider.get_algorithm_name(),
        type=eddsa_provider.get_algorithm_type(),
        description="Edwards-curve Digital Signature Algorithm"
    )
    session.add(eddsa_algo)
    
    for name, params in eddsa_provider.get_supported_curves().items():
        safe_params = make_json_serializable(params)
        
        curve = Curve(
            id=str(uuid.uuid4()),
            name=name,
            algorithm_id=eddsa_algo.id,
            parameters=safe_params,
            description=params.get("description", ""),
            status="enabled"
        )
        session.add(curve)
    
    # RSA
    rsa_provider = RSAProvider()
    rsa_algo = Algorithm(
        id=str(uuid.uuid4()),
        name=rsa_provider.get_algorithm_name(),
        type=rsa_provider.get_algorithm_type(),
        description="RSA Signature Algorithm with SHA-256"
    )
    session.add(rsa_algo)
    
    for name, params in rsa_provider.get_supported_curves().items():
        safe_params = make_json_serializable(params)
        
        curve = Curve(
            id=str(uuid.uuid4()),
            name=name,
            algorithm_id=rsa_algo.id,
            parameters=safe_params,
            description=params.get("description", ""),
            status="enabled"
        )
        session.add(curve)
    
    logger.info("Algorithms and curves seeded successfully")


def seed_roles_and_admin(session: Session) -> None:
    """
    Seed roles and admin user into the database.
    
    Args:
        session: A database session object
    """
    logger.info("Seeding roles and admin user")
    
    # Create roles
    admin_role = Role(
        id=str(uuid.uuid4()),
        name="admin",
        description="Administrator with full access"
    )
    session.add(admin_role)
    
    user_role = Role(
        id=str(uuid.uuid4()),
        name="user",
        description="Regular user with standard permissions"
    )
    session.add(user_role)
    
    # Create default admin user
    admin_user = User(
        id=str(uuid.uuid4()),
        username="admin",
        email="admin@example.com",
        password_hash=generate_password_hash("admin123", method='pbkdf2:sha256'),
        full_name="Administrator",
        status="active",
        is_superuser=True
    )
    session.add(admin_user)
    
    # Add admin role to admin user
    admin_user.roles.append(admin_role)
    
    logger.info("Roles and admin user seeded successfully") 