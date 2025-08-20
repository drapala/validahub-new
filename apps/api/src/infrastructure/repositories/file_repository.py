"""
Repository for File entities.
Handles all database operations for files.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
import logging

from .base_repository import BaseRepository
from ...models.file import File
from ...core.result import Result, Ok, Err

logger = logging.getLogger(__name__)


class FileRepository(BaseRepository[File]):
    """
    Repository for File entities.
    
    This repository extends BaseRepository with file-specific
    operations like finding by job, S3 operations, etc.
    """
    
    def __init__(self, db: Session):
        """
        Initialize FileRepository.
        
        Args:
            db: Database session
        """
        super().__init__(File, db)
    
    def find_by_job_id(
        self, 
        job_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> Result[List[File], str]:
        """
        Find all files belonging to a job.
        
        Args:
            job_id: Job ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Result containing list of files or error
        """
        try:
            files = self.db.query(File).filter(
                File.job_id == job_id
            ).order_by(
                desc(File.created_at)
            ).offset(skip).limit(limit).all()
            return Ok(files)
        except Exception as e:
            logger.error(f"Failed to find files by job {job_id}: {e}")
            return Err(str(e))
    
    def find_by_s3_key(self, s3_key: str) -> Result[Optional[File], str]:
        """
        Find file by S3 key.
        
        Args:
            s3_key: S3 key of the file
            
        Returns:
            Result containing file or None if not found
        """
        try:
            file = self.db.query(File).filter(
                File.s3_key == s3_key
            ).first()
            return Ok(file)
        except Exception as e:
            logger.error(f"Failed to find file by S3 key {s3_key}: {e}")
            return Err(str(e))
    
    def find_by_filename(
        self,
        filename: str,
        job_id: Optional[str] = None
    ) -> Result[List[File], str]:
        """
        Find files by filename, optionally filtered by job.
        
        Args:
            filename: Filename to search for
            job_id: Optional job ID to filter by
            
        Returns:
            Result containing list of files or error
        """
        try:
            query = self.db.query(File).filter(
                File.filename == filename
            )
            
            if job_id:
                query = query.filter(File.job_id == job_id)
            
            files = query.all()
            return Ok(files)
        except Exception as e:
            logger.error(f"Failed to find files by filename {filename}: {e}")
            return Err(str(e))
    
    def find_by_content_type(
        self,
        content_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> Result[List[File], str]:
        """
        Find files by content type.
        
        Args:
            content_type: MIME type of files
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Result containing list of files or error
        """
        try:
            files = self.db.query(File).filter(
                File.content_type == content_type
            ).offset(skip).limit(limit).all()
            return Ok(files)
        except Exception as e:
            logger.error(f"Failed to find files by content type {content_type}: {e}")
            return Err(str(e))
    
    def find_large_files(
        self,
        min_size_bytes: int,
        skip: int = 0,
        limit: int = 100
    ) -> Result[List[File], str]:
        """
        Find files larger than a specified size.
        
        Args:
            min_size_bytes: Minimum file size in bytes
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Result containing list of files or error
        """
        try:
            files = self.db.query(File).filter(
                File.size >= min_size_bytes
            ).order_by(
                desc(File.size)
            ).offset(skip).limit(limit).all()
            return Ok(files)
        except Exception as e:
            logger.error(f"Failed to find large files: {e}")
            return Err(str(e))
    
    def find_recent_files(
        self,
        hours: int = 24,
        skip: int = 0,
        limit: int = 100
    ) -> Result[List[File], str]:
        """
        Find files created within the last N hours.
        
        Args:
            hours: Number of hours to look back
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Result containing list of files or error
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            files = self.db.query(File).filter(
                File.created_at >= cutoff_time
            ).order_by(
                desc(File.created_at)
            ).offset(skip).limit(limit).all()
            return Ok(files)
        except Exception as e:
            logger.error(f"Failed to find recent files: {e}")
            return Err(str(e))
    
    def get_total_size_by_job(self, job_id: str) -> Result[int, str]:
        """
        Get total size of all files for a job.
        
        Args:
            job_id: Job ID
            
        Returns:
            Result containing total size in bytes or error
        """
        try:
            from sqlalchemy import func
            total_size = self.db.query(
                func.sum(File.size)
            ).filter(
                File.job_id == job_id
            ).scalar() or 0
            return Ok(total_size)
        except Exception as e:
            logger.error(f"Failed to get total size for job {job_id}: {e}")
            return Err(str(e))
    
    def delete_by_job_id(self, job_id: str) -> Result[int, str]:
        """
        Delete all files belonging to a job.
        
        Args:
            job_id: Job ID
            
        Returns:
            Result containing number of deleted files or error
        """
        try:
            count = self.db.query(File).filter(
                File.job_id == job_id
            ).count()
            
            self.db.query(File).filter(
                File.job_id == job_id
            ).delete()
            
            self.db.flush()
            return Ok(count)
        except Exception as e:
            logger.error(f"Failed to delete files for job {job_id}: {e}")
            self.db.rollback()
            return Err(str(e))
    
    def delete_old_files(
        self,
        days_old: int
    ) -> Result[int, str]:
        """
        Delete files older than specified days.
        
        Args:
            days_old: Age threshold in days
            
        Returns:
            Result containing number of deleted files or error
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            count = self.db.query(File).filter(
                File.created_at < cutoff_date
            ).count()
            
            self.db.query(File).filter(
                File.created_at < cutoff_date
            ).delete()
            
            self.db.flush()
            return Ok(count)
        except Exception as e:
            logger.error(f"Failed to delete old files: {e}")
            self.db.rollback()
            return Err(str(e))
    
    def get_storage_statistics(self) -> Result[Dict[str, Any], str]:
        """
        Get storage statistics.
        
        Returns:
            Result containing statistics dictionary or error
        """
        try:
            from sqlalchemy import func
            
            total_files = self.db.query(File).count()
            total_size = self.db.query(func.sum(File.size)).scalar() or 0
            
            # Size by content type
            size_by_type = dict(
                self.db.query(
                    File.content_type,
                    func.sum(File.size)
                ).group_by(File.content_type).all()
            )
            
            # Average file size
            avg_size = self.db.query(func.avg(File.size)).scalar() or 0
            
            # Largest file
            largest_file = self.db.query(File).order_by(
                desc(File.size)
            ).first()
            
            return Ok({
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": total_size / (1024 * 1024),
                "total_size_gb": total_size / (1024 * 1024 * 1024),
                "average_size_bytes": float(avg_size),
                "size_by_content_type": size_by_type,
                "largest_file": {
                    "id": largest_file.id,
                    "filename": largest_file.filename,
                    "size": largest_file.size
                } if largest_file else None
            })
        except Exception as e:
            logger.error(f"Failed to get storage statistics: {e}")
            return Err(str(e))