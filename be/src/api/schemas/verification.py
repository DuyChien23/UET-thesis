from pydantic import BaseModel, Field, UUID4
from typing import Optional, Dict, Any, Union
from datetime import datetime


class VerificationRequest(BaseModel):
    """Request schema for signature verification."""
    document_hash: str = Field(..., description="Base64 encoded document hash")
    signature: str = Field(..., description="Base64 encoded signature")
    public_key_id: str = Field(..., description="ID of the public key to use")
    algorithm_name: Optional[str] = Field(None, description="Algorithm name (optional, will use the one associated with the key if not provided)")
    document_id: Optional[str] = Field(None, description="ID of the document being verified (for reference)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the verification")


class VerificationResponse(BaseModel):
    """Response schema for signature verification."""
    id: str = Field(..., description="Verification record ID")
    is_valid: bool = Field(..., description="Whether the signature is valid")
    document_hash: str = Field(..., description="Base64 encoded document hash that was verified")
    public_key_id: str = Field(..., description="ID of the public key used")
    algorithm_name: str = Field(..., description="Algorithm used for verification")
    verification_time: datetime = Field(..., description="When the verification was performed")
    document_id: Optional[str] = Field(None, description="ID of the document (if provided)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the verification")


class BatchVerificationRequest(BaseModel):
    """Request schema for batch signature verification."""
    items: list[VerificationRequest] = Field(..., description="List of verification requests to process in batch")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the batch")


class BatchVerificationItem(BaseModel):
    """Schema for an item in a batch verification response."""
    id: str = Field(..., description="Verification record ID")
    is_valid: bool = Field(..., description="Whether the signature is valid")
    document_hash: str = Field(..., description="Base64 encoded document hash that was verified")
    public_key_id: str = Field(..., description="ID of the public key used")
    algorithm_name: str = Field(..., description="Algorithm used for verification")
    document_id: Optional[str] = Field(None, description="ID of the document (if provided)")
    error: Optional[str] = Field(None, description="Error message if verification failed")


class BatchVerificationResponse(BaseModel):
    """Response schema for batch signature verification."""
    id: str = Field(..., description="Batch verification ID")
    verification_time: datetime = Field(..., description="When the batch verification was performed")
    results: list[BatchVerificationItem] = Field(..., description="Results of the batch verification")
    success_count: int = Field(..., description="Number of successful verifications")
    failure_count: int = Field(..., description="Number of failed verifications")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the batch") 