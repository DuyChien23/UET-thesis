"""
Authentication middleware for the API.
Implements JWT-based authentication and authorization.
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List, Union

from jose import jwt, JWTError
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from src.config.settings import get_settings
from src.db.repositories.users import UserRepository


# Security scheme for API authorization
security = HTTPBearer()


def create_access_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data (Dict[str, Any]): Data to encode in the token
        expires_delta (Optional[timedelta]): Token expiration time
        
    Returns:
        str: The encoded JWT token
    """
    settings = get_settings()
    
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    
    to_encode.update({"exp": expire.timestamp(), "iat": datetime.utcnow().timestamp()})
    
    return jwt.encode(
        to_encode, 
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode a JWT token.
    
    Args:
        token (str): The JWT token to decode
        
    Returns:
        Dict[str, Any]: The decoded token data
        
    Raises:
        HTTPException: If the token is invalid or expired
    """
    settings = get_settings()
    
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except JWTError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    user_repo: UserRepository = Depends()
):
    """
    Get the current authenticated user.
    
    Args:
        credentials (HTTPAuthorizationCredentials): The authentication credentials
        user_repo (UserRepository): The user repository
        
    Returns:
        The authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    token_data = decode_token(credentials.credentials)
    
    if not token_data or "sub" not in token_data:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = await user_repo.get_by_id(token_data["sub"])
    
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user


def has_permission(required_permission: str):
    """
    Dependency to check if the user has a specific permission.
    
    Args:
        required_permission (str): The required permission
        
    Returns:
        A dependency function that checks the permission
    """
    async def permission_checker(
        user = Depends(get_current_user),
        user_repo: UserRepository = Depends()
    ):
        has_perm = await user_repo.user_has_permission(user.id, required_permission)
        
        if not has_perm:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        return user
    
    return permission_checker 