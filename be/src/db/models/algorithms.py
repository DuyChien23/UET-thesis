from sqlalchemy import Column, String, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from ..base import Base


class Algorithm(Base):
    """
    Algorithm model for storing crypto algorithm information.
    """
    __tablename__ = "algorithms"
    
    name = Column(String(32), unique=True, nullable=False, index=True)
    type = Column(String(16), nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    curves = relationship("Curve", back_populates="algorithm", cascade="all, delete-orphan")
    public_keys = relationship("PublicKey", back_populates="algorithm")
    verification_records = relationship("VerificationRecord", back_populates="algorithm")
    
    def __repr__(self) -> str:
        return f"<Algorithm {self.name} ({self.id})>"


class Curve(Base):
    """
    Curve model for storing elliptic curve parameters.
    """
    __tablename__ = "curves"
    
    name = Column(String(64), unique=True, nullable=False, index=True)
    algorithm_id = Column(UUID(as_uuid=True), ForeignKey("algorithms.id"), nullable=False)
    parameters = Column(JSONB, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        String(16),
        nullable=False,
        default="enabled",
        server_default="enabled",
    )
    
    # Relationships
    algorithm = relationship("Algorithm", back_populates="curves")
    public_keys = relationship("PublicKey", back_populates="curve")
    verification_records = relationship("VerificationRecord", back_populates="curve")
    
    def __repr__(self) -> str:
        return f"<Curve {self.name} ({self.id})>" 