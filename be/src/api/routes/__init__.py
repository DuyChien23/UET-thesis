"""
API routes module.

This module defines all API routes for the application.
"""

from fastapi import APIRouter

from .algorithms import router as algorithms_router
from .curves import router as curves_router
from .public_keys import router as public_keys_router
from .verification import router as verification_router
from .signing import router as signing_router
from .auth import router as auth_router

router = APIRouter(prefix="/api")

# Include all routers
router.include_router(auth_router)
router.include_router(algorithms_router)
router.include_router(curves_router)
router.include_router(public_keys_router)
router.include_router(verification_router)
router.include_router(signing_router) 