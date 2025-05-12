from sqlalchemy.orm import Session
from app.models.key_pair import KeyPair
from app.schemas.key_pair import KeyPairCreate
from app.core.security import generate_key_pair, encrypt_private_key
from typing import Optional, List

def get_key_pair(db: Session, key_pair_id: int) -> Optional[KeyPair]:
    return db.query(KeyPair).filter(KeyPair.id == key_pair_id).first()

def get_key_pairs_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[KeyPair]:
    return db.query(KeyPair).filter(
        KeyPair.user_id == user_id,
        KeyPair.is_active == True
    ).offset(skip).limit(limit).all()

def create_key_pair(db: Session, user_id: int, key_pair: KeyPairCreate, user_password: str) -> KeyPair:
    # Generate a new key pair
    private_key_pem, public_key_pem = generate_key_pair(key_pair.curve_name)
    
    # Encrypt the private key with the user's password
    encrypted_private_key = encrypt_private_key(private_key_pem, user_password)
    
    # Create DB model
    db_key_pair = KeyPair(
        user_id=user_id,
        name=key_pair.name,
        public_key=public_key_pem,
        encrypted_private_key=encrypted_private_key,
        curve_name=key_pair.curve_name,
        is_active=True
    )
    
    db.add(db_key_pair)
    db.commit()
    db.refresh(db_key_pair)
    return db_key_pair

def deactivate_key_pair(db: Session, key_pair_id: int, user_id: int) -> bool:
    # Only deactivate keys, don't delete them
    db_key_pair = db.query(KeyPair).filter(
        KeyPair.id == key_pair_id,
        KeyPair.user_id == user_id
    ).first()
    
    if not db_key_pair:
        return False
    
    db_key_pair.is_active = False
    db.commit()
    return True 