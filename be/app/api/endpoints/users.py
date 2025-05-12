from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from typing import List

from app.schemas.user import UserCreate, UserResponse, UserLogin, TokenResponse
from app.services.user_service import UserService
from app.db.database import get_db
from app.services.auth_service import get_current_user, get_current_user_from_token
from app.models.user import User

router = APIRouter()

@router.post(
    "/register", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new user account with the provided username, email, and password. The password is hashed before storage."
)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    try:
        return service.create_user(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/login", 
    response_model=TokenResponse,
    summary="User login",
    description="Authenticates a user with username and password, returning a JWT token that can be used for authorized API requests."
)
def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    service = UserService(db)
    try:
        return service.authenticate_user(user_credentials)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get(
    "/me", 
    response_model=UserResponse,
    summary="Get current user",
    description="Returns the authenticated user's information using token authentication."
)
async def get_user_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get(
    "/me-token", 
    response_model=UserResponse,
    summary="Get user with token only",
    description="Returns the authenticated user's information using direct token authentication. Provide just the token in the Authorization header."
)
async def get_user_me_token(current_user: User = Depends(get_current_user_from_token)):
    return current_user 