# 📋 Jobs & Queue System - ValidaHub

## Overview

The ValidaHub Jobs System provides reliable asynchronous task processing using **Celery**, **Redis**, and **PostgreSQL**. It features idempotency, retry logic, priority queues, and comprehensive job tracking.

## ✅ Features

- **Idempotency**: Prevent duplicate jobs with idempotency keys
- **Priority Queues**: Route jobs based on user plan (free/pro/business/enterprise)
- **Retry Logic**: Exponential backoff with jitter for transient failures
- **Progress Tracking**: Real-time job progress updates
- **Job Cancellation**: Best-effort cancellation of queued/running jobs
- **Correlation IDs**: Request tracing across the system
- **Audit Trail**: Complete job history with timestamps

## 🚀 Quick Start

### 1. Start Redis

```bash
# Using Docker Compose
docker-compose up -d redis

# Or standalone
docker run -d --name redis -p 6379:6379 redis:alpine
```

### 2. Run Database Migrations

```bash
cd apps/api
source venv/bin/activate
alembic upgrade head
```

### 3. Start Celery Worker

```bash
# Start worker for PRO queue
celery -A src.workers.celery_app:celery_app worker \
  -Q queue:pro \
  -n worker.pro@%h \
  --loglevel=INFO

# For all queues
celery -A src.workers.celery_app:celery_app worker \
  -Q queue:free,queue:pro,queue:business,queue:enterprise \
  --loglevel=INFO
```

### 4. Start the API

```bash
uvicorn src.main:app --reload --port 3001
```

## 📡 API Endpoints

### Create Job
```http
POST /api/v1/jobs
Content-Type: application/json
Idempotency-Key: unique-key-123
X-Correlation-Id: request-123

{
  "task": "validate_csv_job",
  "params": {
    "input_uri": "s3://bucket/file.csv",
    "marketplace": "mercado_livre",
    "category": "electronics",
    "ruleset": "default",
    "auto_fix": true
  },
  "priority": 5,
  "plan": "pro",
  "idempotency_key": "upload-xyz-123"
}
```

**Response (202 Accepted):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "task_name": "validate_csv_job",
  "status": "queued",
  "progress": 0,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Get Job Status
```http
GET /api/v1/jobs/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "task_name": "validate_csv_job",
  "status": "running",
  "progress": 65.5,
  "message": "Validating 1500 rows",
  "created_at": "2024-01-15T10:30:00Z",
  "started_at": "2024-01-15T10:30:05Z"
}
```

### Get Job Result
```http
GET /api/v1/jobs/550e8400-e29b-41d4-a716-446655440000/result
```

**Response (if succeeded):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "succeeded",
  "result_ref": "s3://validahub/results/550e8400.json",
  "finished_at": "2024-01-15T10:31:30Z"
}
```

### Cancel Job
```http
DELETE /api/v1/jobs/550e8400-e29b-41d4-a716-446655440000
```

### List Jobs
```http
GET /api/v1/jobs?status=running&limit=10&offset=0
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql://user:pass@localhost/validahub

# Optional
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
MAX_RETRIES=3
TASK_TIME_LIMIT=300
```

### Queue Configuration

| Queue | Priority | Plan | Workers |
|-------|----------|------|---------|
| queue:free | 1 | Free users | 1 |
| queue:pro | 5 | Pro users | 2 |
| queue:business | 7 | Business users | 3 |
| queue:enterprise | 10 | Enterprise users | 5 |

## 📝 Available Tasks

### validate_csv_job
Validates CSV files using the rule engine.

**Parameters:**
- `input_uri`: S3 URI or file path
- `marketplace`: Target marketplace
- `category`: Product category
- `ruleset`: Rule set to use
- `auto_fix`: Apply automatic fixes

### correct_csv_job
Applies corrections to CSV files.

### sync_connector_job
Syncs data from external connectors (placeholder).

### generate_report_job
Generates analytics reports (placeholder).

## 🔄 Job Lifecycle

```
QUEUED → RUNNING → SUCCEEDED
   ↓        ↓          ↓
   ↓     RETRYING   FAILED
   ↓        ↓
CANCELLED  EXPIRED
```

## 🧪 Testing

### Basic Test

```python
import requests

# Create a job
response = requests.post(
    "http://localhost:3001/api/v1/jobs",
    json={
        "task": "validate_csv_job",
        "params": {
            "input_uri": "test.csv",
            "marketplace": "mercado_livre"
        },
        "plan": "pro"
    }
)
job = response.json()
print(f"Job created: {job['id']}")

# Check status
status = requests.get(f"http://localhost:3001/api/v1/jobs/{job['id']}")
print(f"Status: {status.json()['status']}")
```

### Idempotency Test

```python
# First request
response1 = requests.post(
    "http://localhost:3001/api/v1/jobs",
    json={
        "task": "validate_csv_job",
        "params": {"input_uri": "test.csv"},
        "idempotency_key": "test-123"
    }
)

# Second request with same idempotency_key
response2 = requests.post(
    "http://localhost:3001/api/v1/jobs",
    json={
        "task": "validate_csv_job",
        "params": {"input_uri": "test.csv"},
        "idempotency_key": "test-123"
    },
    headers={"Prefer": "return=representation"}
)

# Should return same job
assert response1.json()["id"] == response2.json()["id"]
```

## 🔍 Monitoring

### Celery Flower (Web UI)
```bash
pip install flower
celery -A src.workers.celery_app:celery_app flower --port=5555
```

Access at: http://localhost:5555

### Check Worker Status
```bash
celery -A src.workers.celery_app:celery_app inspect active
celery -A src.workers.celery_app:celery_app inspect stats
```

### Redis CLI
```bash
redis-cli
> KEYS job:*
> HGETALL job:550e8400-e29b-41d4-a716-446655440000
```

## 🚨 Troubleshooting

### Job Stuck in QUEUED
- Check if Celery workers are running
- Verify Redis connection
- Check queue routing configuration

### Jobs Not Persisting
- Verify PostgreSQL connection
- Check Alembic migrations
- Review database permissions

### High Memory Usage
- Implement result expiration
- Use S3 for large results
- Enable Redis eviction policy

## 📚 Architecture

```
Client → API → JobService → Celery → Worker
           ↓                  ↓         ↓
      PostgreSQL ← Redis ← Task Handler
           ↓                            ↓
       Job Model              Rule Engine/Services
```

## 🔐 Security Considerations

1. **Authentication**: Implement proper user authentication
2. **Rate Limiting**: Limit jobs per user/plan
3. **Input Validation**: Sanitize all job parameters
4. **Resource Limits**: Set memory/CPU limits per task
5. **Secrets Management**: Use environment variables

## 🎯 Next Steps

- [ ] Implement job scheduling (cron-like)
- [ ] Add webhook notifications
- [ ] Create job templates
- [ ] Implement job chaining/workflows
- [ ] Add metrics collection (Prometheus)
- [ ] Setup distributed tracing (OpenTelemetry)

## 📖 References

- [Celery Documentation](https://docs.celeryproject.org/)
- [Redis Documentation](https://redis.io/documentation)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [Idempotency Keys](https://stripe.com/docs/api/idempotent_requests)