"""
API routes for signature verification.
"""

import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Body, Path
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from src.api.schemas.verification import VerificationRequest, VerificationResponse
from src.services.verification import VerificationService
from src.services.public_keys import PublicKeyService
from src.db.session import get_db_session
from src.db.repositories.public_keys import PublicKeyRepository
from src.api.middlewares.auth import get_current_user
from src.api.schemas.users import UserResponse
from src.services import get_verification_service

router = APIRouter(prefix="/verification", tags=["verification"])


@router.post("", response_model=VerificationResponse)
async def verify_signature(
    request: VerificationRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Verify a signature.
    
    Verifies a digital signature using the specified public key and algorithm.
    """
    # Create repository and service instances
    public_key_repo = PublicKeyRepository(db)
    public_key_service = PublicKeyService(public_key_repo)
    verification_service = VerificationService(public_key_service)
    
    # Get the public key
    try:
        public_key = await public_key_service.get_public_key_by_id(request.public_key_id)
        if not public_key:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"Public key with ID {request.public_key_id} not found"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Determine the algorithm to use
    algorithm_name = request.algorithm_name or public_key.algorithm_name
    
    # Verify the signature
    try:
        # Generate a unique ID for this verification
        verification_id = str(uuid.uuid4())
        
        # Call the verification service
        is_valid = await verification_service.verify_signature(
            document_hash=request.document_hash,
            signature=request.signature,
            public_key_id=request.public_key_id,
            algorithm_name=algorithm_name
        )
        
        # Record the verification (if implemented)
        # await verification_service.record_verification(...)
        
        # Return the response
        return {
            "id": verification_id,
            "is_valid": is_valid,
            "document_hash": request.document_hash,
            "public_key_id": request.public_key_id,
            "algorithm_name": algorithm_name,
            "verification_time": datetime.utcnow(),
            "document_id": request.document_id,
            "metadata": request.metadata
        }
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Verification failed: {str(e)}"
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