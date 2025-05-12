"""
API routes for public key management.
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_201_CREATED

from api.schemas.public_keys import PublicKeyCreate, PublicKeyResponse, PublicKeyList, PublicKeyDelete
from services import get_public_key_service
from api.middlewares.auth import get_current_user, has_permission

router = APIRouter(prefix="/public-keys", tags=["public-keys"])


@router.post("/", response_model=PublicKeyResponse, status_code=HTTP_201_CREATED)
async def create_public_key(
    request: PublicKeyCreate,
    user = Depends(get_current_user)
):
    """
    Create a new public key.
    
    Registers a new public key in the system, associated with the current user.
    """
    public_key_service = get_public_key_service()
    
    try:
        result = await public_key_service.create_public_key(
            key_data=request.key_data,
            algorithm_name=request.algorithm_name,
            user_id=str(user.id),
            name=request.name,
            description=request.description,
            curve_name=request.curve_name,
            metadata=request.metadata
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{key_id}", response_model=PublicKeyResponse)
async def get_public_key(
    key_id: str = Path(..., description="The public key ID"),
    user = Depends(get_current_user)
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
    user = Depends(get_current_user)
):
    """
    Get all public keys for the current user.
    
    Lists all public keys associated with the current user.
    """
    public_key_service = get_public_key_service()
    
    keys = await public_key_service.get_user_public_keys(str(user.id))
    
    return {
        "items": keys,
        "count": len(keys)
    }


@router.delete("/{key_id}", response_model=PublicKeyDelete)
async def delete_public_key(
    key_id: str = Path(..., description="The public key ID"),
    user = Depends(get_current_user)
):
    """
    Delete a public key.
    
    Deletes a public key owned by the current user.
    """
    public_key_service = get_public_key_service()
    
    try:
        success = await public_key_service.delete_public_key(key_id, str(user.id))
        
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