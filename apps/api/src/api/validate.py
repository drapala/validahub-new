from fastapi import APIRouter, UploadFile, File, Query, HTTPException, Response
from fastapi.responses import StreamingResponse
from typing import Optional, Dict, Any
import io
import json
import logging

from src.schemas.validate import (
    ValidationResult,
    Marketplace,
    Category,
)
from src.services.validator import csv_validator
from src.services.corrector_v2 import CSVCorrectorV2

logger = logging.getLogger(__name__)
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
        logger.exception("Error processing CSV file")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing CSV: {str(e)}",
        )


@router.post("/correct_csv")
async def correct_csv(
    file: UploadFile = File(..., description="CSV file to correct"),
    marketplace: Marketplace = Query(..., description="Target marketplace"),
    category: Category = Query(..., description="Product category"),
) -> StreamingResponse:
    """
    Validate and automatically correct a CSV file.
    
    Returns the corrected CSV file for download.
    """
    
    # Validate file type
    if not file.filename.endswith(('.csv', '.CSV')):
        raise HTTPException(
            status_code=400,
            detail="File must be a CSV file",
        )
    
    try:
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # First, validate the CSV
        file.file.seek(0)  # Reset file pointer
        validation_result = await csv_validator.validate_csv(
            file=file,
            marketplace=marketplace,
            category=category,
        )
        
        # Apply corrections
        corrector = CSVCorrectorV2()
        corrected_csv, summary = corrector.apply_corrections(
            csv_content=csv_content,
            validation_result=validation_result,
            marketplace=marketplace,
            category=category
        )
        
        # Create response with corrected CSV
        output = io.BytesIO(corrected_csv.encode('utf-8'))
        
        # Generate filename
        original_name = file.filename.rsplit('.', 1)[0]
        corrected_filename = f"{original_name}_corrected.csv"
        
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={corrected_filename}",
                "X-Corrections-Applied": str(summary["total_corrections"]),
                "X-Success-Rate": f"{summary['success_rate']:.1f}%"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error correcting CSV: {str(e)}",
        )


@router.post("/correction_preview")
async def correction_preview(
    file: UploadFile = File(..., description="CSV file to preview corrections"),
    marketplace: Marketplace = Query(..., description="Target marketplace"),
    category: Category = Query(..., description="Product category"),
) -> Dict[str, Any]:
    """
    Preview corrections that would be applied to a CSV file.
    
    Returns a detailed report of proposed corrections without applying them.
    """
    
    # Validate file type
    if not file.filename.endswith(('.csv', '.CSV')):
        raise HTTPException(
            status_code=400,
            detail="File must be a CSV file",
        )
    
    try:
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Validate the CSV
        file.file.seek(0)  # Reset file pointer
        validation_result = await csv_validator.validate_csv(
            file=file,
            marketplace=marketplace,
            category=category,
        )
        
        # Apply corrections (in memory)
        corrector = CSVCorrectorV2()
        corrected_csv, summary = corrector.apply_corrections(
            csv_content=csv_content,
            validation_result=validation_result,
            marketplace=marketplace,
            category=category
        )
        
        # Generate detailed report
        report = corrector.generate_correction_report(
            original_csv=csv_content,
            corrected_csv=corrected_csv,
            summary=summary
        )
        
        return report
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating correction preview: {str(e)}",
        )
