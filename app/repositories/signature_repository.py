from sqlalchemy.orm import Session
from typing import Optional, List

from app.models.signature import Signature

class SignatureRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, signature_id: int) -> Optional[Signature]:
        return self.db.query(Signature).filter(Signature.id == signature_id).first()
    
    def get_by_user_id(self, user_id: int) -> List[Signature]:
        return self.db.query(Signature).filter(Signature.user_id == user_id).all()
    
    def get_by_data_hash(self, data_hash: str) -> List[Signature]:
        return self.db.query(Signature).filter(Signature.data_hash == data_hash).all()
    
    def create_signature(self, 
                         user_id: int, 
                         key_pair_id: int, 
                         signature: str, 
                         data_hash: str, 
                         original_data: Optional[str], 
                         content_type: str, 
                         file_name: Optional[str]) -> Signature:
        signature_obj = Signature(
            user_id=user_id,
            key_pair_id=key_pair_id,
            signature=signature,
            data_hash=data_hash,
            original_data=original_data,
            content_type=content_type,
            file_name=file_name
        )
        self.db.add(signature_obj)
        self.db.commit()
        self.db.refresh(signature_obj)
        return signature_obj
    
    def update_signature(self, signature_id: int, **kwargs) -> Optional[Signature]:
        signature = self.get_by_id(signature_id)
        if not signature:
            return None
        
        for key, value in kwargs.items():
            if hasattr(signature, key) and value is not None:
                setattr(signature, key, value)
        
        self.db.commit()
        self.db.refresh(signature)
        return signature
    
    def delete_signature(self, signature_id: int, user_id: int) -> bool:
        signature = self.get_by_id(signature_id)
        if not signature or signature.user_id != user_id:
            return False
        
        self.db.delete(signature)
        self.db.commit()
        return True 