"""
API routes initialization.
"""

from fastapi import APIRouter
from .verification import router as verification_router
from .public_keys import router as public_keys_router
from .algorithms import router as algorithms_router
from .auth import router as auth_router

# Main router that includes all other routers
api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router)
api_router.include_router(verification_router)
api_router.include_router(public_keys_router)
api_router.include_router(algorithms_router) 