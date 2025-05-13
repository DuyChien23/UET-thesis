"""
Public key models module.
Contains SQLAlchemy models for public key storage.
"""

from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from ..base import Base, UUID, JSONB


class PublicKey(Base):
    """
    Model for storing public keys.
    """
    __tablename__ = "public_keys"
    
    # Foreign key to user
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False, index=True)
    
    # Key data and metadata
    key_data = Column(Text, nullable=False)
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Algorithm and curve
    algorithm_name = Column(String(50), ForeignKey("algorithms.name"), nullable=False, index=True)
    curve_name = Column(String(50), ForeignKey("curves.name"), nullable=True, index=True)
    
    # Additional metadata
    key_metadata = Column(JSONB, nullable=True)
    
    # Key fingerprint (for display/quick comparison)
    fingerprint = Column(String(64), nullable=True, unique=True, index=True)
    
    # Relationships
    user = relationship("User", back_populates="public_keys")
    algorithm = relationship("Algorithm", back_populates="public_keys")
    curve = relationship("Curve", back_populates="public_keys")
    verification_records = relationship("VerificationRecord", back_populates="public_key")
    
    def __repr__(self) -> str:
        name = self.name or f"key-{str(self.id)[:8]}"
        return f"<PublicKey {name} ({self.algorithm_name})>" 