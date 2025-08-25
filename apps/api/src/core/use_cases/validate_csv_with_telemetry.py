"""
Validation use case with integrated telemetry.
"""

from typing import Dict, Any, Optional
import time
import hashlib
from pathlib import Path

from ..pipeline.validation_pipeline_decoupled_optimized import ValidationPipelineDecoupledOptimized
from interfaces import IValidator
from ...telemetry.telemetry_service import get_telemetry_service
from ...telemetry.events import EventType, EventSeverity
from ...core.logging_config import get_logger

logger = get_logger(__name__)


class ValidateCSVWithTelemetry:
    """
    Use case for CSV validation with telemetry emission.
    
    Features:
    - Emits telemetry events at key points
    - Tracks performance metrics
    - Monitors error rates
    - Provides detailed observability
    """
    
    def __init__(self, validator: IValidator):
        """
        Initialize use case with validator.
        
        Args:
            validator: Validator implementation
        """
        self.validator = validator
        self.pipeline = ValidationPipelineDecoupledOptimized(validator)
        self.telemetry = get_telemetry_service()
    
    async def execute(
        self,
        job_id: str,
        file_path: str,
        marketplace: str,
        category: Optional[str] = None,
        ruleset: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute CSV validation with telemetry.
        
        Args:
            job_id: Unique job identifier
            file_path: Path to CSV file
            marketplace: Marketplace name
            category: Product category
            ruleset: Ruleset to use
            user_id: User identifier
            **kwargs: Additional parameters
            
        Returns:
            Validation results with telemetry metadata
        """
        # Set telemetry context
        self.telemetry.set_context(
            user_id=user_id,
            job_id=job_id,
            marketplace=marketplace
        )
        
        # Start timing
        start_time = time.time()
        
        # Get file info
        file_info = self._get_file_info(file_path)
        
        # Emit validation started event
        await self.telemetry.emit_validation_started(
            job_id=job_id,
            marketplace=marketplace,
            file_name=file_info["name"],
            file_size=file_info["size"],
            category=category,
            ruleset=ruleset
        )
        
        try:
            # Track validation operation
            async with self.telemetry.track_operation(
                "csv_validation",
                EventType.PERFORMANCE_METRIC,
                marketplace=marketplace
            ):
                # Execute validation
                result = await self.pipeline.validate_csv_async(
                    file_path=file_path,
                    marketplace=marketplace,
                    category=category,
                    ruleset=ruleset,
                    **kwargs
                )
            
            # Calculate metrics
            processing_time_ms = int((time.time() - start_time) * 1000)
            total_rows = result.get("total_rows", 0)
            valid_rows = len(result.get("valid_rows", []))
            invalid_rows = len(result.get("invalid_rows", []))
            
            # Emit validation completed event
            await self.telemetry.emit_validation_completed(
                job_id=job_id,
                marketplace=marketplace,
                total_rows=total_rows,
                valid_rows=valid_rows,
                invalid_rows=invalid_rows,
                processing_time_ms=processing_time_ms,
                category=category,
                ruleset=ruleset,
                file_hash=file_info["hash"]
            )
            
            # Emit performance metrics
            if total_rows > 0:
                # Success rate
                success_rate = (valid_rows / total_rows) * 100
                await self.telemetry.emit_performance_metric(
                    metric_name="validation_success_rate",
                    metric_value=success_rate,
                    metric_unit="percentage",
                    operation=f"validation_{marketplace}"
                )
                
                # Processing speed
                rows_per_second = total_rows / (processing_time_ms / 1000)
                await self.telemetry.emit_performance_metric(
                    metric_name="validation_throughput",
                    metric_value=rows_per_second,
                    metric_unit="rows_per_second",
                    operation=f"validation_{marketplace}"
                )
            
            # Track error patterns
            if invalid_rows > 0:
                await self._emit_error_telemetry(result, job_id, marketplace)
            
            # Add telemetry metadata to result
            result["telemetry"] = {
                "job_id": job_id,
                "processing_time_ms": processing_time_ms,
                "events_emitted": True,
                "file_hash": file_info["hash"]
            }
            
            return result
            
        except Exception as e:
            # Emit validation failed event
            await self.telemetry.emit_validation_failed(
                job_id=job_id,
                marketplace=marketplace,
                error_message=str(e)
            )
            
            # Emit system error
            await self.telemetry.emit_system_error(
                component="validation_use_case",
                message=f"Validation failed for job {job_id}",
                error_type=type(e).__name__,
                stack_trace=str(e)
            )
            
            # Re-raise the error
            raise
        
        finally:
            # Clear telemetry context
            self.telemetry.clear_context()
    
    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get file information for telemetry.
        
        Args:
            file_path: Path to file
            
        Returns:
            File information dictionary
        """
        path = Path(file_path)
        
        if not path.exists():
            return {
                "name": path.name,
                "size": 0,
                "hash": None
            }
        
        # Get file size
        file_size = path.stat().st_size
        
        # Calculate file hash (first 1MB for performance)
        file_hash = None
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(1024 * 1024)  # Read first 1MB
                file_hash = hashlib.sha256(chunk).hexdigest()
        except Exception as e:
            logger.warning(f"Failed to calculate file hash: {e}")
        
        return {
            "name": path.name,
            "size": file_size,
            "hash": file_hash
        }
    
    async def _emit_error_telemetry(
        self,
        result: Dict[str, Any],
        job_id: str,
        marketplace: str
    ):
        """
        Emit telemetry for validation errors.
        
        Args:
            result: Validation result
            job_id: Job identifier
            marketplace: Marketplace name
        """
        # Count error types
        error_counts = {}
        for row in result.get("invalid_rows", []):
            for error in row.get("errors", []):
                error_type = error.get("field", "unknown")
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        # Emit metrics for each error type
        for error_type, count in error_counts.items():
            await self.telemetry.emit_performance_metric(
                metric_name=f"validation_error_{error_type}",
                metric_value=count,
                metric_unit="count",
                operation=f"validation_{marketplace}"
            )