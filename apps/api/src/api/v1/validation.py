"""
Enhanced validation endpoints using YAML-based rule engine.
"""

from fastapi import (
    APIRouter, 
    UploadFile, 
    File, 
    Form,
    Query, 
    HTTPException, 
    Header,
    Response,
    status,
    Depends,
    BackgroundTasks
)
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional, Dict, Any, Union
import io
import json
import logging
import uuid
import time
import os
from datetime import datetime
import pandas as pd

from ...schemas.validate import (
    ValidationResult,
    Marketplace,
    Category,
    ValidateCsvRequest,
    CorrectCsvRequest,
    AsyncJobResponse
)
from ...schemas.errors import (
    ProblemDetail,
    ValidationProblemDetail,
    FileSizeProblemDetail,
    RateLimitProblemDetail
)
from ...core.pipeline.validation_pipeline import ValidationPipeline
from ...services.rule_engine_service import RuleEngineService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["validation"])

# Constants
MAX_SYNC_FILE_SIZE = int(os.environ.get("MAX_SYNC_FILE_SIZE", 5 * 1024 * 1024))  # 5MB default
MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", 50 * 1024 * 1024))           # 50MB default
RULESET_VERSION = "2.0.0"

# Initialize services
rule_engine_service = RuleEngineService()
validation_pipeline = ValidationPipeline(rule_engine_service=rule_engine_service)


def get_correlation_id(
    x_correlation_id: Optional[str] = Header(None, alias="X-Correlation-Id")
) -> str:
    """Generate or return correlation ID for request tracking."""
    return x_correlation_id or str(uuid.uuid4())


def problem_response(problem: ProblemDetail) -> JSONResponse:
    """Create a problem+json response."""
    # Convert to dict and handle datetime serialization
    content = problem.model_dump(exclude_none=True)
    
    # Convert datetime fields to ISO format strings
    if "timestamp" in content and content["timestamp"]:
        if isinstance(content["timestamp"], datetime):
            content["timestamp"] = content["timestamp"].isoformat()
    
    if "rate_limit_reset" in content and content["rate_limit_reset"]:
        if isinstance(content["rate_limit_reset"], datetime):
            content["rate_limit_reset"] = content["rate_limit_reset"].isoformat()
    
    return JSONResponse(
        status_code=problem.status,
        content=content,
        headers={"Content-Type": "application/problem+json"}
    )


@router.post(
    "/validate",
    response_model=ValidationResult,
    responses={
        202: {"model": AsyncJobResponse, "description": "Request accepted for async processing"},
        400: {"model": ProblemDetail, "description": "Bad request"},
        413: {"model": FileSizeProblemDetail, "description": "File too large"},
        415: {"model": ProblemDetail, "description": "Unsupported media type"},
        422: {"model": ValidationProblemDetail, "description": "Validation error"},
        429: {"model": RateLimitProblemDetail, "description": "Rate limit exceeded"}
    },
    operation_id="validateCsv"
)
async def validate_csv_v2(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="CSV file to validate"),
    marketplace: Marketplace = Form(..., description="Target marketplace"),
    category: Category = Form(..., description="Product category"),
    auto_fix: bool = Form(True, description="Automatically fix issues when possible"),
    options: Optional[str] = Form(None, description="Additional options as JSON"),
    correlation_id: str = Depends(get_correlation_id),
):
    """
    Validate a CSV file using YAML-based rule engine.
    
    Enhanced features:
    - Uses configurable YAML rules instead of hardcoded logic
    - Supports auto-fix mode for automatic corrections
    - Returns detailed validation items with error and correction details
    - Provides comprehensive summary statistics
    
    This endpoint:
    - Loads marketplace-specific rules from YAML files
    - Validates each row against the ruleset
    - Optionally applies automatic fixes
    - Returns detailed results with corrected data if auto_fix=true
    """
    
    # Parse options if provided
    parsed_options = {}
    if options:
        try:
            parsed_options = json.loads(options)
        except json.JSONDecodeError:
            return problem_response(ValidationProblemDetail(
                detail="Invalid JSON in options parameter",
                instance=f"/api/v1/validate",
                extensions={"field": "options"},
                correlation_id=correlation_id
            ))
    
    # Validate file type
    if not file.filename.endswith(('.csv', '.CSV')):
        return problem_response(ProblemDetail(
            type="/errors/invalid-file-type",
            title="Invalid File Type",
            status=415,
            detail="File must be a CSV file",
            instance="/api/v1/validate",
            correlation_id=correlation_id
        ))
    
    # Check file size
    if file.size and file.size > MAX_FILE_SIZE:
        return problem_response(FileSizeProblemDetail(
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE/1024/1024:.0f}MB",
            instance="/api/v1/validate",
            max_size_bytes=MAX_FILE_SIZE,
            actual_size_bytes=file.size,
            correlation_id=correlation_id
        ))
    
    # Determine sync vs async processing
    if file.size and file.size > MAX_SYNC_FILE_SIZE:
        # Async processing for large files
        job_id = str(uuid.uuid4())
        
        background_tasks.add_task(
            process_validation_async_v2,
            job_id=job_id,
            file=file,
            marketplace=marketplace,
            category=category,
            auto_fix=auto_fix,
            options=parsed_options,
            correlation_id=correlation_id
        )
        
        return AsyncJobResponse(
            job_id=job_id,
            status="accepted",
            message="File accepted for processing",
            location=f"/api/v1/jobs/{job_id}"
        )
    
    # Synchronous processing for small files
    try:
        # Read CSV file
        content = await file.read()
        csv_str = content.decode('utf-8', errors='replace')
        
        # Parse CSV to DataFrame
        df = pd.read_csv(io.StringIO(csv_str))
        
        # Handle NaN and inf values right after reading
        import numpy as np
        df = df.replace([np.inf, -np.inf], None)
        df = df.where(pd.notnull(df), None)
        
        # Validate using pipeline
        result = validation_pipeline.validate(
            df=df,
            marketplace=marketplace,
            category=category,
            auto_fix=auto_fix
        )
        
        # Add job_id for tracking
        result.job_id = str(uuid.uuid4())
        
        # Convert corrected DataFrame to dict if present
        if result.corrected_data is not None:
            # Handle NaN and inf values before converting to dict
            import numpy as np
            df = result.corrected_data
            df = df.replace([np.inf, -np.inf], None)
            df = df.where(pd.notnull(df), None)
            result.corrected_data = df.to_dict('records')
        
        return result
        
    except pd.errors.EmptyDataError:
        return problem_response(ValidationProblemDetail(
            detail="CSV file is empty or invalid",
            instance="/api/v1/validate",
            correlation_id=correlation_id
        ))
    except Exception as e:
        logger.exception("Error processing CSV file")
        return problem_response(ProblemDetail(
            type="/errors/processing-error",
            title="Processing Error",
            status=500,
            detail=f"Error processing CSV: {str(e)}",
            instance="/api/v1/validate",
            correlation_id=correlation_id
        ))


# Alias endpoint for compatibility with frontend
@router.post(
    "/validate_csv",
    response_model=ValidationResult,
    responses={
        202: {"model": AsyncJobResponse, "description": "Request accepted for async processing"},
        400: {"model": ProblemDetail, "description": "Bad request"},
        413: {"model": FileSizeProblemDetail, "description": "File too large"},
        415: {"model": ProblemDetail, "description": "Unsupported media type"},
        422: {"model": ValidationProblemDetail, "description": "Validation error"},
        429: {"model": RateLimitProblemDetail, "description": "Rate limit exceeded"}
    },
    operation_id="validateCsvAlias",
    include_in_schema=False  # Hide from docs to avoid duplication
)
async def validate_csv_alias(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    marketplace: Marketplace = Query(...),
    category: Category = Query(...),
    auto_fix: bool = Query(True),
    options: Optional[str] = Query(None),
    correlation_id: str = Depends(get_correlation_id),
):
    """Alias for /validate endpoint for backward compatibility."""
    # Call the main validate function with Form parameters converted to Query
    return await validate_csv_v2(
        background_tasks=background_tasks,
        file=file,
        marketplace=marketplace,
        category=category,
        auto_fix=auto_fix,
        options=options,
        correlation_id=correlation_id
    )


@router.post(
    "/validate_row",
    response_model=Dict[str, Any],
    responses={
        400: {"model": ProblemDetail, "description": "Bad request"},
        422: {"model": ValidationProblemDetail, "description": "Validation error"}
    },
    operation_id="validateRow"
)
async def validate_row_v2(
    row_data: Dict[str, Any],
    marketplace: Marketplace = Query(..., description="Target marketplace"),
    category: Optional[Category] = Query(None, description="Product category"),
    auto_fix: bool = Query(True, description="Automatically fix issues when possible"),
    row_number: int = Query(1, description="Row number for context", ge=1),
    correlation_id: str = Depends(get_correlation_id),
):
    """
    Validate a single row of data using YAML-based rule engine.
    
    This endpoint is useful for:
    - Real-time validation as users enter data
    - Testing rules on individual records
    - API-based integrations that process rows individually
    
    Returns the validation results and optionally the corrected row data.
    """
    
    try:
        # Validate single row
        fixed_row, validation_items = validation_pipeline.validate_single_row(
            row=row_data,
            marketplace=marketplace,
            category=category,
            row_number=row_number,
            auto_fix=auto_fix
        )
        
        return {
            "original_row": row_data,
            "fixed_row": fixed_row if auto_fix else None,
            "validation_items": [item.model_dump() for item in validation_items],
            "has_errors": any(item.status.value == "ERROR" for item in validation_items),
            "has_warnings": any(item.status.value == "WARNING" for item in validation_items),
            "auto_fix_applied": auto_fix
        }
        
    except Exception as e:
        logger.exception("Error validating row")
        return problem_response(ProblemDetail(
            type="/errors/processing-error",
            title="Processing Error",
            status=500,
            detail=f"Error validating row: {str(e)}",
            instance="/api/v1/validate_row",
            correlation_id=correlation_id
        ))


@router.post(
    "/correct",
    response_model=None,  # Dynamic response type
    responses={
        200: {"description": "Corrected CSV file", "content": {"text/csv": {}}},
        202: {"model": AsyncJobResponse, "description": "Request accepted for async processing"},
        400: {"model": ProblemDetail, "description": "Bad request"},
        413: {"model": FileSizeProblemDetail, "description": "File too large"},
        415: {"model": ProblemDetail, "description": "Unsupported media type"},
        422: {"model": ValidationProblemDetail, "description": "Validation error"},
    },
    operation_id="correctCsv"
)
async def correct_csv_v2(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="CSV file to correct"),
    marketplace: Marketplace = Form(..., description="Target marketplace"),
    category: Category = Form(..., description="Product category"),
    options: Optional[str] = Form(None, description="Additional options as JSON"),
    correlation_id: str = Depends(get_correlation_id),
):
    """
    Validate and automatically correct a CSV file using YAML-based rules.
    
    Returns the corrected CSV file for download (sync) or job ID (async).
    
    This endpoint:
    - Uses YAML-configured rules for validation and correction
    - Applies all available fixes automatically
    - Returns a downloadable corrected CSV file
    - Provides correction statistics in response headers
    """
    
    # Parse options if provided
    parsed_options = {}
    if options:
        try:
            parsed_options = json.loads(options)
        except json.JSONDecodeError:
            return problem_response(ValidationProblemDetail(
                detail="Invalid JSON in options parameter",
                instance="/api/v1/correct",
                extensions={"field": "options"},
                correlation_id=correlation_id
            ))
    
    # Validate file type
    if not file.filename.endswith(('.csv', '.CSV')):
        return problem_response(ProblemDetail(
            type="/errors/invalid-file-type",
            title="Invalid File Type",
            status=415,
            detail="File must be a CSV file",
            instance="/api/v1/correct",
            correlation_id=correlation_id
        ))
    
    # Check file size
    if file.size and file.size > MAX_FILE_SIZE:
        return problem_response(FileSizeProblemDetail(
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE/1024/1024:.0f}MB",
            instance="/api/v1/correct",
            max_size_bytes=MAX_FILE_SIZE,
            actual_size_bytes=file.size,
            correlation_id=correlation_id
        ))
    
    # Async processing for large files
    if file.size and file.size > MAX_SYNC_FILE_SIZE:
        job_id = str(uuid.uuid4())
        
        background_tasks.add_task(
            process_correction_async_v2,
            job_id=job_id,
            file=file,
            marketplace=marketplace,
            category=category,
            options=parsed_options,
            correlation_id=correlation_id
        )
        
        return AsyncJobResponse(
            job_id=job_id,
            status="accepted",
            message="File accepted for processing",
            location=f"/api/v1/jobs/{job_id}"
        )
    
    # Synchronous processing
    try:
        # Read CSV file
        content = await file.read()
        csv_str = content.decode('utf-8', errors='replace')
        
        # Parse CSV to DataFrame
        df = pd.read_csv(io.StringIO(csv_str))
        
        # Handle NaN and inf values right after reading
        import numpy as np
        df = df.replace([np.inf, -np.inf], None)
        df = df.where(pd.notnull(df), None)
        
        # Validate and fix using pipeline
        result = validation_pipeline.validate(
            df=df,
            marketplace=marketplace,
            category=category,
            auto_fix=True  # Always fix for this endpoint
        )
        
        # Convert corrected DataFrame to CSV
        if result.corrected_data is not None:
            corrected_csv = result.corrected_data.to_csv(index=False)
        else:
            # If no corrections, return original
            corrected_csv = csv_str
        
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
                "X-Total-Corrections": str(result.summary.total_corrections),
                "X-Total-Errors": str(result.summary.total_errors),
                "X-Total-Warnings": str(result.summary.total_warnings),
                "X-Processing-Time": f"{result.summary.processing_time_seconds:.2f}s",
                "X-Correlation-Id": correlation_id,
                "X-Job-Id": str(uuid.uuid4())
            }
        )
        
    except Exception as e:
        logger.exception("Error correcting CSV file")
        return problem_response(ProblemDetail(
            type="/errors/processing-error",
            title="Processing Error",
            status=500,
            detail=f"Error correcting CSV: {str(e)}",
            instance="/api/v1/correct",
            correlation_id=correlation_id
        ))


# Alias endpoint for compatibility with frontend
@router.post(
    "/correct_csv",
    response_model=None,
    responses={
        200: {"description": "Corrected CSV file", "content": {"text/csv": {}}},
        202: {"model": AsyncJobResponse, "description": "Request accepted for async processing"},
        400: {"model": ProblemDetail, "description": "Bad request"},
        413: {"model": FileSizeProblemDetail, "description": "File too large"},
        415: {"model": ProblemDetail, "description": "Unsupported media type"},
        422: {"model": ValidationProblemDetail, "description": "Validation error"},
    },
    operation_id="correctCsvAlias",
    include_in_schema=False
)
async def correct_csv_alias(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    marketplace: Marketplace = Query(...),
    category: Category = Query(...),
    options: Optional[str] = Query(None),
    correlation_id: str = Depends(get_correlation_id),
):
    """Alias for /correct endpoint for backward compatibility."""
    return await correct_csv_v2(
        background_tasks=background_tasks,
        file=file,
        marketplace=marketplace,
        category=category,
        options=options,
        correlation_id=correlation_id
    )


# Alias endpoint for correction preview
@router.post(
    "/correction_preview",
    response_model=Dict[str, Any],
    responses={
        400: {"model": ProblemDetail, "description": "Bad request"},
        413: {"model": FileSizeProblemDetail, "description": "File too large"},
        422: {"model": ValidationProblemDetail, "description": "Validation error"},
    },
    operation_id="correctionPreview",
    include_in_schema=False
)
async def correction_preview(
    file: UploadFile = File(...),
    marketplace: Marketplace = Query(...),
    category: Category = Query(...),
    sample_size: int = Query(100, ge=1, le=1000),
    correlation_id: str = Depends(get_correlation_id),
):
    """Preview corrections that would be applied to a CSV file."""
    try:
        # Read and validate file
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            return problem_response(FileSizeProblemDetail(
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE/1024/1024:.1f}MB",
                max_size_mb=MAX_FILE_SIZE/1024/1024,
                provided_size_mb=len(content)/1024/1024,
                instance="/api/v1/correction_preview",
                correlation_id=correlation_id
            ))
        
        # Process CSV with preview
        df = pd.read_csv(io.BytesIO(content), nrows=sample_size)
        
        # Validate and get corrections
        result = validation_pipeline.validate(
            df=df,
            marketplace=marketplace,
            category=category,
            auto_fix=True
        )
        
        # Build preview response
        preview_data = {
            "sample_size": len(df),
            "total_corrections": result.summary.total_corrections,
            "corrections_by_field": {},
            "preview_rows": []
        }
        
        # Count corrections by field
        for item in result.validation_items:
            for correction in item.corrections:
                field = correction.field
                if field not in preview_data["corrections_by_field"]:
                    preview_data["corrections_by_field"][field] = 0
                preview_data["corrections_by_field"][field] += 1
        
        # Add first 10 rows with corrections
        for item in result.validation_items[:10]:
            if item.corrections:
                preview_data["preview_rows"].append({
                    "row": item.row_number,
                    "corrections": [
                        {
                            "field": c.field,
                            "before": c.original_value,
                            "after": c.corrected_value,
                            "type": c.correction_type
                        }
                        for c in item.corrections
                    ]
                })
        
        return preview_data
        
    except Exception as e:
        logger.exception("Error in correction preview")
        return problem_response(ProblemDetail(
            type="/errors/preview-error",
            title="Preview Error",
            status=500,
            detail=f"Error generating preview: {str(e)}",
            instance="/api/v1/correction_preview",
            correlation_id=correlation_id
        ))


@router.post("/reload_rules")
async def reload_rules(
    marketplace: Optional[Marketplace] = Query(None, description="Specific marketplace to reload"),
    correlation_id: str = Depends(get_correlation_id),
):
    """
    Reload validation rules from YAML files.
    
    This endpoint is useful for:
    - Updating rules without restarting the service
    - Testing new rule configurations
    - Clearing cached rules
    
    If no marketplace is specified, all rules are reloaded.
    """
    
    try:
        validation_pipeline.reload_rules(marketplace)
        
        return {
            "status": "success",
            "message": f"Rules reloaded for {marketplace.value if marketplace else 'all marketplaces'}",
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": correlation_id
        }
        
    except Exception as e:
        logger.exception("Error reloading rules")
        return problem_response(ProblemDetail(
            type="/errors/reload-error",
            title="Reload Error",
            status=500,
            detail=f"Error reloading rules: {str(e)}",
            instance="/api/v1/reload_rules",
            correlation_id=correlation_id
        ))


# Async processing functions
async def process_validation_async_v2(
    job_id: str,
    file: UploadFile,
    marketplace: Marketplace,
    category: Category,
    auto_fix: bool,
    options: dict,
    correlation_id: str
):
    """Process validation asynchronously with rule engine."""
    # TODO: Implement with Celery or similar job queue
    logger.info(f"Processing validation job {job_id} asynchronously with rule engine")


async def process_correction_async_v2(
    job_id: str,
    file: UploadFile,
    marketplace: Marketplace,
    category: Category,
    options: dict,
    correlation_id: str
):
    """Process correction asynchronously with rule engine."""
    # TODO: Implement with Celery or similar job queue
    logger.info(f"Processing correction job {job_id} asynchronously with rule engine")