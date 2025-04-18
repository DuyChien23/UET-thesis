from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class KeyPairBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    curve_name: str = Field(..., description="The elliptic curve name (e.g., secp256k1, secp384r1, secp521r1)")

class KeyPairCreate(KeyPairBase):
    user_password: str = Field(..., description="User password to encrypt the private key")

class KeyPair(KeyPairBase):
    id: int
    user_id: int
    public_key: str
    encrypted_private_key: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class KeyPairWithoutPrivate(KeyPairBase):
    id: int
    user_id: int
    public_key: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class KeyPairResponse(KeyPairWithoutPrivate):
    encrypted_private_key: str

class KeyPairPublic(BaseModel):
    id: int
    name: str
    public_key: str
    curve_name: str
    created_at: datetime

    class Config:
        from_attributes = True 