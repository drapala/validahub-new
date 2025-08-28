"""
Refactored validation endpoints following Clean Architecture.
Endpoints now only handle HTTP concerns and delegate to use cases.
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
from src.core.logging_config import get_logger
import os
import uuid
from datetime import datetime

from ...schemas.validate import (
    ValidationResult,
    Marketplace,
    Category,
    AsyncJobResponse
)
from ...schemas.errors import (
    ProblemDetail,
    ValidationProblemDetail,
    FileSizeProblemDetail,
    RateLimitProblemDetail
)
from ...core.interfaces import IRuleEngineService
from ...core.pipeline.validation_pipeline_decoupled import ValidationPipelineDecoupled
from ...core.use_cases import (
    CorrectCsvUseCase,
    ValidateCsvUseCase,
    ValidateRowUseCase,
)
from ...core.use_cases.correct_csv import CorrectCsvInput
from ...core.use_cases.validate_csv import ValidateCsvInput
from ...core.use_cases.validate_row import ValidateRowInput
from ...infrastructure.validators.rule_engine_validator import RuleEngineValidator
from ...services.rule_engine_service import RuleEngineService

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["validation-refactored"])

# Constants
MAX_SYNC_FILE_SIZE = int(os.environ.get("MAX_SYNC_FILE_SIZE", 5 * 1024 * 1024))  # 5MB default
MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", 50 * 1024 * 1024))           # 50MB default

# Note: Chunked CSV processing for large files is tracked in BACKLOG.md under PERF-1

# Dependency provider functions for better DI and testing
def get_rule_engine_service() -> IRuleEngineService:
    """Provide rule engine service instance."""
    return RuleEngineService()


def get_validator(
    rule_engine_service: IRuleEngineService = Depends(get_rule_engine_service),
) -> RuleEngineValidator:
    """Provide validator with injected rule engine service."""
    return RuleEngineValidator(rule_engine_service)


def get_validation_pipeline(
    validator: RuleEngineValidator = Depends(get_validator),
) -> ValidationPipelineDecoupled:
    """Provide validation pipeline with injected validator."""
    return ValidationPipelineDecoupled(validator=validator)


def get_validate_csv_use_case(
    validation_pipeline: ValidationPipelineDecoupled = Depends(get_validation_pipeline),
) -> ValidateCsvUseCase:
    """Provide validate CSV use case."""
    return ValidateCsvUseCase(validation_pipeline)


def get_correct_csv_use_case(
    validation_pipeline: ValidationPipelineDecoupled = Depends(get_validation_pipeline),
) -> CorrectCsvUseCase:
    """Provide correct CSV use case."""
    return CorrectCsvUseCase(validation_pipeline)


def get_validate_row_use_case(
    validation_pipeline: ValidationPipelineDecoupled = Depends(get_validation_pipeline),
) -> ValidateRowUseCase:
    """Provide validate row use case."""
    return ValidateRowUseCase(validation_pipeline)


def get_correlation_id(
    x_correlation_id: Optional[str] = Header(None, alias="X-Correlation-Id")
) -> str:
    """Generate or return correlation ID for request tracking."""
    return x_correlation_id or str(uuid.uuid4())


def problem_response(problem: ProblemDetail) -> JSONResponse:
    """Create a problem+json response."""
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


async def validate_file_type(file: UploadFile, correlation_id: str) -> Optional[JSONResponse]:
    """Validate that the uploaded file is a CSV."""
    if not file.filename or not file.filename.lower().endswith('.csv'):
        return problem_response(ProblemDetail(
            type="/errors/invalid-file-type",
            title="Invalid File Type",
            status=415,
            detail="File must be a CSV file",
            instance="/api/v1/validate",
            correlation_id=correlation_id
        ))
    return None


async def validate_file_size(file: UploadFile, correlation_id: str, endpoint: str) -> Optional[JSONResponse]:
    """Validate that the file size is within limits."""
    if file.size and file.size > MAX_FILE_SIZE:
        return problem_response(FileSizeProblemDetail(
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE/1024/1024:.0f}MB",
            instance=endpoint,
            max_size_bytes=MAX_FILE_SIZE,
            actual_size_bytes=file.size,
            correlation_id=correlation_id
        ))
    return None


def parse_json_options(options: Optional[str], correlation_id: str, endpoint: str) -> Union[Dict, JSONResponse]:
    """Parse JSON options string."""
    if not options:
        return {}
    
    try:
        return json.loads(options)
    except json.JSONDecodeError:
        return problem_response(ValidationProblemDetail(
            detail="Invalid JSON in options parameter",
            instance=endpoint,
            extensions={"field": "options"},
            correlation_id=correlation_id
        ))


@router.post(
    "/validate-clean",
    response_model=ValidationResult,
    responses={
        202: {"model": AsyncJobResponse, "description": "Request accepted for async processing"},
        400: {"model": ProblemDetail, "description": "Bad request"},
        413: {"model": FileSizeProblemDetail, "description": "File too large"},
        415: {"model": ProblemDetail, "description": "Unsupported media type"},
        422: {"model": ValidationProblemDetail, "description": "Validation error"},
        429: {"model": RateLimitProblemDetail, "description": "Rate limit exceeded"}
    },
    operation_id="validateCsvClean"
)
async def validate_csv_clean(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="CSV file to validate"),
    marketplace: Marketplace = Form(..., description="Target marketplace"),
    category: Category = Form(..., description="Product category"),
    auto_fix: bool = Form(True, description="Automatically fix issues when possible"),
    options: Optional[str] = Form(None, description="Additional options as JSON"),
    correlation_id: str = Depends(get_correlation_id),
    use_case: ValidateCsvUseCase = Depends(get_validate_csv_use_case),
):
    """
    Validate a CSV file - Clean Architecture implementation.
    
    This endpoint:
    - Only handles HTTP concerns (file upload, response formatting)
    - Delegates business logic to ValidateCsvUseCase
    - Returns structured validation results
    """
    
    # HTTP Layer: Validate file type
    error_response = await validate_file_type(file, correlation_id)
    if error_response:
        return error_response
    
    # HTTP Layer: Validate file size
    error_response = await validate_file_size(file, correlation_id, "/api/v1/validate-clean")
    if error_response:
        return error_response
    
    # HTTP Layer: Parse options
    parsed_options = parse_json_options(options, correlation_id, "/api/v1/validate-clean")
    if isinstance(parsed_options, JSONResponse):
        return parsed_options
    
    # HTTP Layer: Handle async for large files
    if file.size and file.size > MAX_SYNC_FILE_SIZE:
        job_id = str(uuid.uuid4())
        
        background_tasks.add_task(
            process_validation_async_clean,
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
    
    # HTTP Layer: Read file content
    # Note: CSV validation requires the entire DataFrame in memory for cross-row validations.
    # For true streaming, we'd need to redesign the validation pipeline to work with chunks.
    # Current limits: <5MB sync, 5-50MB async, >50MB rejected
    try:
        content = await file.read()
    except OSError as e:
        return problem_response(ProblemDetail(
            type="/errors/file-os-error",
            title="File Access Error",
            status=400,
            detail=f"An OS error occurred while reading the file: {str(e)}. Please check the file and try again.",
            instance="/api/v1/validate-clean",
            correlation_id=correlation_id
        ))
    except Exception as e:
        return problem_response(ProblemDetail(
            type="/errors/file-read-error",
            title="File Read Error",
            status=400,
            detail=f"An unexpected error occurred while reading the file: {str(e)}. Please try again or contact support if the problem persists.",
            instance="/api/v1/validate-clean",
            correlation_id=correlation_id
        ))
    
    try:
        csv_str = content.decode('utf-8', errors='strict')
    except UnicodeDecodeError as e:
        return problem_response(ProblemDetail(
            type="/errors/file-decode-error",
            title="File Decode Error",
            status=400,
            detail="The uploaded file could not be decoded as UTF-8. Please ensure the file is a valid UTF-8 encoded CSV.",
            instance="/api/v1/validate-clean",
            correlation_id=correlation_id
        ))
    
    # Business Layer: Execute use case
    try:
        use_case_input = ValidateCsvInput(
            csv_content=csv_str,
            marketplace=marketplace,
            category=category,
            auto_fix=auto_fix,
            options=parsed_options,
        )
        result = await use_case.execute(use_case_input)
        return result
        
    except ValueError as e:
        return problem_response(ValidationProblemDetail(
            detail=str(e),
            instance="/api/v1/validate-clean",
            correlation_id=correlation_id
        ))
    except Exception as e:
        logger.exception("Error in validation use case")
        return problem_response(ProblemDetail(
            type="/errors/processing-error",
            title="Processing Error",
            status=500,
            detail=f"Error processing CSV: {str(e)}",
            instance="/api/v1/validate-clean",
            correlation_id=correlation_id
        ))


@router.post(
    "/correct-clean",
    response_model=None,
    responses={
        200: {"description": "Corrected CSV file", "content": {"text/csv": {}}},
        202: {"model": AsyncJobResponse, "description": "Request accepted for async processing"},
        400: {"model": ProblemDetail, "description": "Bad request"},
        413: {"model": FileSizeProblemDetail, "description": "File too large"},
        415: {"model": ProblemDetail, "description": "Unsupported media type"},
        422: {"model": ValidationProblemDetail, "description": "Validation error"},
    },
    operation_id="correctCsvClean"
)
async def correct_csv_clean(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="CSV file to correct"),
    marketplace: Marketplace = Form(..., description="Target marketplace"),
    category: Category = Form(..., description="Product category"),
    options: Optional[str] = Form(None, description="Additional options as JSON"),
    correlation_id: str = Depends(get_correlation_id),
    use_case: CorrectCsvUseCase = Depends(get_correct_csv_use_case),
):
    """
    Correct a CSV file - Clean Architecture implementation.
    
    This endpoint:
    - Only handles HTTP concerns (file upload, response streaming)
    - Delegates business logic to CorrectCsvUseCase
    - Returns corrected CSV as downloadable file
    """
    
    # HTTP Layer: Validate file type
    error_response = await validate_file_type(file, correlation_id)
    if error_response:
        return error_response
    
    # HTTP Layer: Validate file size
    error_response = await validate_file_size(file, correlation_id, "/api/v1/correct-clean")
    if error_response:
        return error_response
    
    # HTTP Layer: Parse options
    parsed_options = parse_json_options(options, correlation_id, "/api/v1/correct-clean")
    if isinstance(parsed_options, JSONResponse):
        return parsed_options
    
    # HTTP Layer: Handle async for large files
    if file.size and file.size > MAX_SYNC_FILE_SIZE:
        job_id = str(uuid.uuid4())
        
        background_tasks.add_task(
            process_correction_async_clean,
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
    
    # HTTP Layer: Read file content
    # Note: CSV validation requires the entire DataFrame in memory for cross-row validations.
    # For true streaming, we'd need to redesign the validation pipeline to work with chunks.
    # Current limits: <5MB sync, 5-50MB async, >50MB rejected
    try:
        content = await file.read()
    except OSError as e:
        return problem_response(ProblemDetail(
            type="/errors/file-os-error",
            title="File Access Error",
            status=400,
            detail=f"An OS error occurred while reading the file: {str(e)}. Please check the file and try again.",
            instance="/api/v1/correct-clean",
            correlation_id=correlation_id
        ))
    except Exception as e:
        return problem_response(ProblemDetail(
            type="/errors/file-read-error",
            title="File Read Error",
            status=400,
            detail=f"An unexpected error occurred while reading the file: {str(e)}. Please try again or contact support if the problem persists.",
            instance="/api/v1/correct-clean",
            correlation_id=correlation_id
        ))
    
    try:
        csv_str = content.decode('utf-8', errors='strict')
    except UnicodeDecodeError as e:
        return problem_response(ProblemDetail(
            type="/errors/file-decode-error",
            title="File Decode Error",
            status=400,
            detail="The uploaded file could not be decoded as UTF-8. Please ensure the file is a valid UTF-8 encoded CSV.",
            instance="/api/v1/correct-clean",
            correlation_id=correlation_id
        ))
    
    # Business Layer: Execute use case
    try:
        use_case_input = CorrectCsvInput(
            csv_content=csv_str,
            marketplace=marketplace,
            category=category,
            options=parsed_options,
            original_filename=file.filename,
        )

        result = await use_case.execute(use_case_input)
        
        # HTTP Layer: Prepare response with streaming
        def csv_streamer(csv_text: str, chunk_size: int = 8192):
            encoded = csv_text.encode('utf-8')
            for i in range(0, len(encoded), chunk_size):
                yield encoded[i:i+chunk_size]
        
        # Safely split filename, handling files without extension and dotfiles
        base, ext = os.path.splitext(result.original_filename)
        if base:
            original_name = base
        else:
            # For files like '.config', base is '', so use the full filename (which is the dotfile)
            original_name = result.original_filename
        corrected_filename = f"{original_name}_corrected.csv"
        
        return StreamingResponse(
            csv_streamer(result.corrected_csv),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={corrected_filename}",
                "X-Total-Corrections": str(result.total_corrections),
                "X-Total-Errors": str(result.total_errors),
                "X-Total-Warnings": str(result.total_warnings),
                "X-Processing-Time": f"{result.processing_time:.2f}s",
                "X-Correlation-Id": correlation_id,
                "X-Job-Id": result.job_id
            }
        )
        
    except ValueError as e:
        return problem_response(ValidationProblemDetail(
            detail=str(e),
            instance="/api/v1/correct-clean",
            correlation_id=correlation_id
        ))
    except Exception as e:
        logger.exception("Error in correction use case")
        return problem_response(ProblemDetail(
            type="/errors/processing-error",
            title="Processing Error",
            status=500,
            detail=f"Error correcting CSV: {str(e)}",
            instance="/api/v1/correct-clean",
            correlation_id=correlation_id
        ))


@router.post(
    "/validate-row-clean",
    response_model=Dict[str, Any],
    responses={
        400: {"model": ProblemDetail, "description": "Bad request"},
        422: {"model": ValidationProblemDetail, "description": "Validation error"}
    },
    operation_id="validateRowClean"
)
async def validate_row_clean(
    row_data: Dict[str, Any],
    marketplace: Marketplace = Query(..., description="Target marketplace"),
    category: Optional[Category] = Query(None, description="Product category"),
    auto_fix: bool = Query(True, description="Automatically fix issues when possible"),
    row_number: int = Query(1, description="Row number for context", ge=1),
    correlation_id: str = Depends(get_correlation_id),
    use_case: ValidateRowUseCase = Depends(get_validate_row_use_case),
):
    """
    Validate a single row - Clean Architecture implementation.
    
    This endpoint:
    - Only handles HTTP concerns (request/response)
    - Delegates business logic to ValidateRowUseCase
    - Returns structured validation results
    """
    
    # Business Layer: Execute use case
    try:
        use_case_input = ValidateRowInput(
            row_data=row_data,
            marketplace=marketplace,
            category=category,
            row_number=row_number,
            auto_fix=auto_fix,
        )

        result = await use_case.execute(use_case_input)
        
        # HTTP Layer: Format response
        return {
            "original_row": result.original_row,
            "fixed_row": result.fixed_row,
            "validation_items": result.validation_items,
            "has_errors": result.has_errors,
            "has_warnings": result.has_warnings,
            "auto_fix_applied": result.auto_fix_applied
        }
        
    except Exception as e:
        logger.exception("Error in row validation use case")
        return problem_response(ProblemDetail(
            type="/errors/processing-error",
            title="Processing Error",
            status=500,
            detail=f"Error validating row: {str(e)}",
            instance="/api/v1/validate-row-clean",
            correlation_id=correlation_id
        ))


# Async processing functions (infrastructure layer)
async def process_validation_async_clean(
    job_id: str,
    file: UploadFile,
    marketplace: Marketplace,
    category: Category,
    auto_fix: bool,
    options: dict,
    correlation_id: str
):
    """Process validation asynchronously - Clean implementation."""
    # TODO: Implement with proper job queue (Celery/Redis)
    logger.info(f"Processing validation job {job_id} asynchronously")


async def process_correction_async_clean(
    job_id: str,
    file: UploadFile,
    marketplace: Marketplace,
    category: Category,
    options: dict,
    correlation_id: str
):
    """Process correction asynchronously - Clean implementation."""
    # TODO: Implement with proper job queue (Celery/Redis)
    logger.info(f"Processing correction job {job_id} asynchronously")