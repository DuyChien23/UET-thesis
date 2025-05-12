from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class CurveInfo(BaseModel):
    """Schema for curve information."""
    name: str = Field(..., description="Curve name")
    bit_size: Optional[int] = Field(None, description="Bit size of the curve")
    description: Optional[str] = Field(None, description="Description of the curve")


class AlgorithmInfo(BaseModel):
    """Schema for algorithm information."""
    name: str = Field(..., description="Algorithm name")
    type: str = Field(..., description="Algorithm type")
    is_default: bool = Field(..., description="Whether this is the default algorithm")
    curves: List[CurveInfo] = Field(..., description="List of supported curves")
    supported_key_formats: List[str] = Field(..., description="List of supported key formats")


class AlgorithmList(BaseModel):
    """Schema for listing algorithms."""
    items: List[AlgorithmInfo] = Field(..., description="List of algorithms")
    count: int = Field(..., description="Total number of algorithms") 