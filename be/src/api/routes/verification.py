"""
API routes for signature verification.
"""

import uuid
import csv
import io
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Body, Path, Query
from fastapi.responses import StreamingResponse
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from src.api.schemas.verification import VerificationRequest, VerificationResponse, BatchVerificationRequest, BatchVerificationResponse, VerificationHistoryResponse, VerificationDelete
from src.services.verification import VerificationService
from src.services.public_keys import PublicKeyService
from src.db.session import get_db_session
from src.db.repositories.public_keys import PublicKeyRepository
from src.api.middlewares.auth import get_current_user
from src.api.schemas.users import UserResponse
from src.services import get_verification_service

router = APIRouter(prefix="/verify", tags=["verification"])


@router.post("", response_model=VerificationResponse)
async def verify_signature(
    request: VerificationRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Verify a signature.
    
    Verifies a digital signature using the specified public key and curve.
    """
    verification_service = get_verification_service()
    
    try:
        # Generate a unique ID for this verification
        verification_id = uuid.uuid4()
        
        # Call the verification service
        result = await verification_service.verify_signature(
            document=request.document,
            signature=request.signature,
            public_key=request.public_key,
            algorithm_name=request.algorithm_name,
            curve_name=request.curve_name
        )
        
        return {
            "verification": result[0],
            "meta_data": result[1]
        }
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Verification failed: {str(e)}"
        )


@router.post("/batch", response_model=BatchVerificationResponse)
async def verify_signatures_batch(
    request: BatchVerificationRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Verify multiple signatures in batch.
    
    Verifies multiple digital signatures using the specified public keys and curves.
    """
    verification_service = get_verification_service()
    
    try:
        # Generate a unique ID for this batch verification
        batch_id = uuid.uuid4()
        
        # Process all items in batch
        results = []
        success_count = 0
        
        for item in request.items:
            try:
                result = await verification_service.verify_signature(
                    document=item.document,
                    signature=item.signature,
                    public_key=item.public_key,
                    curve_name=item.curve_name
                )
                
                results.append({
                    "index": len(results),
                    "is_valid": result["is_valid"],
                    "verification_id": uuid.uuid4()
                })
                
                if result["is_valid"]:
                    success_count += 1
                    
            except Exception as e:
                results.append({
                    "index": len(results),
                    "is_valid": False,
                    "verification_id": uuid.uuid4(),
                    "error": str(e)
                })
        
        # Return the response
        return {
            "batch_id": batch_id,
            "total_count": len(request.items),
            "success_count": success_count,
            "results": results,
            "verification_time": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Batch verification failed: {str(e)}"
        )


@router.get("/{verification_id}", response_model=VerificationResponse)
async def get_verification(
    verification_id: UUID4 = Path(..., description="The verification record ID"),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get a verification record by ID.
    
    Retrieves a previously performed verification record by its ID.
    """
    verification_service = get_verification_service()
    
    result = await verification_service.get_verification_by_id(verification_id)
    
    if not result:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Verification record not found"
        )
    
    return result


@router.get("/history/user", response_model=VerificationHistoryResponse)
async def get_user_verification_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: str = Query(None),
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get verification history for current user.
    
    Retrieves verification records for the currently authenticated user.
    Supports pagination, filtering by status and date range.
    """
    verification_service = get_verification_service()
    
    result = await verification_service.get_user_verification_history(
        user_id=str(current_user.id),
        limit=limit,
        offset=offset,
        status=status,
        start_date=start_date,
        end_date=end_date
    )
    
    return result


@router.get("/history/export")
async def export_verification_history(
    status: str = Query(None),
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Export verification history to CSV.
    
    Exports all verification records for the currently authenticated user to a CSV file.
    Supports filtering by status and date range.
    Returns a CSV file as a streaming response.
    """
    verification_service = get_verification_service()
    
    # Get all records (no pagination)
    result = await verification_service.get_user_verification_history(
        user_id=str(current_user.id),
        limit=1000,  # Use a high limit to get all records
        offset=0,
        status=status,
        start_date=start_date,
        end_date=end_date
    )
    
    # Create a StringIO object to write CSV data
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header row
    writer.writerow([
        "ID", 
        "Document Hash", 
        "Algorithm", 
        "Curve", 
        "Status", 
        "Verification Time",
        "Public Key ID"
    ])
    
    # Write data rows
    for record in result["items"]:
        writer.writerow([
            record["id"],
            record["document_hash"],
            record["algorithm_name"],
            record["curve_name"] or "N/A",
            record["status"],
            record["verified_at"].isoformat(),
            record["public_key_id"]
        ])
    
    # Prepare the response
    output.seek(0)
    
    # Get the current date for the filename
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"verification-history-{current_date}.csv"
    
    # Return the CSV as a streaming response
    return StreamingResponse(
        io.StringIO(output.getvalue()),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.delete("/records/{record_id}", response_model=VerificationDelete)
async def delete_verification_record(
    record_id: UUID4 = Path(..., description="The verification record ID"),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Delete a verification record.
    
    Deletes a verification record created by the current user.
    """
    verification_service = get_verification_service()
    
    # Check if the record exists and belongs to the user
    record = await verification_service.get_verification_by_id(str(record_id))
    
    if not record:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Verification record not found"
        )
    
    # Check if the user owns this record
    if record.get("user_id") and str(record["user_id"]) != str(current_user.id):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this record"
        )
    
    # Delete the record
    success = await verification_service.delete_verification_record(str(record_id))
    
    if not success:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Failed to delete verification record"
        )
    
    return {
        "success": True,
        "message": "Verification record deleted successfully"
    } 