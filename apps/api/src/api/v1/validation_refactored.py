"""
Refactored validation endpoints following Clean Architecture.
These endpoints delegate business logic to use cases.
"""

import time
import logging
from typing import Dict, Any, Iterator
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import StreamingResponse, JSONResponse

from ...core.use_cases.validate_csv import ValidateCsvUseCase, ValidateCsvInput
from ...core.use_cases.validate_row import ValidateRowUseCase, ValidateRowInput
from ...schemas.validate import (
    Marketplace,
    Category,
    ValidationResult,
    ValidateCsvRequest,
    CorrectCsvRequest,
    CorrectionPreviewRequest
)
from ..dependencies.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v3", tags=["validation-refactored"])


def csv_streamer(csv_text: str, chunk_size: int = 8192) -> Iterator[bytes]:
    """
    Stream CSV content in chunks for memory efficiency.
    
    Args:
        csv_text: The CSV content as string
        chunk_size: Size of each chunk in bytes
        
    Yields:
        Chunks of encoded CSV data
    """
    encoded = csv_text.encode('utf-8')
    for i in range(0, len(encoded), chunk_size):
        yield encoded[i:i+chunk_size]


@router.post("/validate-csv", response_model=ValidationResult)
async def validate_csv(
    file: UploadFile = File(...),
    marketplace: Marketplace = Form(...),
    category: Category = Form(...),
    auto_fix: bool = Form(True),
    current_user: Dict = Depends(get_current_user)
) -> ValidationResult:
    """
    Validate CSV file using Clean Architecture.
    
    This endpoint handles only HTTP concerns and delegates
    business logic to the ValidateCsvUseCase.
    """
    try:
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Create use case input
        input_data = ValidateCsvInput(
            csv_content=csv_content,
            marketplace=marketplace,
            category=category,
            auto_fix=auto_fix
        )
        
        # Execute use case
        use_case = ValidateCsvUseCase()
        result = await use_case.execute(input_data)
        
        # Add metadata
        result.original_filename = file.filename
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error validating CSV: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/correct-csv")
async def correct_csv(
    file: UploadFile = File(...),
    marketplace: Marketplace = Form(...),
    category: Category = Form(...),
    current_user: Dict = Depends(get_current_user)
):
    """
    Correct CSV file and return as streaming response.
    
    This endpoint validates and corrects the CSV, then returns
    the corrected version as a downloadable file.
    """
    try:
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Create use case input with auto_fix enabled
        input_data = ValidateCsvInput(
            csv_content=csv_content,
            marketplace=marketplace,
            category=category,
            auto_fix=True
        )
        
        # Execute use case
        use_case = ValidateCsvUseCase()
        result = await use_case.execute(input_data)
        
        # Check if corrections were applied
        if not result.corrected_csv:
            return JSONResponse(
                status_code=200,
                content={
                    "message": "No corrections needed",
                    "total_rows": result.total_rows,
                    "valid_rows": result.valid_rows
                }
            )
        
        # Generate filename
        original_name = file.filename.rsplit('.', 1)[0]
        corrected_filename = f"{original_name}_corrected.csv"
        
        # Return streaming response with memory-efficient approach
        return StreamingResponse(
            csv_streamer(result.corrected_csv),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={corrected_filename}"
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error correcting CSV: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/validate-row")
async def validate_row(
    row_data: Dict[str, Any],
    row_number: int = 1,
    marketplace: Marketplace = Marketplace.MERCADO_LIVRE,
    category: Category = Category.ELETRONICOS,
    auto_fix: bool = False,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Validate a single row of data.
    
    This endpoint validates individual rows without
    requiring a full CSV file.
    """
    try:
        # Create use case input
        input_data = ValidateRowInput(
            row_data=row_data,
            row_number=row_number,
            marketplace=marketplace,
            category=category,
            auto_fix=auto_fix
        )
        
        # Execute use case
        use_case = ValidateRowUseCase()
        result = await use_case.execute(input_data)
        
        # Convert to response format
        return {
            "row_number": result.row_number,
            "has_errors": result.has_errors,
            "has_warnings": result.has_warnings,
            "validation_items": [item.dict() for item in result.validation_items],
            "corrected_data": result.corrected_data,
            "summary": result.summary.dict() if result.summary else None
        }
        
    except Exception as e:
        logger.exception(f"Error validating row: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/correction-preview", response_model=Dict[str, Any])
async def correction_preview(
    file: UploadFile = File(...),
    request: CorrectionPreviewRequest = ...,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Preview corrections that would be applied to a CSV.
    
    This endpoint shows a sample of corrections without
    actually modifying the entire file.
    """
    try:
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Create use case input
        input_data = ValidateCsvInput(
            csv_content=csv_content,
            marketplace=request.marketplace,
            category=request.category,
            auto_fix=True,
            options={
                "sample_size": request.sample_size,
                "sample_strategy": request.sample_strategy,
                "show_only_changed": request.show_only_changed
            }
        )
        
        # Execute use case
        use_case = ValidateCsvUseCase()
        result = await use_case.execute(input_data)
        
        # Build preview response
        preview_items = result.validation_items[:request.sample_size]
        
        return {
            "summary": {
                "total_corrections": sum(1 for item in result.validation_items if item.corrections),
                "success_rate": (result.valid_rows / result.total_rows * 100) if result.total_rows > 0 else 0,
                "corrections_by_rule": {},  # Would need to aggregate from validation items
                "affected_rows": [item.row_number for item in result.validation_items if item.corrections][:100]
            },
            "preview_data": result.corrected_data[:request.sample_size] if result.corrected_data else [],
            "changes": [item.dict() for item in preview_items],
            "job_id": result.job_id
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error generating correction preview: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")