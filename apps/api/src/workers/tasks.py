"""
Celery tasks for async job processing.
"""

import os
import json
import logging
import tempfile
from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
import io
import boto3
from botocore.exceptions import ClientError

from .celery_app import celery_app, DatabaseTask, update_job_progress
from ..services.rule_engine_service import RuleEngineService
from ..core.pipeline.validation_pipeline import ValidationPipeline
from ..services.csv_validation_service import CSVValidationService
from ..exceptions import TransientError
from ..telemetry.job_telemetry import get_job_telemetry
from ..telemetry.metrics import MetricsCollector, ValidationMetrics

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="validate_csv_job",
    autoretry_for=(TransientError, ConnectionError, TimeoutError),
    retry_backoff=2,
    retry_jitter=True,
    max_retries=5,
    time_limit=300,
    soft_time_limit=270
)
def validate_csv_job(
    self,
    job_id: str,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate CSV file using rule engine.
    
    Args:
        job_id: Job UUID
        params: {
            "input_uri": "s3://bucket/key.csv" or file path,
            "marketplace": "mercado_livre",
            "category": "electronics",
            "ruleset": "default",
            "auto_fix": true/false
        }
    
    Returns:
        {
            "result_ref": "s3://bucket/results/job_id.json",
            "summary": {...},
            "status": "success"
        }
    """
    
    task_id = self.request.id
    logger.info(f"Starting validate_csv_job: job_id={job_id}, task_id={task_id}")
    
    try:
        # Track start time for metrics
        start_time = datetime.utcnow()
        
        # Initialize services
        validation_service = CSVValidationService()
        telemetry = get_job_telemetry()
        
        # Update progress: Starting
        update_job_progress(task_id, 10, "Downloading input file")
        
        # Emit progress with enhanced metrics
        telemetry.emit_job_progress(
            job_id=job_id, 
            task_name="validate_csv_job", 
            progress=10, 
            message="Downloading input file", 
            params=params
        )
        
        # Get input file
        input_uri = params.get("input_uri")
        if not input_uri:
            raise ValueError("input_uri is required")
        
        # Download or read file
        csv_content = _download_file(input_uri)
        
        # Update progress: File loaded
        update_job_progress(task_id, 30, "File loaded, starting validation")
        
        # Emit progress with payload size metric
        progress_metrics = {
            "payload_size_bytes": len(csv_content.encode('utf-8'))
        }
        telemetry.emit_job_progress(
            job_id=job_id,
            task_name="validate_csv_job",
            progress=30,
            message=f"File loaded ({progress_metrics['payload_size_bytes']} bytes), starting validation",
            params={**params, "metrics": progress_metrics}
        )
        
        logger.info(f"Loaded CSV with {len(csv_content)} bytes")
        
        # Update progress: Validating
        update_job_progress(task_id, 50, "Validating data")
        telemetry.emit_job_progress(
            job_id=job_id,
            task_name="validate_csv_job",
            progress=50,
            message="Validating data",
            params=params
        )
        
        # Extract parameters
        marketplace = params.get("marketplace", "mercado_livre")
        category = params.get("category", "general")
        ruleset = params.get("ruleset", "default")
        auto_fix = params.get("auto_fix", False)
        
        # Use domain service for validation
        validation_result, corrected_csv = validation_service.validate_csv_content(
            csv_content=csv_content,
            marketplace=marketplace,
            category=category,
            ruleset=ruleset,
            auto_fix=auto_fix
        )
        
        # Calculate standardized business metrics
        validation_metrics = MetricsCollector.collect_validation_metrics(
            csv_content=csv_content,
            validation_result=validation_result,
            processing_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000) if 'start_time' in locals() else None
        )
        
        # Enrich with business context
        validation_metrics = MetricsCollector.enrich_with_business_context(
            validation_metrics, params
        )
        
        # Calculate error rates
        error_rates = MetricsCollector.calculate_error_rates(validation_metrics)
        
        # Convert to dict for serialization
        metrics = validation_metrics.to_dict()
        metrics.update(error_rates)
        
        # Update progress: Saving results with metrics
        update_job_progress(task_id, 80, "Saving validation results")
        
        # Emit progress with preliminary metrics
        telemetry.emit_job_progress(
            job_id=job_id,
            task_name="validate_csv_job",
            progress=80,
            message=f"Saving results ({validation_result['total_rows']} rows processed)",
            params={**params, "preliminary_metrics": {
                "total_rows": validation_result["total_rows"],
                "error_rows": validation_result["error_rows"]
            }}
        )
        
        # Add metadata to validation result
        validation_result["job_id"] = job_id
        validation_result["timestamp"] = datetime.utcnow().isoformat()
        
        # Save result to storage
        result_ref = _save_result(job_id, validation_result)
        
        # Save corrected data if available
        if corrected_csv:
            corrected_ref = _save_file(
                f"corrected/{job_id}.csv",
                corrected_csv.encode('utf-8')
            )
            validation_result["corrected_file"] = corrected_ref
        
        # Update progress: Complete
        update_job_progress(task_id, 100, "Validation completed")
        
        logger.info(f"Validation completed: job_id={job_id}, result_ref={result_ref}")
        
        return {
            "result_ref": result_ref,
            "summary": {
                "total_rows": validation_result["total_rows"],
                "valid_rows": validation_result["valid_rows"],
                "error_rows": validation_result["error_rows"],
                "warning_rows": validation_result["warning_rows"]
            },
            "status": "success",
            "marketplace": marketplace,
            "category": category,
            "metrics": metrics
        }
        
    except Exception as e:
        logger.error(f"Error in validate_csv_job: {e}", exc_info=True)
        
        # Check if it's a transient error that should be retried
        if _is_transient_error(e):
            raise TransientError(f"Transient error: {e}") from e
        
        # Non-transient error, fail the job
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="correct_csv_job",
    autoretry_for=(TransientError,),
    retry_backoff=2,
    max_retries=3
)
def correct_csv_job(
    self,
    job_id: str,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """Apply corrections to CSV file."""
    # Similar to validate_csv_job but always with auto_fix=True
    params["auto_fix"] = True
    return validate_csv_job(self, job_id, params)


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="sync_connector_job",
    autoretry_for=(TransientError,),
    retry_backoff=2,
    max_retries=3
)
def sync_connector_job(
    self,
    job_id: str,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """Sync data from external connector."""
    
    task_id = self.request.id
    logger.info(f"Starting sync_connector_job: job_id={job_id}")
    
    # Placeholder for connector sync logic
    update_job_progress(task_id, 50, "Syncing connector (mock)")
    
    return {
        "result_ref": f"s3://validahub/results/{job_id}.json",
        "status": "success",
        "message": "Connector sync not yet implemented"
    }


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="generate_report_job"
)
def generate_report_job(
    self,
    job_id: str,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate analytics report."""
    
    task_id = self.request.id
    logger.info(f"Starting generate_report_job: job_id={job_id}")
    
    # Placeholder for report generation
    update_job_progress(task_id, 100, "Report generated (mock)")
    
    return {
        "result_ref": f"s3://validahub/reports/{job_id}.pdf",
        "status": "success"
    }


# Helper functions

def _download_file(uri: str) -> str:
    """Download file from S3 or local path."""
    
    if uri.startswith("s3://"):
        # Parse S3 URI
        parts = uri.replace("s3://", "").split("/", 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ""
        
        # Download from S3
        s3 = boto3.client("s3")
        try:
            response = s3.get_object(Bucket=bucket, Key=key)
            return response["Body"].read().decode("utf-8")
        except ClientError as e:
            logger.error(f"Error downloading from S3: {e}")
            raise
    
    elif os.path.exists(uri):
        # Read local file
        with open(uri, "r", encoding="utf-8") as f:
            return f.read()
    
    else:
        # Raise exception instead of silently using mock data
        logger.error(f"File not found: {uri}")
        raise FileNotFoundError(f"File not found: {uri}")


def _save_result(job_id: str, result: Dict[str, Any]) -> str:
    """Save job result to storage."""
    
    # For MVP, save to local temp file
    # In production, this would upload to S3
    
    result_json = json.dumps(result, indent=2, default=str)
    
    # Check if S3 is configured
    if os.getenv("AWS_ACCESS_KEY_ID"):
        try:
            s3 = boto3.client("s3")
            bucket = os.getenv("S3_BUCKET", "validahub")
            key = f"results/{job_id}.json"
            
            s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=result_json.encode("utf-8"),
                ContentType="application/json"
            )
            
            return f"s3://{bucket}/{key}"
        except Exception as e:
            logger.error(f"Error saving to S3: {e}")
    
    # Fallback to local storage
    temp_dir = os.getenv("TEMP_STORAGE_PATH", "/tmp/validahub")
    os.makedirs(temp_dir, exist_ok=True)
    
    file_path = os.path.join(temp_dir, f"{job_id}.json")
    with open(file_path, "w") as f:
        f.write(result_json)
    
    return f"file://{file_path}"


def _save_file(path: str, content: bytes) -> str:
    """Save file to storage."""
    
    # Similar to _save_result but for binary files
    if os.getenv("AWS_ACCESS_KEY_ID"):
        try:
            s3 = boto3.client("s3")
            bucket = os.getenv("S3_BUCKET", "validahub")
            
            s3.put_object(
                Bucket=bucket,
                Key=path,
                Body=content
            )
            
            return f"s3://{bucket}/{path}"
        except Exception as e:
            logger.error(f"Error saving file to S3: {e}")
    
    # Fallback to local
    temp_dir = os.getenv("TEMP_STORAGE_PATH", "/tmp/validahub")
    os.makedirs(os.path.dirname(os.path.join(temp_dir, path)), exist_ok=True)
    
    file_path = os.path.join(temp_dir, path)
    with open(file_path, "wb") as f:
        f.write(content)
    
    return f"file://{file_path}"


def _is_transient_error(error: Exception) -> bool:
    """
    Check if error is transient and should be retried.
    
    Uses exception type checking for reliable detection of transient errors.
    String matching is avoided to prevent false positives.
    """
    
    # Import AWS exceptions only if needed
    try:
        from botocore.exceptions import (
            EndpointConnectionError, 
            ConnectTimeoutError, 
            ReadTimeoutError, 
            ConnectionClosedError,
            ClientError
        )
        
        # Check for specific AWS transient errors
        if isinstance(error, ClientError):
            error_code = error.response.get('Error', {}).get('Code', '')
            transient_error_codes = [
                'ThrottlingException',
                'TooManyRequestsException',
                'RequestLimitExceeded',
                'ServiceUnavailable',
                'RequestTimeout',
                'InternalServerError',
                'InternalError'
            ]
            if error_code in transient_error_codes:
                return True
        
        # AWS connection errors
        aws_transient_types = (
            EndpointConnectionError,
            ConnectTimeoutError,
            ReadTimeoutError,
            ConnectionClosedError,
        )
        if isinstance(error, aws_transient_types):
            return True
            
    except ImportError:
        # botocore not available, skip AWS-specific checks
        pass
    
    # Standard Python transient exception types
    transient_types = (
        ConnectionError,      # Network connection errors
        TimeoutError,        # Operation timeouts
        BrokenPipeError,     # Broken network pipe
        ConnectionResetError, # Connection reset by peer
        ConnectionAbortedError, # Connection aborted
    )
    
    if isinstance(error, transient_types):
        return True
    
    # Check for specific OSError types that are transient
    if isinstance(error, OSError):
        # errno values that indicate transient network issues
        import errno
        transient_errno = [
            errno.EAGAIN,      # Resource temporarily unavailable
            errno.EWOULDBLOCK, # Operation would block
            errno.EINPROGRESS, # Operation in progress
            errno.ETIMEDOUT,   # Connection timed out
            errno.ECONNRESET,  # Connection reset by peer
            errno.ECONNREFUSED, # Connection refused
            errno.EHOSTUNREACH, # No route to host
            errno.ENETUNREACH,  # Network unreachable
            errno.ENETDOWN,     # Network is down
        ]
        if hasattr(error, 'errno') and error.errno in transient_errno:
            return True
    
    # Default: not a transient error
    # Avoid string matching to prevent false positives
    logger.debug(f"Error not identified as transient: {type(error).__name__}: {error}")
    return False