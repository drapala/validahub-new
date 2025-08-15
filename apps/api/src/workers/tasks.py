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

logger = logging.getLogger(__name__)

# Transient errors that should trigger retry
class TransientError(Exception):
    """Transient error that should be retried."""
    pass


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
        # Update progress: Starting
        update_job_progress(task_id, 10, "Downloading input file")
        
        # Get input file
        input_uri = params.get("input_uri")
        if not input_uri:
            raise ValueError("input_uri is required")
        
        # Download or read file
        csv_content = _download_file(input_uri)
        
        # Update progress: File loaded
        update_job_progress(task_id, 30, "File loaded, starting validation")
        
        # Parse CSV
        df = pd.read_csv(io.StringIO(csv_content))
        total_rows = len(df)
        
        logger.info(f"Loaded CSV with {total_rows} rows")
        
        # Initialize validation pipeline
        rule_engine = RuleEngineService()
        pipeline = ValidationPipeline(rule_engine_service=rule_engine)
        
        # Update progress: Validating
        update_job_progress(task_id, 50, f"Validating {total_rows} rows")
        
        # Perform validation
        marketplace = params.get("marketplace", "mercado_livre")
        category = params.get("category", "general")
        auto_fix = params.get("auto_fix", False)
        
        result = pipeline.validate(
            df=df,
            marketplace=marketplace,
            category=category,
            auto_fix=auto_fix
        )
        
        # Update progress: Saving results
        update_job_progress(task_id, 80, "Saving validation results")
        
        # Prepare result
        validation_result = {
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            "total_rows": result.total_rows,
            "valid_rows": result.valid_rows,
            "error_rows": result.error_rows,
            "warning_rows": result.warning_rows,
            "summary": result.summary.model_dump() if hasattr(result.summary, 'model_dump') else result.summary,
            "validation_items": [
                item.model_dump() if hasattr(item, 'model_dump') else item
                for item in result.validation_items[:100]  # Limit for storage
            ]
        }
        
        # Save result to storage
        result_ref = _save_result(job_id, validation_result)
        
        # Save corrected data if available
        if auto_fix and result.corrected_data is not None:
            corrected_csv = result.corrected_data.to_csv(index=False)
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
                "total_rows": result.total_rows,
                "valid_rows": result.valid_rows,
                "error_rows": result.error_rows,
                "warning_rows": result.warning_rows
            },
            "status": "success"
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
        # For MVP, return mock CSV data
        logger.warning(f"File not found, returning mock data for: {uri}")
        return """sku,title,price,stock,category
SKU001,Product 1,10.99,5,Electronics
SKU002,Product 2,25.50,0,Clothing
,Product 3,-5,10,Electronics
SKU004,,30.00,-1,"""


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
    """Check if error is transient and should be retried."""
    
    transient_messages = [
        "connection",
        "timeout",
        "temporarily",
        "try again",
        "service unavailable"
    ]
    
    error_str = str(error).lower()
    return any(msg in error_str for msg in transient_messages)