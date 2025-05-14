from pydantic import BaseModel, Field, UUID4
from typing import Optional, Dict, Any
from datetime import datetime


class SignRequest(BaseModel):
    """Request schema for document signing."""
    document: str = Field(..., description="Base64 encoded document to sign")
    private_key: str = Field(..., description="Base64 encoded private key to use for signing")
    curves_name: str = Field(..., description="Name of the curve to use for signing")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the signing")


class SignResponse(BaseModel):
    """Response schema for document signing."""
    id: str = Field(..., description="Signing record ID")
    document: str = Field(..., description="Base64 encoded document that was signed")
    signature: str = Field(..., description="Base64 encoded signature")
    algorithm_name: str = Field(..., description="Algorithm used for signing")
    curve_name: str = Field(..., description="Curve used for signing")
    signing_time: datetime = Field(..., description="When the signing was performed")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the signing") 