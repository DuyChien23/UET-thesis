from pydantic import BaseModel, Field, UUID4
from typing import Optional, Dict, Any, Union
from datetime import datetime


class VerificationRequest(BaseModel):
    """Request schema for signature verification."""
    document: str = Field(..., description="Document to verify")
    signature: str = Field(..., description="Signature to verify")
    public_key: str = Field(..., description="Public key to use for verification")
    curve_name: str = Field(..., description="Name of the curve to use")
    algorithm_name: str = Field(..., description="Name of the algorithm to use")



class VerificationResponse(BaseModel):
    """Response schema for signature verification."""
    verification: bool = Field(..., description="Whether the signature is valid")
    meta_data: Dict[str, Any] = Field(..., description="Metadata of the verification")


class BatchVerificationRequest(BaseModel):
    """Request schema for batch signature verification."""
    items: list[VerificationRequest] = Field(..., description="List of verification requests to process in batch")


class BatchVerificationResponse(BaseModel):
    """Response schema for batch signature verification."""
    batch_id: UUID4 = Field(..., description="ID of the batch verification")
    total_count: int = Field(..., description="Total number of items in batch")
    success_count: int = Field(..., description="Number of successful verifications")
    results: list[dict] = Field(..., description="Results of the batch verification")
    verification_time: datetime = Field(..., description="When the batch verification was performed") 