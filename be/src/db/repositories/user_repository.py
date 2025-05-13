from typing import Optional, List, Dict, Any
import uuid
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .base import BaseRepository
from ..models.users import User, Role, Permission, user_roles, role_permissions


class UserRepository(BaseRepository[User]):
    """
    Repository for user operations
    """
    
    def __init__(self):
        super().__init__(User)
    
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            db (AsyncSession): Database session
            username (str): Username to search for
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        query = select(User).where(User.username == username)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            db (AsyncSession): Database session
            email (str): Email to search for
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_active_users(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """
        Get active users with pagination.
        
        Args:
            db (AsyncSession): Database session
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            List[User]: List of active users
        """
        query = select(User).where(User.status == "active").offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_user_with_roles(self, db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        """
        Get a user with their roles.
        
        Args:
            db (AsyncSession): Database session
            user_id (uuid.UUID): User ID
            
        Returns:
            Optional[User]: The user with roles if found, None otherwise
        """
        query = select(User).where(User.id == user_id).options(selectinload(User.roles))
        result = await db.execute(query)
        return result.scalars().first()
    
    async def update_last_login(self, db: AsyncSession, user_id: uuid.UUID) -> None:
        """
        Update a user's last login timestamp.
        
        Args:
            db (AsyncSession): Database session
            user_id (uuid.UUID): User ID
        """
        user = await self.get(db, user_id)
        if user:
            user.last_login = func.now()
            db.add(user)
            await db.commit()
    
    async def add_role_to_user(
        self, 
        db: AsyncSession, 
        user_id: uuid.UUID, 
        role_id: uuid.UUID
    ) -> bool:
        """
        Add a role to a user.
        
        Args:
            db (AsyncSession): Database session
            user_id (uuid.UUID): User ID
            role_id (uuid.UUID): Role ID
            
        Returns:
            bool: True if the role was added, False otherwise
        """
        # Check if user and role exist
        user = await self.get(db, user_id)
        if not user:
            return False
        
        # Get the role
        query = select(Role).where(Role.id == role_id)
        result = await db.execute(query)
        role = result.scalars().first()
        if not role:
            return False
        
        # Check if the role is already assigned
        for user_role in user.roles:
            if user_role.id == role_id:
                return True  # Already assigned
        
        # Add the role
        user.roles.append(role)
        db.add(user)
        await db.commit()
        return True
    
    async def remove_role_from_user(
        self, 
        db: AsyncSession, 
        user_id: uuid.UUID, 
        role_id: uuid.UUID
    ) -> bool:
        """
        Remove a role from a user.
        
        Args:
            db (AsyncSession): Database session
            user_id (uuid.UUID): User ID
            role_id (uuid.UUID): Role ID
            
        Returns:
            bool: True if the role was removed, False otherwise
        """
        # Check if user exists
        user = await self.get_user_with_roles(db, user_id)
        if not user:
            return False
        
        # Remove the role
        removed = False
        for role in user.roles:
            if role.id == role_id:
                user.roles.remove(role)
                removed = True
                break
        
        if removed:
            db.add(user)
            await db.commit()
        
        return removed
    
    async def user_has_permission(
        self, 
        db: AsyncSession, 
        user_id: uuid.UUID, 
        permission_name: str
    ) -> bool:
        """
        Check if a user has a specific permission through any of their roles.
        
        Args:
            db (AsyncSession): Database session
            user_id (uuid.UUID): User ID
            permission_name (str): Permission name to check
            
        Returns:
            bool: True if the user has the permission, False otherwise
        """
        # Query that checks if the user has a role that has the permission
        query = (
            select(func.count())
            .select_from(User)
            .join(user_roles, User.id == user_roles.c.user_id)
            .join(Role, Role.id == user_roles.c.role_id)
            .join(role_permissions, Role.id == role_permissions.c.role_id)
            .join(Permission, Permission.id == role_permissions.c.permission_id)
            .where(
                and_(
                    User.id == user_id,
                    Permission.name == permission_name
                )
            )
        )
        
        result = await db.execute(query)
        count = result.scalar_one()
        return count > 0


class RoleRepository(BaseRepository[Role]):
    """
    Repository for role operations
    """
    
    def __init__(self):
        super().__init__(Role)
    
    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Role]:
        """
        Get a role by name.
        
        Args:
            db (AsyncSession): Database session
            name (str): Role name to search for
            
        Returns:
            Optional[Role]: The role if found, None otherwise
        """
        query = select(Role).where(Role.name == name)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_role_with_permissions(self, db: AsyncSession, role_id: uuid.UUID) -> Optional[Role]:
        """
        Get a role with its permissions.
        
        Args:
            db (AsyncSession): Database session
            role_id (uuid.UUID): Role ID
            
        Returns:
            Optional[Role]: The role with permissions if found, None otherwise
        """
        query = select(Role).where(Role.id == role_id).options(selectinload(Role.permissions))
        result = await db.execute(query)
        return result.scalars().first()
    
    async def add_permission_to_role(
        self, 
        db: AsyncSession, 
        role_id: uuid.UUID, 
        permission_id: uuid.UUID
    ) -> bool:
        """
        Add a permission to a role.
        
        Args:
            db (AsyncSession): Database session
            role_id (uuid.UUID): Role ID
            permission_id (uuid.UUID): Permission ID
            
        Returns:
            bool: True if the permission was added, False otherwise
        """
        # Check if role and permission exist
        role = await self.get_role_with_permissions(db, role_id)
        if not role:
            return False
        
        # Get the permission
        query = select(Permission).where(Permission.id == permission_id)
        result = await db.execute(query)
        permission = result.scalars().first()
        if not permission:
            return False
        
        # Check if the permission is already assigned
        for role_permission in role.permissions:
            if role_permission.id == permission_id:
                return True  # Already assigned
        
        # Add the permission
        role.permissions.append(permission)
        db.add(role)
        await db.commit()
        return True
    
    async def remove_permission_from_role(
        self, 
        db: AsyncSession, 
        role_id: uuid.UUID, 
        permission_id: uuid.UUID
    ) -> bool:
        """
        Remove a permission from a role.
        
        Args:
            db (AsyncSession): Database session
            role_id (uuid.UUID): Role ID
            permission_id (uuid.UUID): Permission ID
            
        Returns:
            bool: True if the permission was removed, False otherwise
        """
        # Check if role exists
        role = await self.get_role_with_permissions(db, role_id)
        if not role:
            return False
        
        # Remove the permission
        removed = False
        for permission in role.permissions:
            if permission.id == permission_id:
                role.permissions.remove(permission)
                removed = True
                break
        
        if removed:
            db.add(role)
            await db.commit()
        
        return removed


class PermissionRepository(BaseRepository[Permission]):
    """
    Repository for permission operations
    """
    
    def __init__(self):
        super().__init__(Permission)
    
    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Permission]:
        """
        Get a permission by name.
        
        Args:
            db (AsyncSession): Database session
            name (str): Permission name to search for
            
        Returns:
            Optional[Permission]: The permission if found, None otherwise
        """
        query = select(Permission).where(Permission.name == name)
        result = await db.execute(query)
        return result.scalars().first() 