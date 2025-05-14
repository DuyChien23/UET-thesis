"""
API routes for algorithm information.
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Body
from starlette.status import HTTP_404_NOT_FOUND, HTTP_201_CREATED, HTTP_200_OK, HTTP_400_BAD_REQUEST

from src.api.schemas.algorithms import (
    AlgorithmInfo, AlgorithmList, AlgorithmCreate, AlgorithmUpdate,
    CurveInfo, CurveCreate, CurveUpdate
)
from src.services import get_algorithm_service
from src.api.middlewares.auth import get_current_user, get_admin_user
from src.api.schemas.users import UserResponse

router = APIRouter(prefix="/algorithms", tags=["algorithms"])


@router.get("/", response_model=AlgorithmList)
async def get_algorithms():
    """
    Get all supported algorithms.
    
    Lists all signature algorithms supported by the system.
    """
    algorithm_service = get_algorithm_service()
    
    algorithms = await algorithm_service.get_all_algorithms()
    
    # Ensure each curve has algorithm_id field
    for algo in algorithms:
        for curve in algo.get("curves", []):
            if "algorithm_id" not in curve:
                curve["algorithm_id"] = str(algo["id"])
            if "algorithm_name" not in curve:
                curve["algorithm_name"] = algo["name"]
    
    return {
        "items": algorithms,
        "count": len(algorithms)
    }


@router.get("/default", response_model=AlgorithmInfo)
async def get_default_algorithm():
    """
    Get the default algorithm.
    
    Returns information about the default signature algorithm.
    """
    algorithm_service = get_algorithm_service()
    
    try:
        algorithm = await algorithm_service.get_default_algorithm()
        
        # Ensure each curve has algorithm_id field
        for curve in algorithm.get("curves", []):
            if "algorithm_id" not in curve:
                curve["algorithm_id"] = str(algorithm["id"])
            if "algorithm_name" not in curve:
                curve["algorithm_name"] = algorithm["name"]
                
        return algorithm
    except ValueError as e:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/{algorithm_name}", response_model=AlgorithmInfo)
async def get_algorithm(
    algorithm_name: str = Path(..., description="The algorithm name")
):
    """
    Get algorithm details.
    
    Returns detailed information about a specific signature algorithm.
    """
    algorithm_service = get_algorithm_service()
    
    try:
        algorithm = await algorithm_service.get_algorithm_info(algorithm_name)
        
        # Ensure each curve has algorithm_id field
        for curve in algorithm.get("curves", []):
            if "algorithm_id" not in curve:
                curve["algorithm_id"] = str(algorithm["id"])
            if "algorithm_name" not in curve:
                curve["algorithm_name"] = algorithm["name"]
                
        return algorithm
    except KeyError:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Algorithm '{algorithm_name}' not found"
        )


# Endpoints requiring authentication
@router.get("/auth/", response_model=AlgorithmList)
async def get_algorithms_auth(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get all supported algorithms (requires authentication).
    
    Lists all signature algorithms supported by the system.
    """
    algorithm_service = get_algorithm_service()
    
    algorithms = await algorithm_service.get_all_algorithms()
    
    # Ensure each curve has algorithm_id field
    for algo in algorithms:
        for curve in algo.get("curves", []):
            if "algorithm_id" not in curve:
                curve["algorithm_id"] = str(algo["id"])
            if "algorithm_name" not in curve:
                curve["algorithm_name"] = algo["name"]
    
    return {
        "items": algorithms,
        "count": len(algorithms)
    }


@router.get("/auth/default", response_model=AlgorithmInfo)
async def get_default_algorithm_auth(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get the default algorithm (requires authentication).
    
    Returns information about the default signature algorithm.
    """
    algorithm_service = get_algorithm_service()
    
    try:
        algorithm = await algorithm_service.get_default_algorithm()
        
        # Ensure each curve has algorithm_id field
        for curve in algorithm.get("curves", []):
            if "algorithm_id" not in curve:
                curve["algorithm_id"] = str(algorithm["id"])
            if "algorithm_name" not in curve:
                curve["algorithm_name"] = algorithm["name"]
                
        return algorithm
    except ValueError as e:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/auth/{algorithm_name}", response_model=AlgorithmInfo)
async def get_algorithm_auth(
    algorithm_name: str = Path(..., description="The algorithm name"),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get algorithm details (requires authentication).
    
    Returns detailed information about a specific signature algorithm.
    """
    algorithm_service = get_algorithm_service()
    
    try:
        algorithm = await algorithm_service.get_algorithm_info(algorithm_name)
        
        # Ensure each curve has algorithm_id field
        for curve in algorithm.get("curves", []):
            if "algorithm_id" not in curve:
                curve["algorithm_id"] = str(algorithm["id"])
            if "algorithm_name" not in curve:
                curve["algorithm_name"] = algorithm["name"]
                
        return algorithm
    except KeyError:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Algorithm '{algorithm_name}' not found"
        )


# Admin endpoints for managing algorithms
@router.post("/", response_model=AlgorithmInfo, status_code=HTTP_201_CREATED)
async def create_algorithm(
    algorithm: AlgorithmCreate = Body(...),
    admin_user: UserResponse = Depends(get_admin_user)
):
    """
    Create a new algorithm (admin only).
    
    Creates a new signature algorithm in the system.
    """
    algorithm_service = get_algorithm_service()
    
    try:
        created_algorithm = await algorithm_service.create_algorithm(algorithm.dict())
        return created_algorithm
    except ValueError as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{algorithm_id}", response_model=AlgorithmInfo)
async def update_algorithm(
    algorithm_id: str = Path(..., description="The algorithm ID"),
    algorithm_update: AlgorithmUpdate = Body(...),
    admin_user: UserResponse = Depends(get_admin_user)
):
    """
    Update an algorithm (admin only).
    
    Updates an existing signature algorithm.
    """
    algorithm_service = get_algorithm_service()
    
    try:
        updated_algorithm = await algorithm_service.update_algorithm(
            algorithm_id, algorithm_update.dict(exclude_unset=True)
        )
        return updated_algorithm
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


@router.delete("/{algorithm_id}")
async def delete_algorithm(
    algorithm_id: str = Path(..., description="The algorithm ID"),
    admin_user: UserResponse = Depends(get_admin_user)
):
    """
    Delete (disable) an algorithm (admin only).
    
    Disables an existing signature algorithm.
    """
    algorithm_service = get_algorithm_service()
    
    try:
        result = await algorithm_service.delete_algorithm(algorithm_id)
        return result
    except KeyError as e:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# Curves endpoints
@router.post("/curves", response_model=CurveInfo, status_code=HTTP_201_CREATED)
async def create_curve(
    curve: CurveCreate = Body(...),
    admin_user: UserResponse = Depends(get_admin_user)
):
    """
    Create a new curve (admin only).
    
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


@router.put("/curves/{curve_id}", response_model=CurveInfo)
async def update_curve(
    curve_id: str = Path(..., description="The curve ID"),
    curve_update: CurveUpdate = Body(...),
    admin_user: UserResponse = Depends(get_admin_user)
):
    """
    Update a curve (admin only).
    
    Updates an existing curve.
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


@router.delete("/curves/{curve_id}")
async def delete_curve(
    curve_id: str = Path(..., description="The curve ID"),
    admin_user: UserResponse = Depends(get_admin_user)
):
    """
    Delete (disable) a curve (admin only).
    
    Disables an existing curve.
    """
    algorithm_service = get_algorithm_service()
    
    try:
        result = await algorithm_service.delete_curve(curve_id)
        return result
    except KeyError as e:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=str(e)
        ) 