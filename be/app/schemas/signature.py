from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SignatureBase(BaseModel):
    data_hash: str
    content_type: str
    file_name: Optional[str] = None

class SignatureCreate(SignatureBase):
    signature: str
    original_data: Optional[str] = None
    key_pair_id: int

class Signature(SignatureBase):
    id: int
    user_id: int
    key_pair_id: int
    signature: str
    original_data: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SignatureResponse(SignatureBase):
    id: int
    user_id: int
    key_pair_id: int
    signature: str
    original_data: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SignatureVerify(BaseModel):
    signature: str
    data: str
    public_key: str
    curve_name: str = "secp521r1"

class VerificationResponse(BaseModel):
    is_valid: bool 