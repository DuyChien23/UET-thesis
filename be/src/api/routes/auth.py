"""
API routes for user authentication and profile management.
"""

from datetime import timedelta
import uuid
from fastapi import APIRouter, Depends, HTTPException, Body
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_201_CREATED

from src.api.schemas.users import UserCreate, UserLogin, Token, UserProfile, UserUpdate, PasswordChange
from src.api.middlewares.auth import create_access_token, get_current_user
from src.db.repositories.users import UserRepository
from src.config.settings import get_settings
from src.utils.password import verify_password, get_password_hash

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserProfile, status_code=HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    user_repo: UserRepository = Depends()
):
    """
    Register a new user.
    
    Creates a new user account with the provided details.
    """
    # Check if username already exists
    if await user_repo.get_by_username(user_data.username):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if await user_repo.get_by_email(user_data.email):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = get_password_hash(user_data.password)
    
    # Create the user
    user = await user_repo.create({
        "username": user_data.username,
        "email": user_data.email,
        "password_hash": hashed_password,
        "full_name": user_data.full_name,
        "status": "active"
    })
    
    # Add default role
    default_role = await user_repo.get_role_by_name("user")
    if default_role:
        await user_repo.add_role_to_user(user.id, default_role.id)
    
    # Get user with roles
    user_with_roles = await user_repo.get_user_with_roles(user.id)
    
    # Format the response
    return {
        "id": str(user_with_roles.id),
        "username": user_with_roles.username,
        "email": user_with_roles.email,
        "full_name": user_with_roles.full_name,
        "status": user_with_roles.status,
        "roles": [role.name for role in user_with_roles.roles],
        "created_at": user_with_roles.created_at.isoformat(),
        "last_login": user_with_roles.last_login.isoformat() if user_with_roles.last_login else None
    }


@router.post("/login", response_model=Token)
async def login_user(
    login_data: UserLogin,
    user_repo: UserRepository = Depends()
):
    """
    User login.
    
    Authenticates a user and returns a JWT token.
    """
    # Check if user exists
    user = await user_repo.get_by_username(login_data.username)
    if not user:
        # Try email
        user = await user_repo.get_by_email(login_data.username)
        
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Check if user is active
    if user.status != "active":
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    
    # Create access token
    settings = get_settings()
    access_token_expires = timedelta(minutes=settings.jwt_expire_minutes)
    
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    # Update last login
    await user_repo.update_last_login(user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.jwt_expire_minutes * 60
    }


@router.get("/profile", response_model=UserProfile)
async def get_profile(
    user = Depends(get_current_user),
    user_repo: UserRepository = Depends()
):
    """
    Get current user profile.
    
    Returns the profile information for the authenticated user.
    """
    user_with_roles = await user_repo.get_user_with_roles(user.id)
    
    return {
        "id": str(user_with_roles.id),
        "username": user_with_roles.username,
        "email": user_with_roles.email,
        "full_name": user_with_roles.full_name,
        "status": user_with_roles.status,
        "roles": [role.name for role in user_with_roles.roles],
        "created_at": user_with_roles.created_at.isoformat(),
        "last_login": user_with_roles.last_login.isoformat() if user_with_roles.last_login else None
    }


@router.put("/profile", response_model=UserProfile)
async def update_profile(
    update_data: UserUpdate,
    user = Depends(get_current_user),
    user_repo: UserRepository = Depends()
):
    """
    Update user profile.
    
    Updates the profile information for the authenticated user.
    """
    # Prepare update data
    update_dict = {}
    
    if update_data.email is not None:
        # Check if email already exists
        existing_user = await user_repo.get_by_email(update_data.email)
        if existing_user and existing_user.id != user.id:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        update_dict["email"] = update_data.email
    
    if update_data.full_name is not None:
        update_dict["full_name"] = update_data.full_name
    
    if update_data.password is not None:
        update_dict["password_hash"] = get_password_hash(update_data.password)
    
    # Update the user
    updated_user = await user_repo.update(id=user.id, obj_in=update_dict)
    
    if not updated_user:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get user with roles
    user_with_roles = await user_repo.get_user_with_roles(updated_user.id)
    
    # Format the response
    return {
        "id": str(user_with_roles.id),
        "username": user_with_roles.username,
        "email": user_with_roles.email,
        "full_name": user_with_roles.full_name,
        "status": user_with_roles.status,
        "roles": [role.name for role in user_with_roles.roles],
        "created_at": user_with_roles.created_at.isoformat(),
        "last_login": user_with_roles.last_login.isoformat() if user_with_roles.last_login else None
    }


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    user = Depends(get_current_user),
    user_repo: UserRepository = Depends()
):
    """
    Change user password.
    
    Changes the password for the authenticated user.
    """
    # Verify current password
    if not verify_password(password_data.current_password, user.password_hash):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect current password"
        )
    
    # Update password
    hashed_password = get_password_hash(password_data.new_password)
    
    await user_repo.update(id=user.id, obj_in={"password_hash": hashed_password})
    
    return {"message": "Password changed successfully"} 