from pydantic import BaseModel, Field, UUID4
from typing import Optional, Dict, Any
from datetime import datetime


class VerificationRequest(BaseModel):
    """Request schema for signature verification."""
    document_hash: str = Field(..., description="Base64 encoded document hash")
    signature: str = Field(..., description="Base64 encoded signature")
    public_key_id: UUID4 = Field(..., description="ID of the public key to use")
    algorithm_name: Optional[str] = Field(None, description="Algorithm name (optional, will use the one associated with the key if not provided)")
    document_id: Optional[str] = Field(None, description="ID of the document being verified (for reference)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the verification")


class VerificationResponse(BaseModel):
    """Response schema for signature verification."""
    success: bool = Field(..., description="Whether the signature is valid")
    verification_id: Optional[str] = Field(None, description="ID of the verification record")
    timestamp: str = Field(..., description="Timestamp of the verification")
    public_key_id: Optional[str] = Field(None, description="ID of the public key used")
    algorithm: Optional[str] = Field(None, description="Algorithm used for verification")
    document_hash: Optional[str] = Field(None, description="Hash of the verified document")
    error: Optional[str] = Field(None, description="Error message if verification failed") 