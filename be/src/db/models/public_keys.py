"""
Public key models module.
Contains SQLAlchemy models for public key storage.
"""

from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from ..base import Base


class PublicKey(Base):
    """
    Model for storing public keys.
    """
    
    # Foreign key to user
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Key data and metadata
    key_data = Column(Text, nullable=False)
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Algorithm and curve
    algorithm_name = Column(String(50), nullable=False, index=True)
    curve_name = Column(String(50), nullable=True, index=True)
    
    # Additional metadata
    metadata = Column(JSONB, nullable=True)
    
    # Key fingerprint (for display/quick comparison)
    fingerprint = Column(String(64), nullable=True, unique=True, index=True)
    
    # Relationships
    user = relationship("User", back_populates="public_keys")
    verification_records = relationship("VerificationRecord", back_populates="public_key")
    
    def __repr__(self) -> str:
        name = self.name or f"key-{str(self.id)[:8]}"
        return f"<PublicKey {name} ({self.algorithm_name})>" 