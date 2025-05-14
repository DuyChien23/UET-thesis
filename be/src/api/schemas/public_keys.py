from pydantic import BaseModel, Field, UUID4
from typing import Optional, Dict, Any, List
from datetime import datetime


class PublicKeyBase(BaseModel):
    """Base schema for public key data."""
    algorithm_name: str = Field(..., description="Algorithm name for this key")
    curve_name: str = Field(..., description="Curve name for this key")
    key_data: str = Field(..., description="The base64-encoded public key data")
    name: Optional[str] = Field(None, description="A friendly name for this key")
    description: Optional[str] = Field(None, description="A description of this key")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the key")


class PublicKeyCreate(PublicKeyBase):
    """Schema for creating a new public key."""
    pass


class PublicKeyUpdate(BaseModel):
    """Schema for updating a public key."""
    name: Optional[str] = Field(None, description="A friendly name for this key")
    description: Optional[str] = Field(None, description="A description of this key")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the key")
    is_active: Optional[bool] = Field(None, description="Whether this key is active")


class PublicKeyInDB(PublicKeyBase):
    """Schema for a public key as stored in the database."""
    id: str = Field(..., description="Unique ID for the public key")
    user_id: str = Field(..., description="ID of the user who owns this key")
    is_active: bool = Field(..., description="Whether this key is active")
    created_at: datetime = Field(..., description="When this key was created")
    updated_at: Optional[datetime] = Field(None, description="When this key was last updated")

    class Config:
        orm_mode = True


class PublicKeyResponse(PublicKeyInDB):
    """Schema for returning a public key."""
    pass


class PublicKeyList(BaseModel):
    """Schema for returning a list of public keys."""
    keys: List[PublicKeyResponse] = Field(..., description="List of public keys")
    total: int = Field(..., description="Total number of keys matching the query")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")


class PublicKeyDetail(PublicKeyResponse):
    """Schema for returning a detailed view of a public key."""
    algorithm_name: str = Field(..., description="Name of the algorithm for this key")
    algorithm_type: str = Field(..., description="Type of the algorithm for this key")
    curve_details: Dict[str, Any] = Field(..., description="Details about the curve or key type")


class PublicKeyDelete(BaseModel):
    """Response schema for deleting a public key."""
    success: bool = Field(..., description="Whether the key was deleted successfully")
    message: str = Field(..., description="Status message") 