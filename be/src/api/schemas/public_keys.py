from pydantic import BaseModel, Field, UUID4
from typing import Optional, Dict, Any, List


class PublicKeyCreate(BaseModel):
    """Request schema for creating a public key."""
    key_data: str = Field(..., description="Public key data (PEM or DER encoded)")
    algorithm_name: str = Field(..., description="Algorithm name (ECDSA, EdDSA, RSA)")
    name: Optional[str] = Field(None, description="Name for the key")
    description: Optional[str] = Field(None, description="Description for the key")
    curve_name: Optional[str] = Field(None, description="Curve name for ECC algorithms")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the key")


class PublicKeyResponse(BaseModel):
    """Response schema for public key operations."""
    id: str = Field(..., description="Public key ID")
    name: Optional[str] = Field(None, description="Name for the key")
    description: Optional[str] = Field(None, description="Description for the key")
    algorithm_name: str = Field(..., description="Algorithm name")
    curve_name: Optional[str] = Field(None, description="Curve name for ECC algorithms")
    user_id: str = Field(..., description="ID of the user who owns the key")
    created_at: str = Field(..., description="Timestamp when the key was created")
    updated_at: Optional[str] = Field(None, description="Timestamp when the key was last updated")
    key_fingerprint: str = Field(..., description="Fingerprint of the public key")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the key")


class PublicKeyList(BaseModel):
    """Response schema for listing public keys."""
    items: List[PublicKeyResponse] = Field(..., description="List of public keys")
    count: int = Field(..., description="Total number of keys")
    

class PublicKeyDelete(BaseModel):
    """Response schema for deleting a public key."""
    success: bool = Field(..., description="Whether the key was deleted successfully")
    message: str = Field(..., description="Status message") 