"""
API routes for algorithm information.
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from starlette.status import HTTP_404_NOT_FOUND

from src.api.schemas.algorithms import AlgorithmInfo, AlgorithmList
from src.services import get_algorithm_service
from src.api.middlewares.auth import get_current_user

router = APIRouter(prefix="/algorithms", tags=["algorithms"])


@router.get("/", response_model=AlgorithmList)
async def get_algorithms(
    user = Depends(get_current_user)
):
    """
    Get all supported algorithms.
    
    Lists all signature algorithms supported by the system.
    """
    algorithm_service = get_algorithm_service()
    
    algorithms = await algorithm_service.get_all_algorithms()
    
    return {
        "items": algorithms,
        "count": len(algorithms)
    }


@router.get("/default", response_model=AlgorithmInfo)
async def get_default_algorithm(
    user = Depends(get_current_user)
):
    """
    Get the default algorithm.
    
    Returns information about the default signature algorithm.
    """
    algorithm_service = get_algorithm_service()
    
    try:
        algorithm = await algorithm_service.get_default_algorithm()
        return algorithm
    except ValueError as e:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/{algorithm_name}", response_model=AlgorithmInfo)
async def get_algorithm(
    algorithm_name: str = Path(..., description="The algorithm name"),
    user = Depends(get_current_user)
):
    """
    Get algorithm details.
    
    Returns detailed information about a specific signature algorithm.
    """
    algorithm_service = get_algorithm_service()
    
    try:
        algorithm = await algorithm_service.get_algorithm_info(algorithm_name)
        return algorithm
    except KeyError:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Algorithm '{algorithm_name}' not found"
        ) 