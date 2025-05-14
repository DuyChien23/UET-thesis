from pydantic import BaseModel, Field, UUID4
from typing import Optional, Dict, Any
from datetime import datetime


class SignRequest(BaseModel):
    """Request schema for document signing."""
    document: str = Field(..., description="Document to sign")
    private_key: str = Field(..., description="Private key to use for signing")
    curve_name: str = Field(..., description="Name of the curve to use")


class SignResponse(BaseModel):
    """Response schema for document signing."""
    signature: str = Field(..., description="Generated signature")
    document_hash: str = Field(..., description="Hash of the signed document")
    signing_id: UUID4 = Field(..., description="ID of the signing record")
    signing_time: datetime = Field(..., description="When the signing was performed") 