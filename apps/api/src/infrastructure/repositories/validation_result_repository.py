"""
Repository for ValidationResult entities.
Handles all database operations for validation results.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, case, Integer
from src.core.logging_config import get_logger

from .base_repository import BaseRepository
from src.models.validation_result import ValidationResult
from src.core.result import Result, Ok, Err

logger = get_logger(__name__)


class ValidationResultRepository(BaseRepository[ValidationResult]):
    """
    Repository for ValidationResult entities.
    
    This repository extends BaseRepository with validation-result-specific
    operations like finding by job, marketplace, statistics, etc.
    """
    
    def __init__(self, db: Session):
        """
        Initialize ValidationResultRepository.
        
        Args:
            db: Database session
        """
        super().__init__(ValidationResult, db)
    
    def find_by_job_id(
        self, 
        job_id: str
    ) -> Result[Optional[ValidationResult], str]:
        """
        Find validation result by job ID.
        
        Args:
            job_id: Job ID
            
        Returns:
            Result containing validation result or None if not found
        """
        try:
            result = self.db.query(ValidationResult).filter(
                ValidationResult.job_id == job_id
            ).first()
            return Ok(result)
        except Exception as e:
            logger.error(f"Failed to find validation result by job {job_id}: {e}")
            return Err(str(e))
    
    def find_by_file_id(
        self, 
        file_id: str
    ) -> Result[List[ValidationResult], str]:
        """
        Find all validation results for a file.
        
        Args:
            file_id: File ID
            
        Returns:
            Result containing list of validation results or error
        """
        try:
            results = self.db.query(ValidationResult).filter(
                ValidationResult.file_id == file_id
            ).order_by(
                desc(ValidationResult.created_at)
            ).all()
            return Ok(results)
        except Exception as e:
            logger.error(f"Failed to find validation results by file {file_id}: {e}")
            return Err(str(e))
    
    def find_by_marketplace(
        self,
        marketplace: str,
        skip: int = 0,
        limit: int = 100
    ) -> Result[List[ValidationResult], str]:
        """
        Find validation results by marketplace.
        
        Args:
            marketplace: Marketplace name
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Result containing list of validation results or error
        """
        try:
            results = self.db.query(ValidationResult).filter(
                ValidationResult.marketplace == marketplace
            ).order_by(
                desc(ValidationResult.created_at)
            ).offset(skip).limit(limit).all()
            return Ok(results)
        except Exception as e:
            logger.error(f"Failed to find results by marketplace {marketplace}: {e}")
            return Err(str(e))
    
    def find_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> Result[List[ValidationResult], str]:
        """
        Find validation results by status.
        
        Args:
            status: Result status (pending, processing, completed, failed)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Result containing list of validation results or error
        """
        try:
            results = self.db.query(ValidationResult).filter(
                ValidationResult.status == status
            ).order_by(
                desc(ValidationResult.created_at)
            ).offset(skip).limit(limit).all()
            return Ok(results)
        except Exception as e:
            logger.error(f"Failed to find results by status {status}: {e}")
            return Err(str(e))
    
    def find_recent_results(
        self,
        hours: int = 24,
        skip: int = 0,
        limit: int = 100
    ) -> Result[List[ValidationResult], str]:
        """
        Find validation results created within the last N hours.
        
        Args:
            hours: Number of hours to look back
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Result containing list of validation results or error
        """
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            results = self.db.query(ValidationResult).filter(
                ValidationResult.created_at >= cutoff_time
            ).order_by(
                desc(ValidationResult.created_at)
            ).offset(skip).limit(limit).all()
            return Ok(results)
        except Exception as e:
            logger.error(f"Failed to find recent results: {e}")
            return Err(str(e))
    
    def find_failed_results(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> Result[List[ValidationResult], str]:
        """
        Find validation results with errors.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Result containing list of failed validation results or error
        """
        try:
            results = self.db.query(ValidationResult).filter(
                or_(
                    ValidationResult.status == "failed",
                    ValidationResult.invalid_rows > 0
                )
            ).order_by(
                desc(ValidationResult.created_at)
            ).offset(skip).limit(limit).all()
            return Ok(results)
        except Exception as e:
            logger.error(f"Failed to find failed results: {e}")
            return Err(str(e))
    
    def update_status(
        self,
        result_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> Result[bool, str]:
        """
        Update validation result status.
        
        Args:
            result_id: Result ID
            status: New status
            error_message: Optional error message
            
        Returns:
            Result containing success boolean or error
        """
        try:
            result = self.db.query(ValidationResult).filter(
                ValidationResult.id == result_id
            ).first()
            
            if not result:
                return Err("ValidationResult not found")
            
            result.status = status
            if error_message:
                result.error_message = error_message
            
            if status in ["completed", "failed"]:
                result.completed_at = datetime.now(timezone.utc)
            
            self.db.flush()
            return Ok(True)
        except Exception as e:
            logger.error(f"Failed to update result {result_id} status: {e}")
            self.db.rollback()
            return Err(str(e))
    
    def get_marketplace_statistics(
        self,
        marketplace: Optional[str] = None
    ) -> Result[Dict[str, Any], str]:
        """
        Get validation statistics by marketplace.
        
        Args:
            marketplace: Optional marketplace filter
            
        Returns:
            Result containing statistics dictionary or error
        """
        try:
            # Build base filter conditions
            base_filters = []
            if marketplace:
                base_filters.append(ValidationResult.marketplace == marketplace)
            
            # Total validations
            total_validations = self.db.query(ValidationResult).filter(*base_filters).count()
            
            # Success rate
            successful = self.db.query(ValidationResult).filter(
                *base_filters,
                ValidationResult.invalid_rows == 0
            ).count()
            success_rate = (successful / total_validations * 100) if total_validations > 0 else 0
            
            # Average processing time
            avg_time = self.db.query(
                func.avg(ValidationResult.processing_time_ms)
            ).filter(
                *base_filters,
                ValidationResult.processing_time_ms.isnot(None)
            ).scalar() or 0
            
            # Total rows processed
            total_rows = self.db.query(
                func.sum(ValidationResult.total_rows)
            ).filter(
                *base_filters
            ).scalar() or 0
            
            # Error rate by category
            error_by_category = dict(
                self.db.query(
                    ValidationResult.category,
                    func.avg(ValidationResult.invalid_rows * 100.0 / ValidationResult.total_rows)
                ).filter(
                    *base_filters,
                    ValidationResult.category.isnot(None)
                ).group_by(ValidationResult.category).all()
            )
            
            return Ok({
                "marketplace": marketplace or "all",
                "total_validations": total_validations,
                "successful_validations": successful,
                "success_rate": round(success_rate, 2),
                "average_processing_time_ms": round(float(avg_time), 2),
                "total_rows_processed": total_rows,
                "error_rate_by_category": {
                    k: round(v, 2) for k, v in error_by_category.items()
                }
            })
        except Exception as e:
            logger.error(f"Failed to get marketplace statistics: {e}")
            return Err(str(e))
    
    def get_daily_statistics(
        self,
        days: int = 7
    ) -> Result[List[Dict[str, Any]], str]:
        """
        Get daily validation statistics for the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Result containing list of daily statistics or error
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Group by date
            daily_stats = self.db.query(
                func.date(ValidationResult.created_at).label('date'),
                func.count(ValidationResult.id).label('total'),
                func.sum(ValidationResult.total_rows).label('rows_processed'),
                func.avg(ValidationResult.processing_time_ms).label('avg_time'),
                func.sum(
                    case(
                        [(ValidationResult.invalid_rows == 0, 1)],
                        else_=0
                    )
                ).label('successful')
            ).filter(
                ValidationResult.created_at >= cutoff_date
            ).group_by(
                func.date(ValidationResult.created_at)
            ).order_by(
                func.date(ValidationResult.created_at)
            ).all()
            
            return Ok([
                {
                    "date": str(stat.date),
                    "total_validations": stat.total,
                    "rows_processed": stat.rows_processed or 0,
                    "average_processing_time_ms": round(float(stat.avg_time or 0), 2),
                    "successful_validations": stat.successful or 0,
                    "success_rate": round(
                        (stat.successful / stat.total * 100) if stat.total > 0 else 0, 
                        2
                    )
                }
                for stat in daily_stats
            ])
        except Exception as e:
            logger.error(f"Failed to get daily statistics: {e}")
            return Err(str(e))
    
    def cleanup_old_results(
        self,
        days_old: int
    ) -> Result[int, str]:
        """
        Delete validation results older than specified days.
        
        Args:
            days_old: Age threshold in days
            
        Returns:
            Result containing number of deleted results or error
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)
            
            count = self.db.query(ValidationResult).filter(
                ValidationResult.created_at < cutoff_date
            ).count()
            
            self.db.query(ValidationResult).filter(
                ValidationResult.created_at < cutoff_date
            ).delete()
            
            self.db.flush()
            return Ok(count)
        except Exception as e:
            logger.error(f"Failed to cleanup old results: {e}")
            self.db.rollback()
            return Err(str(e))