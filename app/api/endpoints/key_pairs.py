from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.key_pair import KeyPairCreate, KeyPairResponse, KeyPairWithoutPrivate
from app.services.key_pair_service import KeyPairService
from app.db.database import get_db
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter()

@router.post(
    "/", 
    response_model=KeyPairResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new key pair",
    description="Generates a new ECDSA key pair for the authenticated user. The private key is encrypted with the user's password."
)
def create_key_pair(
    key_pair: KeyPairCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    service = KeyPairService(db)
    try:
        return service.create_key_pair(key_pair, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get(
    "/", 
    response_model=List[KeyPairWithoutPrivate],
    summary="Get all user key pairs",
    description="Returns all key pairs belonging to the authenticated user. The private keys are not included in the response for security reasons."
)
def get_user_key_pairs(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    service = KeyPairService(db)
    return service.get_user_key_pairs(current_user.id)

@router.get(
    "/{key_pair_id}", 
    response_model=KeyPairWithoutPrivate,
    summary="Get key pair by ID",
    description="Returns a specific key pair by its ID if it belongs to the authenticated user. The private key is not included in the response for security reasons."
)
def get_key_pair(
    key_pair_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    service = KeyPairService(db)
    key_pair = service.get_key_pair(key_pair_id, current_user.id)
    if not key_pair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Key pair not found")
    return key_pair 