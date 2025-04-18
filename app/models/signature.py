from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, LargeBinary
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Signature(Base):
    __tablename__ = "signatures"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    key_pair_id = Column(Integer, ForeignKey("key_pairs.id", ondelete="CASCADE"))
    # Base64 encoded signature
    signature = Column(Text, nullable=False)
    # Hash of the original data
    data_hash = Column(String, nullable=False, index=True)
    # Original data can be large, so we store it optionally
    original_data = Column(Text, nullable=True)
    # Store content type to help verify appropriate data
    content_type = Column(String, nullable=False)
    # Optional file name if signing a file
    file_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")
    key_pair = relationship("KeyPair") 