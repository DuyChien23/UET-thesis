"""
API routes for document signing.
"""

import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from src.api.schemas.signing import SignRequest, SignResponse
from src.db.session import get_db_session
from src.services import get_signing_service, get_algorithm_service

router = APIRouter(prefix="/signing", tags=["signing"])


@router.post("", response_model=SignResponse)
async def sign_document(
    request: SignRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Sign a document.
    
    Signs a document using the specified private key and curve.
    """
    # Get the signing service
    signing_service = get_signing_service()
    algorithm_service = get_algorithm_service()
    
    # Validate the curve name
    try:
        # Check if the curve exists
        curves = await algorithm_service.get_all_curves()
        curve_found = False
        
        for algorithm in curves:
            if request.curves_name in algorithm["curves"]:
                curve_found = True
                break
                
        if not curve_found:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"Curve with name {request.curves_name} not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Error validating curve: {str(e)}"
        )
    
    # Sign the document
    try:
        result = await signing_service.sign_document(
            document=request.document,
            private_key=request.private_key,
            curve_name=request.curves_name,
            metadata=request.metadata
        )
        
        # Return the result
        return SignResponse(
            id=result["id"],
            document=result["document"],
            signature=result["signature"],
            algorithm_name=result["algorithm_name"],
            curve_name=result["curve_name"],
            signing_time=result["signing_time"],
            metadata=result["metadata"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Signing failed: {str(e)}"
        ) 