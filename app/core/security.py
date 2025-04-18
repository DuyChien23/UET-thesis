from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import os
import hashlib

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# ECDSA operations
def get_curve_by_name(curve_name: str):
    curves = {
        "secp256k1": ec.SECP256K1(),
        "secp384r1": ec.SECP384R1(),
        "secp521r1": ec.SECP521R1()
    }
    return curves.get(curve_name, ec.SECP521R1())

def generate_key_pair(curve_name: str = settings.CURVE_NAME):
    curve = get_curve_by_name(curve_name)
    private_key = ec.generate_private_key(curve)
    public_key = private_key.public_key()
    
    # Serialize public key
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    
    # Serialize private key
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    return private_key_pem, public_key_pem

def encrypt_private_key(private_key_pem: str, user_password: str) -> str:
    # Derive key from password
    key = hashlib.pbkdf2_hmac(
        'sha256', 
        user_password.encode(), 
        settings.SECRET_KEY.encode(), 
        100000,
        32
    )
    
    # Generate a random nonce
    nonce = os.urandom(12)
    
    # Encrypt the private key
    aesgcm = AESGCM(key)
    private_key_bytes = private_key_pem.encode()
    ciphertext = aesgcm.encrypt(nonce, private_key_bytes, None)
    
    # Combine nonce and ciphertext for storage
    encrypted_data = nonce + ciphertext
    return base64.b64encode(encrypted_data).decode('utf-8')

def decrypt_private_key(encrypted_key: str, user_password: str) -> str:
    # Derive key from password
    key = hashlib.pbkdf2_hmac(
        'sha256', 
        user_password.encode(), 
        settings.SECRET_KEY.encode(), 
        100000,
        32
    )
    
    # Decode the encrypted data
    encrypted_data = base64.b64decode(encrypted_key)
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    
    # Decrypt the private key
    aesgcm = AESGCM(key)
    try:
        private_key_bytes = aesgcm.decrypt(nonce, ciphertext, None)
        return private_key_bytes.decode('utf-8')
    except Exception as e:
        raise ValueError("Invalid password or corrupted key")

def sign_data(data: str, private_key_pem: str) -> str:
    # Load private key
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(),
        password=None
    )
    
    # Compute hash of the data
    data_bytes = data.encode() if isinstance(data, str) else data
    signature = private_key.sign(
        data_bytes,
        ec.ECDSA(hashes.SHA256())
    )
    
    # Return base64 encoded signature
    return base64.b64encode(signature).decode('utf-8')

def verify_signature(data: str, signature: str, public_key_pem: str) -> bool:
    try:
        # Convert base64 signature to bytes
        signature_bytes = base64.b64decode(signature)
        
        # Load public key
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode()
        )
        
        # Verify signature
        data_bytes = data.encode() if isinstance(data, str) else data
        public_key.verify(
            signature_bytes,
            data_bytes,
            ec.ECDSA(hashes.SHA256())
        )
        
        return True
    except Exception as e:
        return False

def compute_hash(data: str or bytes) -> str:
    """Compute SHA-256 hash of data"""
    if isinstance(data, str):
        data = data.encode()
    
    return hashlib.sha256(data).hexdigest() 