from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from app.schemas.signature import SignatureCreate, SignatureResponse, SignatureVerify, VerificationResponse
from app.services.signature_service import SignatureService
from app.db.database import get_db
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter()

@router.post(
    "/sign/text", 
    response_model=SignatureResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Sign text data",
    description="Creates a digital signature for the provided text using ECDSA with the selected key pair."
)
async def sign_text(
    text_data: str,
    key_pair_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = SignatureService(db)
    try:
        return service.sign_text(text_data, key_pair_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post(
    "/sign/file", 
    response_model=SignatureResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Sign a file",
    description="Creates a digital signature for the uploaded file using ECDSA with the selected key pair."
)
async def sign_file(
    file: UploadFile = File(...),
    key_pair_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = SignatureService(db)
    try:
        file_content = await file.read()
        return service.sign_file(file_content, file.filename, file.content_type, key_pair_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
@router.post(
    "/verify", 
    response_model=VerificationResponse,
    summary="Verify a signature",
    description="Verifies if a digital signature is valid for the given data using the provided public key."
)
async def verify_signature(
    verification_data: SignatureVerify,
    db: Session = Depends(get_db)
):
    service = SignatureService(db)
    try:
        is_valid = service.verify_signature(verification_data)
        return {"is_valid": is_valid}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get(
    "/user", 
    response_model=List[SignatureResponse],
    summary="Get user signatures",
    description="Returns all signatures created by the authenticated user."
)
async def get_user_signatures(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = SignatureService(db)
    return service.get_user_signatures(current_user.id)

@router.get(
    "/{signature_id}", 
    response_model=SignatureResponse,
    summary="Get signature by ID",
    description="Returns a specific signature by its ID if it belongs to the authenticated user."
)
async def get_signature(
    signature_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = SignatureService(db)
    signature = service.get_signature(signature_id, current_user.id)
    if not signature:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Signature not found")
    return signature 