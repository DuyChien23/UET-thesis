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
from src.core.registry import find_algorithm_for_curve

router = APIRouter(prefix="/sign", tags=["signing"])


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
    
    # Validate the curve name
    try:
        # Check if the curve exists in any algorithm
        algorithm_data = find_algorithm_for_curve(request.curve_name)
        if not algorithm_data:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"Curve with name {request.curve_name} not found"
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
            curve_name=request.curve_name
        )
        
        # Return the result
        return {
            "signature": result["signature"],
            "document_hash": result["document_hash"],
            "public_key": result["public_key"],
            "signing_time": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Signing failed: {str(e)}"
        ) 