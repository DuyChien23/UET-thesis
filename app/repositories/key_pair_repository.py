from sqlalchemy.orm import Session
from typing import Optional, List

from app.models.key_pair import KeyPair

class KeyPairRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, key_pair_id: int) -> Optional[KeyPair]:
        return self.db.query(KeyPair).filter(KeyPair.id == key_pair_id).first()
    
    def get_by_user_id(self, user_id: int) -> List[KeyPair]:
        return self.db.query(KeyPair).filter(KeyPair.user_id == user_id).all()
    
    def create_key_pair(self, 
                        user_id: int, 
                        public_key: str, 
                        encrypted_private_key: str, 
                        curve_name: str, 
                        name: str) -> KeyPair:
        key_pair = KeyPair(
            user_id=user_id,
            public_key=public_key,
            encrypted_private_key=encrypted_private_key,
            curve_name=curve_name,
            name=name,
            is_active=True
        )
        self.db.add(key_pair)
        self.db.commit()
        self.db.refresh(key_pair)
        return key_pair
    
    def update_key_pair(self, key_pair_id: int, **kwargs) -> Optional[KeyPair]:
        key_pair = self.get_by_id(key_pair_id)
        if not key_pair:
            return None
        
        for key, value in kwargs.items():
            if hasattr(key_pair, key) and value is not None:
                setattr(key_pair, key, value)
        
        self.db.commit()
        self.db.refresh(key_pair)
        return key_pair
    
    def deactivate_key_pair(self, key_pair_id: int, user_id: int) -> bool:
        key_pair = self.get_by_id(key_pair_id)
        if not key_pair or key_pair.user_id != user_id:
            return False
        
        key_pair.is_active = False
        self.db.commit()
        return True 