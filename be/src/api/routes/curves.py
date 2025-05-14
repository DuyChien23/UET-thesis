"""
API routes for curve management.
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Body, Query
from starlette.status import HTTP_404_NOT_FOUND, HTTP_201_CREATED, HTTP_200_OK, HTTP_400_BAD_REQUEST

from src.api.schemas.algorithms import (
    CurveInfo, CurveCreate, CurveUpdate, CurveList
)
from src.services import get_algorithm_service
from src.api.middlewares.auth import get_current_user, get_admin_user
from src.api.schemas.users import UserResponse

router = APIRouter(prefix="/curves", tags=["curves"])


@router.get("/", response_model=CurveList)
async def get_curves():
    """
    List all available elliptic curves.
    
    Retrieves a list of all registered curves.
    """
    algorithm_service = get_algorithm_service()
    
    # No filters - get all curves
    curves = await algorithm_service.get_curves({})
    
    return {
        "curves": curves,
        "count": len(curves)
    }


@router.get("/{curve_id}", response_model=CurveInfo)
async def get_curve(
    curve_id: str = Path(..., description="The curve ID"),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get details for a specific curve.
    
    Retrieves detailed information about a specific curve.
    """
    algorithm_service = get_algorithm_service()
    
    try:
        curve = await algorithm_service.get_curve_by_id(curve_id)
        return curve
    except KeyError:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Curve with ID '{curve_id}' not found"
        )


@router.post("/", response_model=CurveInfo, status_code=HTTP_201_CREATED)
async def create_curve(
    curve: CurveCreate = Body(...),
    admin_user: UserResponse = Depends(get_admin_user)
):
    """
    Register a new curve (admin only).
    
    Creates a new curve for an algorithm.
    """
    algorithm_service = get_algorithm_service()
    
    try:
        created_curve = await algorithm_service.create_curve(curve.dict())
        return created_curve
    except KeyError as e:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{curve_id}", response_model=CurveInfo)
async def update_curve(
    curve_id: str = Path(..., description="The curve ID"),
    curve_update: CurveUpdate = Body(...),
    admin_user: UserResponse = Depends(get_admin_user)
):
    """
    Update a curve configuration (admin only).
    
    Updates an existing curve's configuration.
    """
    algorithm_service = get_algorithm_service()
    
    try:
        updated_curve = await algorithm_service.update_curve(
            curve_id, curve_update.dict(exclude_unset=True)
        )
        return updated_curve
    except KeyError as e:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{curve_id}")
async def delete_curve(
    curve_id: str = Path(..., description="The curve ID"),
    admin_user: UserResponse = Depends(get_admin_user)
):
    """
    Delete a curve (admin only).
    
    Disables an existing curve (logical deletion).
    """
    algorithm_service = get_algorithm_service()
    
    try:
        result = await algorithm_service.delete_curve(curve_id)
        return {"message": "Curve successfully disabled"}
    except KeyError as e:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=str(e)
        ) 