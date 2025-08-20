# ValidaHub Job System Documentation

## Overview

ValidaHub uses a robust asynchronous job processing system built on **Celery** with **Redis** as the message broker. This system handles long-running tasks like CSV validation and correction, providing scalability, reliability, and monitoring capabilities.

## Architecture

### Components

1. **Job Service** (`src/services/job_service.py`)
   - Manages job lifecycle (creation, status updates, cancellation)
   - Implements idempotency via `idempotency_key`
   - Handles job persistence in PostgreSQL

2. **Queue Publisher** (`src/infrastructure/queue_publisher.py`)
   - Abstract interface for queue implementations
   - Implementations:
     - `CeleryQueuePublisher`: Production (Redis + Celery)
     - `SQSQueuePublisher`: AWS SQS (future)
     - `InMemoryQueuePublisher`: Testing

3. **Celery Workers** (`src/workers/`)
   - `celery_app.py`: Celery configuration and signal handlers
   - `tasks.py`: Task implementations (validate_csv_job, correct_csv_job)

4. **Job API** (`src/api/v1/jobs.py`)
   - RESTful endpoints for job management
   - Supports async operations with 202 Accepted responses

## Key Features

### 1. Idempotency
- Jobs can include an `idempotency_key` to prevent duplicate processing
- Returns existing job if key matches (with appropriate status code)

### 2. Priority Queues
- Multiple queues based on user plan:
  - `queue:free` (priority 1)
  - `queue:pro` (priority 5)
  - `queue:business` (priority 7)
  - `queue:enterprise` (priority 10)

### 3. Job Status Tracking
- States: `QUEUED`, `RUNNING`, `SUCCEEDED`, `FAILED`, `CANCELLED`, `RETRYING`
- Real-time status updates via Celery signals
- Progress tracking for long-running tasks

### 4. Retry Logic
- Automatic retry with exponential backoff
- Configurable max retries (default: 3)
- Transient error handling

### 5. Telemetry & Monitoring
- Comprehensive event emission:
  - `job.queued`, `job.started`, `job.completed`, `job.failed`
  - `job.cancelled`, `job.retrying`, `job.progress`
- Metrics collection for performance monitoring

## Configuration

### Environment Variables

```bash
# Required
DATABASE_URL=postgresql://user:pass@localhost:5432/validahub
REDIS_URL=redis://localhost:6379/0  # Development
REDIS_URL=rediss://:password@host:port/0  # Production (TLS + Auth)

# Optional
ENV=development|production
MAX_SYNC_FILE_SIZE=5242880  # 5MB
MAX_FILE_SIZE=52428800      # 50MB
```

### Celery Configuration

```python
# src/workers/celery_app.py
celery_app.conf.update(
    task_serializer="json",
    task_track_started=True,
    task_time_limit=300,        # 5 min hard limit
    task_soft_time_limit=270,   # 4.5 min soft limit
    task_acks_late=True,
    worker_prefetch_multiplier=1,  # Fair processing
    task_retry_max=3,
    task_retry_backoff=2,        # Exponential backoff
)
```

## Usage

### Starting Workers

```bash
# Development
celery -A src.workers.celery_app worker --loglevel=info

# Production with multiple queues
celery -A src.workers.celery_app worker \
  --queues=queue:enterprise,queue:business,queue:pro,queue:free \
  --loglevel=info \
  --concurrency=4
```

### Creating Jobs via API

```python
POST /api/v1/jobs
{
  "task": "validate_csv_job",
  "params": {
    "input_uri": "s3://bucket/input.csv",
    "marketplace": "mercado_livre",
    "category": "electronics",
    "auto_fix": true
  },
  "priority": 5,
  "idempotency_key": "unique-key-123"
}

Response: 202 Accepted
{
  "id": "job-uuid",
  "status": "queued",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Checking Job Status

```python
GET /api/v1/jobs/{job_id}

Response: 200 OK
{
  "id": "job-uuid",
  "status": "running",
  "progress": 45.5,
  "message": "Processing row 455 of 1000"
}
```

### Cancelling Jobs

```python
DELETE /api/v1/jobs/{job_id}

Response: 200 OK
{
  "id": "job-uuid",
  "status": "cancelled",
  "message": "Job cancelled by user"
}
```

## Task Implementation

### Creating a New Task

```python
# src/workers/tasks.py
@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="my_new_task",
    autoretry_for=(TransientError,),
    retry_backoff=2,
    max_retries=3
)
def my_new_task(self, job_id: str, params: Dict[str, Any]):
    task_id = self.request.id
    
    # Update progress
    update_job_progress(task_id, 10, "Starting task")
    
    # Task logic here
    result = process_data(params)
    
    # Return result reference
    return {
        "result_ref": "s3://bucket/results/output.json",
        "summary": result.summary,
        "status": "success"
    }
```

## Database Schema

### Job Table
```sql
CREATE TABLE jobs (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    task_name VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    queue VARCHAR,
    priority INTEGER,
    progress FLOAT,
    message TEXT,
    error TEXT,
    result_ref TEXT,
    celery_task_id VARCHAR,
    idempotency_key VARCHAR UNIQUE,
    correlation_id VARCHAR,
    metadata JSONB,
    params_json JSONB,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    created_at TIMESTAMP,
    started_at TIMESTAMP,
    finished_at TIMESTAMP
);
```

## Error Handling

### Transient Errors
- Automatically retried with exponential backoff
- Examples: Network timeouts, temporary resource unavailability

### Permanent Errors
- Job marked as failed immediately
- Examples: Invalid parameters, permission denied

### Error Recovery
```python
# Retry failed job
POST /api/v1/jobs/{job_id}/retry

# Manual intervention required for certain errors
if job.error.startswith("CRITICAL:"):
    notify_admin(job)
```

## Monitoring & Debugging

### Celery Flower (Web UI)
```bash
celery -A src.workers.celery_app flower --port=5555
# Access at http://localhost:5555
```

### Logs
- Application logs: Job creation, status updates
- Worker logs: Task execution, errors, retries
- Telemetry events: Performance metrics, queue times

### Health Checks
```python
GET /health/queue
{
  "status": "healthy",
  "queue_stats": {
    "total_jobs": 1234,
    "queued": 10,
    "running": 5,
    "succeeded": 1200,
    "failed": 19
  }
}
```

## Best Practices

1. **Always use idempotency keys** for critical operations
2. **Set appropriate timeouts** based on expected task duration
3. **Implement proper error handling** with meaningful error messages
4. **Monitor queue depths** and scale workers accordingly
5. **Use correlation IDs** for distributed tracing
6. **Clean up old jobs** periodically to manage database size
7. **Test retry logic** thoroughly before deployment

## Future Enhancements

1. **Multi-region support** with geo-distributed queues
2. **SQS/Lambda integration** for serverless processing
3. **GraphQL subscriptions** for real-time status updates
4. **Job dependencies** and workflow orchestration
5. **Cost tracking** per job/user
6. **Auto-scaling** based on queue depth