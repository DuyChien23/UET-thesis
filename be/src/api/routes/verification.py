"""
API routes for digital signature verification.
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from src.api.schemas.verification import VerificationRequest, VerificationResponse
from src.services import get_verification_service
from src.api.middlewares.auth import get_current_user
from src.api.schemas.users import UserResponse

router = APIRouter(prefix="/verification", tags=["verification"])


@router.post("/", response_model=VerificationResponse)
async def verify_signature(
    request: VerificationRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Verify a digital signature.
    
    Verifies that a signature is valid for a given document hash using the specified public key.
    """
    verification_service = get_verification_service()
    
    try:
        result = await verification_service.verify_signature(
            document_hash=request.document_hash,
            signature=request.signature,
            public_key_id=str(request.public_key_id),
            algorithm_name=request.algorithm_name,
            user_id=str(current_user.id),
            document_id=request.document_id,
            metadata=request.metadata
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{verification_id}", response_model=VerificationResponse)
async def get_verification(
    verification_id: str = Path(..., description="The verification record ID"),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get a verification record by ID.
    
    Retrieves a previously performed verification record by its ID.
    """
    verification_service = get_verification_service()
    
    result = await verification_service.get_verification_by_id(verification_id)
    
    if not result:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Verification record not found"
        )
    
    return result 