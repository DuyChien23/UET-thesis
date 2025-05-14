"""
API routes for signature verification.
"""

import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Body, Path
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from src.api.schemas.verification import VerificationRequest, VerificationResponse, BatchVerificationRequest, BatchVerificationResponse
from src.services.verification import VerificationService
from src.services.public_keys import PublicKeyService
from src.db.session import get_db_session
from src.db.repositories.public_keys import PublicKeyRepository
from src.api.middlewares.auth import get_current_user
from src.api.schemas.users import UserResponse
from src.services import get_verification_service

router = APIRouter(prefix="/verify", tags=["verification"])


@router.post("", response_model=VerificationResponse)
async def verify_signature(
    request: VerificationRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Verify a signature.
    
    Verifies a digital signature using the specified public key and curve.
    """
    verification_service = get_verification_service()
    
    try:
        # Generate a unique ID for this verification
        verification_id = uuid.uuid4()
        
        # Call the verification service
        result = await verification_service.verify_signature(
            document=request.document,
            signature=request.signature,
            public_key=request.public_key,
            algorithm_name=request.algorithm_name,
            curve_name=request.curve_name
        )
        
        return {
            "verification": result[0],
            "meta_data": result[1]
        }
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Verification failed: {str(e)}"
        )


@router.post("/batch", response_model=BatchVerificationResponse)
async def verify_signatures_batch(
    request: BatchVerificationRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Verify multiple signatures in batch.
    
    Verifies multiple digital signatures using the specified public keys and curves.
    """
    verification_service = get_verification_service()
    
    try:
        # Generate a unique ID for this batch verification
        batch_id = uuid.uuid4()
        
        # Process all items in batch
        results = []
        success_count = 0
        
        for item in request.items:
            try:
                result = await verification_service.verify_signature(
                    document=item.document,
                    signature=item.signature,
                    public_key=item.public_key,
                    curve_name=item.curve_name
                )
                
                results.append({
                    "index": len(results),
                    "is_valid": result["is_valid"],
                    "verification_id": uuid.uuid4()
                })
                
                if result["is_valid"]:
                    success_count += 1
                    
            except Exception as e:
                results.append({
                    "index": len(results),
                    "is_valid": False,
                    "verification_id": uuid.uuid4(),
                    "error": str(e)
                })
        
        # Return the response
        return {
            "batch_id": batch_id,
            "total_count": len(request.items),
            "success_count": success_count,
            "results": results,
            "verification_time": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Batch verification failed: {str(e)}"
        )


@router.get("/{verification_id}", response_model=VerificationResponse)
async def get_verification(
    verification_id: UUID4 = Path(..., description="The verification record ID"),
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