from sqlalchemy.orm import Session
import os
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, padding
import base64
import os

from app.repositories import key_pair as key_pair_repo
from app.schemas.key_pair import KeyPairCreate, KeyPair, KeyPairPublic
from typing import List, Optional
from fastapi import HTTPException, status

from app.repositories.key_pair_repository import KeyPairRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import verify_password

# Get the curve from environment variables or use default
DEFAULT_CURVE_NAME = os.getenv("CURVE_NAME", "secp521r1")

# Map curve names to their cryptography objects
CURVE_MAP = {
    "secp256k1": ec.SECP256K1(),
    "secp384r1": ec.SECP384R1(),
    "secp521r1": ec.SECP521R1()
}

class KeyPairService:
    def __init__(self, db: Session):
        self.repository = KeyPairRepository(db)
        self.user_repository = UserRepository(db)
    
    def create_key_pair(self, key_pair_data: KeyPairCreate, user_id: int):
        # Get the user to verify password
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Verify user password for private key encryption
        if not verify_password(key_pair_data.user_password, user.hashed_password):
            raise ValueError("Invalid password")
        
        # Get the curve to use
        curve_name = key_pair_data.curve_name if key_pair_data.curve_name else DEFAULT_CURVE_NAME
        if curve_name not in CURVE_MAP:
            raise ValueError(f"Unsupported curve: {curve_name}. Supported curves: {', '.join(CURVE_MAP.keys())}")
        
        curve = CURVE_MAP[curve_name]
        
        # Generate key pair
        private_key = ec.generate_private_key(curve)
        public_key = private_key.public_key()
        
        # Serialize public key
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Serialize and encrypt private key
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Custom encryption of private key with user password
        encrypted_private_key = self._encrypt_private_key(private_key_bytes, key_pair_data.user_password)
        
        # Store key pair in database
        return self.repository.create_key_pair(
            user_id=user_id,
            public_key=public_key_bytes.decode(),
            encrypted_private_key=encrypted_private_key,
            curve_name=curve_name,
            name=key_pair_data.name
        )
    
    def get_user_key_pairs(self, user_id: int):
        return self.repository.get_by_user_id(user_id)
    
    def get_key_pair(self, key_pair_id: int, user_id: int):
        key_pair = self.repository.get_by_id(key_pair_id)
        if not key_pair or key_pair.user_id != user_id:
            return None
        return key_pair
    
    def _encrypt_private_key(self, private_key_bytes: bytes, password: str) -> str:
        # Create a key from the password
        password_bytes = password.encode()
        key = self._derive_key(password_bytes)
        
        # Generate a random IV
        iv = os.urandom(16)
        
        # Pad the data
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(private_key_bytes) + padder.finalize()
        
        # Encrypt the data
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # Combine IV and encrypted data and encode as base64
        return base64.b64encode(iv + encrypted_data).decode('utf-8')
    
    def decrypt_private_key(self, encrypted_private_key: str, password: str) -> bytes:
        # Decode from base64
        data = base64.b64decode(encrypted_private_key)
        
        # Extract IV and encrypted data
        iv = data[:16]
        encrypted_data = data[16:]
        
        # Create a key from the password
        password_bytes = password.encode()
        key = self._derive_key(password_bytes)
        
        # Decrypt the data
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # Unpad the data
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(padded_data) + unpadder.finalize()
    
    def _derive_key(self, password: bytes) -> bytes:
        # Simple key derivation function - in production, use PBKDF2 or similar
        digest = hashes.Hash(hashes.SHA256())
        digest.update(password)
        return digest.finalize()

def get_key_pair(db: Session, key_pair_id: int) -> KeyPair:
    db_key_pair = key_pair_repo.get_key_pair(db, key_pair_id)
    if not db_key_pair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Key pair with id {key_pair_id} not found"
        )
    return db_key_pair

def get_user_key_pairs(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[KeyPair]:
    return key_pair_repo.get_key_pairs_by_user_id(db, user_id, skip, limit)

def create_key_pair(db: Session, user_id: int, key_pair: KeyPairCreate, user_password: str) -> KeyPair:
    try:
        return key_pair_repo.create_key_pair(db, user_id, key_pair, user_password)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create key pair: {str(e)}"
        )

def deactivate_key_pair(db: Session, key_pair_id: int, user_id: int) -> bool:
    result = key_pair_repo.deactivate_key_pair(db, key_pair_id, user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Key pair with id {key_pair_id} not found or not owned by user"
        )
    return result 