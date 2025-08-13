from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from typing import Optional

from src.schemas.validate import (
    ValidationResult,
    Marketplace,
    Category,
)
from src.services.validator import csv_validator

router = APIRouter(prefix="/api/v1", tags=["validation"])


@router.post("/validate_csv", response_model=ValidationResult)
async def validate_csv(
    file: UploadFile = File(..., description="CSV file to validate"),
    marketplace: Marketplace = Query(..., description="Target marketplace"),
    category: Category = Query(..., description="Product category"),
    dry_run: bool = Query(True, description="If true, only validate without saving"),
) -> ValidationResult:
    """
    Validate a CSV file based on marketplace and category rules.
    
    This endpoint:
    - Checks required columns for the marketplace
    - Validates data types and formats
    - Applies category-specific rules
    - Returns detailed error report
    """
    
    # Validate file type
    if not file.filename.endswith(('.csv', '.CSV')):
        raise HTTPException(
            status_code=400,
            detail="File must be a CSV file",
        )
    
    # Validate file size (max 10MB)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size must be less than 10MB",
        )
    
    try:
        # Perform validation
        result = await csv_validator.validate_csv(
            file=file,
            marketplace=marketplace,
            category=category,
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing CSV: {str(e)}",
        )