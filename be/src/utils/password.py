"""
Password hashing and verification utilities.
"""

import secrets
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Hash a password.
    
    Args:
        password (str): Password to hash
        
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password (str): Password to verify
        hashed_password (str): Hash to verify against
        
    Returns:
        bool: True if the password matches the hash, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_random_password(length: int = 12) -> str:
    """
    Generate a random password.
    
    Args:
        length (int): Length of the password
        
    Returns:
        str: Random password
    """
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    return "".join(secrets.choice(alphabet) for _ in range(length)) 