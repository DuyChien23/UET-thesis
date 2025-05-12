"""
Verification models module.
Contains SQLAlchemy models for storing verification records.
"""

from sqlalchemy import Column, String, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from enum import Enum, auto
from datetime import datetime

from ..base import Base


class VerificationStatus(str, Enum):
    """
    Enumeration for verification status.
    """
    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"


class VerificationRecord(Base):
    """
    Model for storing signature verification records.
    """
    
    # User and document references
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    document_id = Column(String(255), nullable=True, index=True)
    
    # Verification details
    document_hash = Column(String(255), nullable=False, index=True)
    signature = Column(Text, nullable=False)
    
    # Algorithm information
    algorithm_name = Column(String(50), nullable=False, index=True)
    
    # Public key reference
    public_key_id = Column(UUID(as_uuid=True), ForeignKey("public_keys.id"), nullable=False, index=True)
    
    # Verification result
    status = Column(String(16), nullable=False, index=True)
    verified_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Additional data
    metadata = Column(JSONB, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="verification_records")
    public_key = relationship("PublicKey", back_populates="verification_records")
    
    def __repr__(self) -> str:
        result = "valid" if self.status == VerificationStatus.SUCCESS else "invalid"
        return f"<VerificationRecord {result} ({str(self.id)[:8]})>"


class BatchVerification(Base):
    """
    Model for storing batch verification records.
    """
    __tablename__ = "batch_verifications"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    total_count = Column(Integer, nullable=False)
    success_count = Column(Integer, nullable=False)
    metadata = Column(JSONB, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="batch_verifications")
    items = relationship("BatchVerificationItem", back_populates="batch", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<BatchVerification {self.success_count}/{self.total_count} ({self.id})>"
    
    @property
    def success_rate(self) -> float:
        """
        Calculate the success rate of the batch verification.
        
        Returns:
            float: Success rate as a percentage
        """
        if self.total_count == 0:
            return 0.0
        
        return (self.success_count / self.total_count) * 100


class BatchVerificationItem(Base):
    """
    Model for storing items in a batch verification.
    """
    __tablename__ = "batch_verification_items"
    
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batch_verifications.id", ondelete="CASCADE"), nullable=False)
    verification_record_id = Column(UUID(as_uuid=True), ForeignKey("verification_records.id"), nullable=False)
    item_index = Column(Integer, nullable=False)
    
    # Relationships
    batch = relationship("BatchVerification", back_populates="items")
    verification_record = relationship("VerificationRecord", back_populates="batch_items")
    
    def __repr__(self) -> str:
        return f"<BatchVerificationItem {self.item_index} ({self.id})>"
    
    class Meta:
        constraints = [
            {'name': 'uq_batch_index', 'type': 'unique', 'columns': ['batch_id', 'item_index']}
        ] 