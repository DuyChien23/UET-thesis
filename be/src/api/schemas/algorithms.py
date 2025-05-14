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
    algorithm_id: str = Field("", description="Algorithm ID this curve belongs to")
    algorithm_name: Optional[str] = Field(None, description="Algorithm name")
    description: Optional[str] = Field(None, description="Description of the curve")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Curve parameters")
    status: str = Field("enabled", description="Curve status (enabled or disabled)")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    
    class Config:
        orm_mode = True


class CurveList(BaseModel):
    """Schema for list of curves."""
    curves: List[CurveInfo] = Field(..., description="List of available curves")
    count: int = Field(..., description="Total number of curves")


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


class AlgorithmCreate(BaseModel):
    """Schema for creating a new algorithm."""
    name: str = Field(..., description="Algorithm name")
    type: str = Field(..., description="Algorithm type")
    description: Optional[str] = Field(None, description="Description of the algorithm")
    is_default: bool = Field(False, description="Whether this is the default algorithm")


class AlgorithmUpdate(BaseModel):
    """Schema for updating an existing algorithm."""
    name: Optional[str] = Field(None, description="Algorithm name")
    type: Optional[str] = Field(None, description="Algorithm type")
    description: Optional[str] = Field(None, description="Description of the algorithm")
    is_default: Optional[bool] = Field(None, description="Whether this is the default algorithm")
    status: Optional[str] = Field(None, description="Status of the algorithm (enabled/disabled)")


class CurveCreate(BaseModel):
    """Schema for creating a new curve."""
    name: str = Field(..., description="Curve name")
    algorithm_id: str = Field(..., description="ID of the algorithm this curve belongs to")
    description: Optional[str] = Field(None, description="Description of the curve")
    parameters: Dict[str, Any] = Field(..., description="Curve parameters")


class CurveUpdate(BaseModel):
    """Schema for updating an existing curve."""
    name: Optional[str] = Field(None, description="Curve name")
    description: Optional[str] = Field(None, description="Description of the curve")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Curve parameters")
    status: Optional[str] = Field(None, description="Status of the curve (enabled/disabled)") 