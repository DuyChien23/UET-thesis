"""
API routes for public key management.
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_201_CREATED

from src.api.schemas.public_keys import PublicKeyCreate, PublicKeyResponse, PublicKeyList, PublicKeyDelete, PublicKeyUpdate
from src.services import get_public_key_service
from src.api.middlewares.auth import get_current_user, has_permission
from src.api.schemas.users import UserResponse

router = APIRouter(prefix="/public-keys", tags=["public-keys"])


@router.post("/", response_model=PublicKeyResponse, status_code=HTTP_201_CREATED)
async def create_public_key(
    request: PublicKeyCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a new public key.
    
    Registers a new public key in the system, associated with the current user.
    """
    public_key_service = get_public_key_service()
    
    try:
        result = await public_key_service.create_public_key(
            key_data=request.key_data,
            algorithm_id=request.algorithm_name,
            user_id=str(current_user.id),
            curve=request.curve_name,
            name=request.name,
            description=request.description,
            metadata=request.metadata
        )
        
        # Transform response to match expected schema
        from datetime import datetime
        
        # Ensure metadata is a valid dictionary
        metadata = result.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}
        
        response = {
            "id": result["id"],
            "user_id": result["user_id"],
            "algorithm_name": result["algorithm_name"],
            "curve_name": result["curve_name"],
            "key_data": result.get("key_data", ""),
            "name": result["name"],
            "description": result["description"],
            "metadata": metadata,
            "created_at": result.get("created_at", datetime.now().isoformat()),
            "updated_at": result.get("updated_at"),
            "is_active": result.get("is_active", True)
        }
        
        return response
    
    except ValueError as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{key_id}", response_model=PublicKeyResponse)
async def get_public_key(
    key_id: str = Path(..., description="The public key ID"),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get a public key by ID.
    
    Retrieves public key details by its ID.
    """
    public_key_service = get_public_key_service()
    
    key = await public_key_service.get_public_key(key_id)
    
    if not key:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Public key not found"
        )
    
    return key


@router.get("/", response_model=PublicKeyList)
async def get_user_public_keys(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get all public keys for the current user.
    
    Lists all public keys associated with the current user.
    """
    public_key_service = get_public_key_service()
    
    keys = await public_key_service.get_user_public_keys(str(current_user.id))
    
    # Ensure each key has the required fields
    for key in keys:
        # Add missing fields if needed
        if "key_data" not in key:
            key["key_data"] = ""  # Empty string for security
        if "is_active" not in key:
            key["is_active"] = True  # Default to active
    
    return {
        "keys": keys,
        "total": len(keys),
        "page": 1,
        "size": len(keys),
        "pages": 1
    }


@router.put("/{key_id}", response_model=PublicKeyResponse)
async def update_public_key(
    key_id: str = Path(..., description="The public key ID"),
    request: PublicKeyUpdate = ...,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Update a public key.
    
    Updates a public key owned by the current user.
    Only name, description, and metadata can be updated.
    """
    public_key_service = get_public_key_service()
    
    try:
        # Get the key first to check ownership
        existing_key = await public_key_service.get_public_key(key_id)
        
        if not existing_key:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Public key not found"
            )
        
        # Check ownership
        if str(existing_key.get('user_id')) != str(current_user.id):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="You don't own this public key"
            )
        
        # Update the key
        updated_key = await public_key_service.update_public_key(
            key_id=key_id,
            name=request.name,
            description=request.description,
            metadata=request.metadata
        )
        
        return updated_key
        
    except ValueError as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{key_id}", response_model=PublicKeyDelete)
async def delete_public_key(
    key_id: str = Path(..., description="The public key ID"),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Delete a public key.
    
    Deletes a public key owned by the current user.
    """
    public_key_service = get_public_key_service()
    
    try:
        success = await public_key_service.delete_public_key(key_id, str(current_user.id))
        
        if not success:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Public key not found"
            )
        
        return {
            "success": True,
            "message": "Public key deleted successfully"
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 