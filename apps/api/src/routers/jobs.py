"""Jobs API endpoints for validation processing."""

import random
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from src.db.database import get_db
from src.models import Job, JobItem, JobStatus, JobChannel, JobType, ErrorSeverity
from src.middleware.auth import get_current_user

def get_current_tenant_id():
    """Temporary function to get tenant ID."""
    return "validahub-id"
from src.services.auth_service import AuthService

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


class JobsFilter:
    """Filter parameters for jobs listing."""
    def __init__(
        self,
        status: Optional[List[JobStatus]] = Query(None),
        channel: Optional[List[JobChannel]] = Query(None),
        seller: Optional[str] = Query(None),
        period_start: Optional[datetime] = Query(None),
        period_end: Optional[datetime] = Query(None),
        severity: Optional[List[ErrorSeverity]] = Query(None),
        type: Optional[List[JobType]] = Query(None),
        page_index: int = Query(0, ge=0),
        page_size: int = Query(10, ge=1, le=100),
    ):
        self.status = status or []
        self.channel = channel or []
        self.seller = seller
        self.period_start = period_start
        self.period_end = period_end
        self.severity = severity or []
        self.type = type or []
        self.page_index = page_index
        self.page_size = page_size


@router.get("")
async def list_jobs(
    filters: JobsFilter = Depends(),
    tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """List jobs with filters and pagination."""
    query = db.query(Job).filter(Job.tenant_id == tenant_id)
    
    # Apply filters
    if filters.status:
        query = query.filter(Job.status.in_(filters.status))
    
    if filters.channel:
        query = query.filter(Job.channel.in_(filters.channel))
    
    if filters.seller:
        query = query.filter(Job.seller_name.contains(filters.seller))
    
    if filters.period_start:
        query = query.filter(Job.created_at >= filters.period_start)
    
    if filters.period_end:
        query = query.filter(Job.created_at <= filters.period_end)
    
    if filters.severity:
        query = query.filter(Job.severity.in_(filters.severity))
    
    if filters.type:
        query = query.filter(Job.type.in_(filters.type))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    jobs = query.order_by(desc(Job.created_at))\
        .offset(filters.page_index * filters.page_size)\
        .limit(filters.page_size)\
        .all()
    
    return {
        "data": [job.to_dict() for job in jobs],
        "total": total,
        "page_index": filters.page_index,
        "page_size": filters.page_size,
    }


@router.get("/stats")
async def get_job_stats(
    tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """Get job statistics and KPIs."""
    # Base query for last 24 hours
    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    base_query = db.query(Job).filter(
        and_(
            Job.tenant_id == tenant_id,
            Job.created_at >= cutoff_time
        )
    )
    
    # Total jobs
    total_jobs = base_query.count()
    
    # Jobs by status
    status_counts = db.query(
        Job.status,
        func.count(Job.id)
    ).filter(
        and_(
            Job.tenant_id == tenant_id,
            Job.created_at >= cutoff_time
        )
    ).group_by(Job.status).all()
    
    jobs_by_status = {status.value: count for status, count in status_counts}
    
    # Calculate metrics
    failed_jobs = jobs_by_status.get('failed', 0)
    review_jobs = jobs_by_status.get('review', 0)
    success_jobs = jobs_by_status.get('success', 0)
    
    success_rate = (success_jobs / total_jobs * 100) if total_jobs > 0 else 0.0
    
    # Performance metrics
    perf_metrics = db.query(
        func.avg(Job.duration_ms).label('avg_latency'),
        func.percentile_cont(0.95).within_group(Job.duration_ms).label('p95'),
        func.percentile_cont(0.99).within_group(Job.duration_ms).label('p99')
    ).filter(
        and_(
            Job.tenant_id == tenant_id,
            Job.created_at >= cutoff_time,
            Job.duration_ms.isnot(None)
        )
    ).first()
    
    # Jobs by channel
    channel_counts = db.query(
        Job.channel,
        func.count(Job.id)
    ).filter(
        and_(
            Job.tenant_id == tenant_id,
            Job.created_at >= cutoff_time
        )
    ).group_by(Job.channel).all()
    
    jobs_by_channel = {channel.value: count for channel, count in channel_counts}
    
    # Jobs by severity
    severity_counts = db.query(
        Job.severity,
        func.count(Job.id)
    ).filter(
        and_(
            Job.tenant_id == tenant_id,
            Job.created_at >= cutoff_time,
            Job.severity.isnot(None)
        )
    ).group_by(Job.severity).all()
    
    jobs_by_severity = {severity.value if severity else 'none': count for severity, count in severity_counts}
    
    return {
        "total_jobs": total_jobs,
        "success_rate": round(success_rate, 2),
        "failed_jobs": failed_jobs,
        "review_jobs": review_jobs,
        "avg_latency_ms": round(perf_metrics.avg_latency or 0, 2),
        "p95_latency_ms": round(perf_metrics.p95 or 0, 2),
        "p99_latency_ms": round(perf_metrics.p99 or 0, 2),
        "jobs_by_channel": jobs_by_channel,
        "jobs_by_status": jobs_by_status,
        "jobs_by_severity": jobs_by_severity,
    }


@router.get("/{job_id}")
async def get_job_detail(
    job_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """Get detailed information about a specific job."""
    job = db.query(Job).filter(
        and_(
            Job.id == job_id,
            Job.tenant_id == tenant_id
        )
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get job items with errors
    items = db.query(JobItem).filter(
        JobItem.job_id == job_id
    ).order_by(JobItem.created_at).limit(100).all()
    
    return {
        "job": job.to_dict(),
        "items": [item.to_dict() for item in items],
        "item_stats": {
            "total": job.total_items,
            "processed": job.processed_items,
            "success": job.success_items,
            "failed": job.failed_items,
            "warnings": job.warning_items,
        }
    }


@router.post("/{job_id}/reprocess")
async def reprocess_job(
    job_id: str,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    tenant_id: str = Depends(get_current_tenant_id),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Reprocess a failed or completed job."""
    # Find original job
    original_job = db.query(Job).filter(
        and_(
            Job.id == job_id,
            Job.tenant_id == tenant_id
        )
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if job can be reprocessed
    if original_job.status not in [JobStatus.FAILED, JobStatus.REVIEW, JobStatus.SUCCESS]:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot reprocess job with status {original_job.status}"
        )
    
    # Check idempotency
    if idempotency_key:
        existing = db.query(Job).filter(
            and_(
                Job.tenant_id == tenant_id,
                Job.idempotency_key == idempotency_key
            )
        ).first()
        
        if existing:
            return {
                "job_id": existing.id,
                "status": existing.status.value,
                "message": "Job already being processed (idempotent response)"
            }
    
    # Create new job for reprocessing
    new_job = Job(
        tenant_id=tenant_id,
        seller_id=original_job.seller_id,
        seller_name=original_job.seller_name,
        channel=original_job.channel,
        type=original_job.type,
        status=JobStatus.PENDING,
        file_name=original_job.file_name,
        file_size_bytes=original_job.file_size_bytes,
        file_url=original_job.file_url,
        total_items=original_job.total_items,
        parent_job_id=original_job.id,
        idempotency_key=idempotency_key,
        reprocess_count=original_job.reprocess_count + 1,
    )
    
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    # TODO: Queue the job for actual processing
    # For now, just return the new job info
    
    return {
        "job_id": new_job.id,
        "status": new_job.status.value,
        "message": "Job queued for reprocessing",
        "parent_job_id": original_job.id,
    }


@router.post("/create-mock")
async def create_mock_jobs(
    count: int = Query(50, ge=1, le=1000),
    tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    """Create mock jobs for testing (development only)."""
    import os
    if os.getenv("ENVIRONMENT") == "production":
        raise HTTPException(status_code=403, detail="Not available in production")
    
    channels = list(JobChannel)
    types = list(JobType)
    statuses = list(JobStatus)
    severities = list(ErrorSeverity)
    
    sellers = [
        ("seller_001", "TechMart Brasil"),
        ("seller_002", "Fashion Store SP"),
        ("seller_003", "Casa & Decor RJ"),
        ("seller_004", "Electronics Hub"),
        ("seller_005", "Beauty Express"),
    ]
    
    jobs = []
    for i in range(count):
        # Random data
        channel = random.choice(channels)
        job_type = random.choice(types)
        status = random.choice(statuses)
        seller_id, seller_name = random.choice(sellers)
        
        total_items = random.randint(10, 10000)
        success_rate = random.uniform(0.6, 1.0) if status == JobStatus.SUCCESS else random.uniform(0, 0.8)
        
        success_items = int(total_items * success_rate)
        failed_items = total_items - success_items
        warning_items = random.randint(0, min(100, total_items))
        
        # Create job
        job = Job(
            tenant_id=tenant_id,
            seller_id=seller_id,
            seller_name=seller_name,
            channel=channel,
            type=job_type,
            status=status,
            total_items=total_items,
            processed_items=total_items if status in [JobStatus.SUCCESS, JobStatus.FAILED] else random.randint(0, total_items),
            success_items=success_items,
            failed_items=failed_items,
            warning_items=warning_items,
            duration_ms=random.randint(100, 30000) if status in [JobStatus.SUCCESS, JobStatus.FAILED] else None,
            avg_item_time_ms=random.uniform(1, 100) if status in [JobStatus.SUCCESS, JobStatus.FAILED] else None,
            p95_time_ms=random.uniform(50, 200) if status in [JobStatus.SUCCESS, JobStatus.FAILED] else None,
            p99_time_ms=random.uniform(100, 500) if status in [JobStatus.SUCCESS, JobStatus.FAILED] else None,
            error_count=failed_items if failed_items > 0 else 0,
            warning_count=warning_items,
            severity=random.choice(severities) if failed_items > 0 else None,
            last_error="Validation failed: Invalid SKU format" if failed_items > 0 else None,
            file_name=f"catalog_{seller_id}_{i:04d}.csv",
            file_size_bytes=random.randint(1024, 104857600),
            created_at=datetime.utcnow() - timedelta(hours=random.randint(0, 72)),
            started_at=datetime.utcnow() - timedelta(hours=random.randint(0, 48)) if status != JobStatus.PENDING else None,
            completed_at=datetime.utcnow() - timedelta(minutes=random.randint(1, 120)) if status in [JobStatus.SUCCESS, JobStatus.FAILED] else None,
        )
        
        jobs.append(job)
        
        # Create some job items for failed/review jobs
        if status in [JobStatus.FAILED, JobStatus.REVIEW] and random.random() > 0.5:
            for j in range(min(10, failed_items)):
                item = JobItem(
                    job_id=job.id,
                    sku=f"SKU{random.randint(100000, 999999)}",
                    title=f"Product {j}",
                    status=random.choice([JobStatus.FAILED, JobStatus.REVIEW]),
                    field_errors=[{
                        "field": random.choice(["price", "stock", "description", "images"]),
                        "error": random.choice([
                            "Required field missing",
                            "Invalid format",
                            "Value out of range",
                            "Invalid characters"
                        ])
                    }] if random.random() > 0.5 else [],
                    error_codes=[f"ERR_{random.randint(1000, 9999)}"],
                    error_categories=[random.choice(["pricing", "stock", "attributes", "images"])],
                    suggestions=[{
                        "field": "price",
                        "suggestion": "Price should be greater than 0",
                        "confidence": random.uniform(0.7, 1.0)
                    }] if random.random() > 0.5 else [],
                    processing_time_ms=random.randint(1, 100),
                )
                db.add(item)
    
    db.add_all(jobs)
    db.commit()
    
    return {"message": f"Created {count} mock jobs"}