from typing import Optional, List, Dict, Any
import uuid
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.repositories.base import BaseRepository
from src.db.models.users import User, Role, Permission, user_roles, role_permissions


class UserRepository(BaseRepository[User]):
    """
    Repository for user operations
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize the repository.
        
        Args:
            db_session (AsyncSession): Database session
        """
        super().__init__(User)
        self.db = db_session
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            username (str): Username to search for
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        query = select(User).where(User.username == username)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_role_by_name(self, role_name: str) -> Optional[Role]:
        """
        Get a role by name.
        
        Args:
            role_name (str): Role name to search for
            
        Returns:
            Optional[Role]: The role if found, None otherwise
        """
        query = select(Role).where(Role.name == role_name)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            email (str): Email to search for
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_active_users(
        self, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """
        Get active users with pagination.
        
        Args:
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            List[User]: List of active users
        """
        query = select(User).where(User.status == "active").offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_user_with_roles(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Get a user with their roles.
        
        Args:
            user_id (uuid.UUID): User ID
            
        Returns:
            Optional[User]: The user with roles if found, None otherwise
        """
        query = select(User).where(User.id == user_id).options(selectinload(User.roles))
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def update_last_login(self, user_id: uuid.UUID) -> None:
        """
        Update a user's last login timestamp.
        
        Args:
            user_id (uuid.UUID): User ID
        """
        user = await self.get(self.db, user_id)
        if user:
            user.last_login = func.now()
            self.db.add(user)
            await self.db.commit()
    
    async def add_role_to_user(
        self, 
        user_id: uuid.UUID, 
        role_id: uuid.UUID
    ) -> bool:
        """
        Add a role to a user.
        
        Args:
            user_id (uuid.UUID): User ID
            role_id (uuid.UUID): Role ID
            
        Returns:
            bool: True if the role was added, False otherwise
        """
        # Check if user and role exist
        user = await self.get(self.db, user_id)
        if not user:
            return False
        
        # Get the role
        query = select(Role).where(Role.id == role_id)
        result = await self.db.execute(query)
        role = result.scalars().first()
        if not role:
            return False
        
        # Check if the role is already assigned
        for user_role in user.roles:
            if user_role.id == role_id:
                return True  # Already assigned
        
        # Add the role
        user.roles.append(role)
        self.db.add(user)
        await self.db.commit()
        return True
    
    async def remove_role_from_user(
        self, 
        user_id: uuid.UUID, 
        role_id: uuid.UUID
    ) -> bool:
        """
        Remove a role from a user.
        
        Args:
            user_id (uuid.UUID): User ID
            role_id (uuid.UUID): Role ID
            
        Returns:
            bool: True if the role was removed, False otherwise
        """
        # Check if user exists
        user = await self.get_user_with_roles(user_id)
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
            self.db.add(user)
            await self.db.commit()
        
        return removed
    
    async def user_has_permission(
        self, 
        user_id: uuid.UUID, 
        permission_name: str
    ) -> bool:
        """
        Check if a user has a specific permission through any of their roles.
        
        Args:
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
        
        result = await self.db.execute(query)
        count = result.scalar_one()
        return count > 0
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id (str): The user ID
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            return None
        
        query = select(User).where(User.id == user_uuid)
        result = await self.db.execute(query)
        return result.scalars().first()


class RoleRepository(BaseRepository[Role]):
    """
    Repository for role operations
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize the repository.
        
        Args:
            db_session (AsyncSession): Database session
        """
        super().__init__(Role)
        self.db = db_session
    
    async def get_by_name(self, name: str) -> Optional[Role]:
        """
        Get a role by name.
        
        Args:
            name (str): Role name to search for
            
        Returns:
            Optional[Role]: The role if found, None otherwise
        """
        query = select(Role).where(Role.name == name)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_role_with_permissions(self, role_id: uuid.UUID) -> Optional[Role]:
        """
        Get a role with its permissions.
        
        Args:
            role_id (uuid.UUID): Role ID
            
        Returns:
            Optional[Role]: The role with permissions if found, None otherwise
        """
        query = select(Role).where(Role.id == role_id).options(selectinload(Role.permissions))
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def add_permission_to_role(
        self, 
        role_id: uuid.UUID, 
        permission_id: uuid.UUID
    ) -> bool:
        """
        Add a permission to a role.
        
        Args:
            role_id (uuid.UUID): Role ID
            permission_id (uuid.UUID): Permission ID
            
        Returns:
            bool: True if the permission was added, False otherwise
        """
        # Check if role and permission exist
        role = await self.get_role_with_permissions(role_id)
        if not role:
            return False
        
        # Get the permission
        query = select(Permission).where(Permission.id == permission_id)
        result = await self.db.execute(query)
        permission = result.scalars().first()
        if not permission:
            return False
        
        # Check if the permission is already assigned
        for role_permission in role.permissions:
            if role_permission.id == permission_id:
                return True  # Already assigned
        
        # Add the permission
        role.permissions.append(permission)
        self.db.add(role)
        await self.db.commit()
        return True
    
    async def remove_permission_from_role(
        self, 
        role_id: uuid.UUID, 
        permission_id: uuid.UUID
    ) -> bool:
        """
        Remove a permission from a role.
        
        Args:
            role_id (uuid.UUID): Role ID
            permission_id (uuid.UUID): Permission ID
            
        Returns:
            bool: True if the permission was removed, False otherwise
        """
        # Check if role exists
        role = await self.get_role_with_permissions(role_id)
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
            self.db.add(role)
            await self.db.commit()
        
        return removed


class PermissionRepository(BaseRepository[Permission]):
    """
    Repository for permission operations
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize the repository.
        
        Args:
            db_session (AsyncSession): Database session
        """
        super().__init__(Permission)
        self.db = db_session
    
    async def get_by_name(self, name: str) -> Optional[Permission]:
        """
        Get a permission by name.
        
        Args:
            name (str): Permission name to search for
            
        Returns:
            Optional[Permission]: The permission if found, None otherwise
        """
        query = select(Permission).where(Permission.name == name)
        result = await self.db.execute(query)
        return result.scalars().first() 