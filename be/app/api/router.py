from fastapi import APIRouter
from app.api.endpoints import users, key_pairs, signatures

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(key_pairs.router, prefix="/key-pairs", tags=["key-pairs"])
api_router.include_router(signatures.router, prefix="/signatures", tags=["signatures"]) 