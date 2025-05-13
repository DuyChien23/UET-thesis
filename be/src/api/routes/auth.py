"""
API routes for user authentication and profile management.
"""

from datetime import timedelta
import uuid
from fastapi import APIRouter, Depends, HTTPException, Body
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_201_CREATED
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.users import UserCreate, UserLogin, Token, UserProfile, UserUpdate, PasswordChange, UserResponse
from src.api.middlewares.auth import create_access_token, get_current_user, authenticate_user, get_current_active_user
from src.db.repositories.users import UserRepository
from src.config.settings import get_settings
from src.utils.password import verify_password, get_password_hash
from src.db.session import get_db_session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserProfile, status_code=HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Register a new user.
    
    Creates a new user account with the provided details.
    """
    user_repo = UserRepository(db)
    
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
    user = await user_repo.create(db, obj_in={
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


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
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
    user_repo = UserRepository(db)
    await user_repo.update_last_login(user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.jwt_expire_minutes * 60
    }


@router.post("/login", response_model=Token)
async def login_user(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db_session)
):
    """
    User login.
    
    Authenticates a user and returns a JWT token.
    """
    user = await authenticate_user(login_data.username, login_data.password, db)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
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
    user_repo = UserRepository(db)
    await user_repo.update_last_login(user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.jwt_expire_minutes * 60
    }


@router.get("/profile", response_model=UserProfile)
async def get_profile(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get current user profile.
    
    Returns the profile information for the authenticated user.
    """
    # Get session and repository
    session = await get_db_session()
    user_repo = UserRepository(session)
    
    user_with_roles = await user_repo.get_user_with_roles(current_user.id)
    
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
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Update user profile.
    
    Updates the profile information for the authenticated user.
    """
    # Use the provided db session
    user_repo = UserRepository(db)
    
    # Prepare update data
    update_dict = {}
    
    if update_data.email is not None:
        # Check if email already exists
        existing_user = await user_repo.get_by_email(update_data.email)
        if existing_user and existing_user.id != current_user.id:
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
    updated_user = await user_repo.update(db=db, id=current_user.id, obj_in=update_dict)
    
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
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Change user password.
    
    Changes the password for the authenticated user.
    """
    # Use the provided db session
    user_repo = UserRepository(db)
    
    # Get the full user object with password hash
    user = await user_repo.get_by_id(current_user.id)
    
    # Verify current password
    if not verify_password(password_data.current_password, user.password_hash):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect current password"
        )
    
    # Update password
    hashed_password = get_password_hash(password_data.new_password)
    
    await user_repo.update(db=db, id=user.id, obj_in={"password_hash": hashed_password})
    
    return {"message": "Password changed successfully"} 