from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union


class CurveParameters(BaseModel):
    """Schema for curve parameters."""
    bit_size: Optional[int] = Field(None, description="Bit size of the curve")
    hash_algorithm: Optional[str] = Field(None, description="Hash algorithm")
    
    class Config:
        extra = "allow"  # Allow additional fields


class CurveInfo(BaseModel):
    """Schema for curve information."""
    id: str = Field(..., description="Curve ID")
    name: str = Field(..., description="Curve name")
    description: Optional[str] = Field(None, description="Description of the curve")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Curve parameters")
    
    class Config:
        orm_mode = True


class AlgorithmInfo(BaseModel):
    """Schema for algorithm information."""
    id: str = Field(..., description="Algorithm ID")
    name: str = Field(..., description="Algorithm name")
    type: str = Field(..., description="Algorithm type")
    description: Optional[str] = Field(None, description="Description of the algorithm")
    is_default: bool = Field(False, description="Whether this is the default algorithm")
    status: str = Field("enabled", description="Status of the algorithm")
    curves: List[CurveInfo] = Field([], description="List of supported curves")
    
    class Config:
        orm_mode = True


class AlgorithmList(BaseModel):
    """Schema for listing algorithms."""
    items: List[AlgorithmInfo] = Field(..., description="List of algorithms")
    count: int = Field(..., description="Total number of algorithms")
    
    class Config:
        orm_mode = True 