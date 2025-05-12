"""
User models module.
Contains SQLAlchemy models for user management with roles and permissions.
"""

from sqlalchemy import Column, String, ForeignKey, Table, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from ..base import Base, UUID


# Association table for user roles
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", UUID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUID, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
)

# Association table for role permissions
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", UUID, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", UUID, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
)


class User(Base):
    """
    User model.
    """
    __tablename__ = "users"
    
    # Authentication
    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile
    full_name = Column(String(100), nullable=True)
    status = Column(String(20), nullable=False, default="active", server_default="active", index=True)
    
    # Tracking
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    public_keys = relationship("PublicKey", back_populates="user", cascade="all, delete-orphan")
    verification_records = relationship("VerificationRecord", back_populates="user")
    
    def __repr__(self) -> str:
        return f"<User {self.username} ({str(self.id)[:8]})>"


class Role(Base):
    """
    Role model for authorization.
    """
    __tablename__ = "roles"
    
    name = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(String(255), nullable=True)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    
    def __repr__(self) -> str:
        return f"<Role {self.name}>"


class Permission(Base):
    """
    Permission model for fine-grained authorization.
    """
    __tablename__ = "permissions"
    
    name = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(String(255), nullable=True)
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
    
    def __repr__(self) -> str:
        return f"<Permission {self.name}>" 