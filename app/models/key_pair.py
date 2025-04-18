from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class KeyPair(Base):
    __tablename__ = "key_pairs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    public_key = Column(Text, nullable=False)
    # Store encrypted private key
    encrypted_private_key = Column(Text, nullable=False)
    # Curve used for this key pair (e.g., secp256k1, secp384r1, secp521r1)
    curve_name = Column(String, nullable=False)
    name = Column(String, nullable=False)  # A name for the key pair
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    user = relationship("User", back_populates="key_pairs") 