from sqlalchemy.orm import Session
from app.repositories import signature as signature_repo
from app.repositories import key_pair as key_pair_repo
from app.schemas.signature import SignatureCreate, Signature, SignatureVerify
from app.core.security import sign_data, verify_signature, decrypt_private_key, compute_hash
from typing import List, Optional
from fastapi import HTTPException, status
import base64
import hashlib
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature

from app.repositories.signature_repository import SignatureRepository
from app.repositories.key_pair_repository import KeyPairRepository
from app.services.key_pair_service import KeyPairService, CURVE_MAP

class SignatureService:
    def __init__(self, db: Session):
        self.repository = SignatureRepository(db)
        self.key_pair_repository = KeyPairRepository(db)
        self.key_pair_service = KeyPairService(db)
    
    def sign_text(self, text_data: str, key_pair_id: int, user_id: int):
        # Validate key pair exists and belongs to user
        key_pair = self.key_pair_repository.get_by_id(key_pair_id)
        if not key_pair or key_pair.user_id != user_id:
            raise ValueError("Key pair not found or does not belong to user")
        
        # Generate hash of the text data
        data_bytes = text_data.encode('utf-8')
        data_hash = hashlib.sha256(data_bytes).hexdigest()
        
        # Create a signature object (placeholder)
        # In a real implementation, you'd use the key_pair to sign the data
        # For now this is just storing the data to sign later
        signature = self.repository.create_signature(
            user_id=user_id,
            key_pair_id=key_pair_id,
            signature="placeholder",  # Will be updated after signing
            data_hash=data_hash,
            original_data=text_data,
            content_type="text/plain",
            file_name=None
        )
        
        # This is where you'd implement the actual signing logic
        # We'll need to prompt for the user's password to decrypt the private key
        
        return signature
    
    def sign_file(self, file_content: bytes, filename: str, content_type: str, key_pair_id: int, user_id: int):
        # Validate key pair exists and belongs to user
        key_pair = self.key_pair_repository.get_by_id(key_pair_id)
        if not key_pair or key_pair.user_id != user_id:
            raise ValueError("Key pair not found or does not belong to user")
        
        # Generate hash of the file data
        data_hash = hashlib.sha256(file_content).hexdigest()
        
        # For files, we may not want to store the full content in the database
        # Instead, just store the hash and file metadata
        signature = self.repository.create_signature(
            user_id=user_id,
            key_pair_id=key_pair_id,
            signature="placeholder",  # Will be updated after signing
            data_hash=data_hash,
            original_data=None,  # Don't store large file content
            content_type=content_type,
            file_name=filename
        )
        
        # In a real implementation, you'd use the key_pair to sign the data
        # We'd need to prompt for the user's password to decrypt the private key
        
        return signature
    
    def get_user_signatures(self, user_id: int):
        return self.repository.get_by_user_id(user_id)
    
    def get_signature(self, signature_id: int, user_id: int):
        signature = self.repository.get_by_id(signature_id)
        if not signature or signature.user_id != user_id:
            return None
        return signature
    
    def verify_signature(self, verification_data: SignatureVerify) -> bool:
        try:
            # Decode the signature
            signature_bytes = base64.b64decode(verification_data.signature)
            
            # Get the data hash
            data_bytes = verification_data.data.encode('utf-8')
            data_hash = hashlib.sha256(data_bytes).digest()
            
            # Load the public key
            public_key = serialization.load_pem_public_key(
                verification_data.public_key.encode('utf-8')
            )
            
            # Verify the signature
            try:
                public_key.verify(
                    signature_bytes,
                    data_hash,
                    ec.ECDSA(hashes.SHA256())
                )
                return True
            except InvalidSignature:
                return False
        except Exception as e:
            raise ValueError(f"Verification error: {str(e)}")
    
    def _sign_data(self, data_hash_hex: str, private_key_bytes: bytes, curve_name: str):
        # Convert hex hash to bytes
        data_hash = bytes.fromhex(data_hash_hex)
        
        # Load the private key
        private_key = serialization.load_pem_private_key(
            private_key_bytes,
            password=None
        )
        
        # Sign the data hash
        signature = private_key.sign(
            data_hash,
            ec.ECDSA(hashes.SHA256())
        )
        
        # Return base64 encoded signature
        return base64.b64encode(signature).decode('utf-8')

def get_signature(db: Session, signature_id: int) -> Signature:
    db_signature = signature_repo.get_signature(db, signature_id)
    if not db_signature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Signature with id {signature_id} not found"
        )
    return db_signature

def get_user_signatures(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Signature]:
    return signature_repo.get_signatures_by_user_id(db, user_id, skip, limit)

def create_signature(
    db: Session, 
    user_id: int, 
    signature_data: SignatureCreate, 
    user_password: str
) -> Signature:
    # Get the key pair
    key_pair = key_pair_repo.get_key_pair(db, signature_data.key_pair_id)
    if not key_pair or key_pair.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Key pair not found or not owned by user"
        )
    
    if not key_pair.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Key pair is not active"
        )
    
    try:
        # Decode base64 data if needed
        data = signature_data.data
        
        # Compute hash of the data
        data_hash = compute_hash(data)
        
        # Decrypt private key
        private_key_pem = decrypt_private_key(key_pair.encrypted_private_key, user_password)
        
        # Sign the data
        signature_value = sign_data(data, private_key_pem)
        
        # Store original data only if it's not too large (limit to 10KB)
        original_data = data if len(data) <= 10240 else None
        
        # Create signature in database
        return signature_repo.create_signature(
            db=db,
            user_id=user_id,
            signature_data=signature_value,
            data_hash=data_hash,
            original_data=original_data,
            key_pair_id=key_pair.id,
            content_type=signature_data.content_type,
            file_name=signature_data.file_name
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create signature: {str(e)}"
        )

def verify_signature_data(db: Session, verify_data: SignatureVerify) -> bool:
    try:
        # Verify the signature
        is_valid = verify_signature(
            data=verify_data.data,
            signature=verify_data.signature,
            public_key_pem=verify_data.public_key
        )
        return is_valid
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to verify signature: {str(e)}"
        )

def delete_signature(db: Session, signature_id: int, user_id: int) -> bool:
    result = signature_repo.delete_signature(db, signature_id, user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Signature with id {signature_id} not found or not owned by user"
        )
    return result 