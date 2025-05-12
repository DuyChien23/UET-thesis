from sqlalchemy.orm import Session
from app.models.signature import Signature
from app.schemas.signature import SignatureCreate
from app.core.security import compute_hash
from typing import Optional, List

def get_signature(db: Session, signature_id: int) -> Optional[Signature]:
    return db.query(Signature).filter(Signature.id == signature_id).first()

def get_signatures_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Signature]:
    return db.query(Signature).filter(Signature.user_id == user_id).offset(skip).limit(limit).all()

def get_signatures_by_key_pair_id(db: Session, key_pair_id: int, skip: int = 0, limit: int = 100) -> List[Signature]:
    return db.query(Signature).filter(Signature.key_pair_id == key_pair_id).offset(skip).limit(limit).all()

def create_signature(
    db: Session, 
    user_id: int, 
    signature_data: str, 
    data_hash: str, 
    original_data: Optional[str],
    key_pair_id: int,
    content_type: str,
    file_name: Optional[str] = None
) -> Signature:
    db_signature = Signature(
        user_id=user_id,
        key_pair_id=key_pair_id,
        signature=signature_data,
        data_hash=data_hash,
        original_data=original_data,
        content_type=content_type,
        file_name=file_name
    )
    db.add(db_signature)
    db.commit()
    db.refresh(db_signature)
    return db_signature

def delete_signature(db: Session, signature_id: int, user_id: int) -> bool:
    db_signature = db.query(Signature).filter(
        Signature.id == signature_id,
        Signature.user_id == user_id
    ).first()
    
    if not db_signature:
        return False
    
    db.delete(db_signature)
    db.commit()
    return True 