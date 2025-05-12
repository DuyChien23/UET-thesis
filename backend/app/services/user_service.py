from sqlalchemy.orm import Session
from app.repositories import user as user_repo
from app.schemas.user import UserCreate, UserUpdate, User, UserLogin
from typing import List, Optional
from fastapi import HTTPException, status
from datetime import timedelta
from app.repositories.user_repository import UserRepository
from app.services.auth_service import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

def get_user(db: Session, user_id: int) -> User:
    db_user = user_repo.get_user(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return user_repo.get_users(db, skip, limit)

def create_user(db: Session, user: UserCreate) -> User:
    # Check if username exists
    if user_repo.get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    if user_repo.get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    return user_repo.create_user(db, user)

def update_user(db: Session, user_id: int, user: UserUpdate) -> User:
    db_user = user_repo.update_user(db, user_id, user)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    result = user_repo.delete_user(db, user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return result

class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)
    
    def create_user(self, user: UserCreate):
        # Check if username or email already exists
        if self.repository.get_by_username(user.username):
            raise ValueError("Username already registered")
        if self.repository.get_by_email(user.email):
            raise ValueError("Email already registered")
        
        # Hash the password
        hashed_password = get_password_hash(user.password)
        
        # Create new user
        return self.repository.create_user(user.username, user.email, hashed_password)
    
    def authenticate_user(self, user_credentials: UserLogin):
        user = self.repository.get_by_username(user_credentials.username)
        if not user:
            raise ValueError("Incorrect username or password")
        if not verify_password(user_credentials.password, user.hashed_password):
            raise ValueError("Incorrect username or password")
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {"access_token": access_token, "token_type": "bearer"} 