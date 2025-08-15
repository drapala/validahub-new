# ValidaHub API - Usage Examples

## Health Check

```bash
# Simple health check (no auth required)
curl -X GET "http://localhost:3001/health"

# Response
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "services": {
    "api": "healthy",
    "database": "healthy",
    "redis": "healthy",
    "s3": "healthy"
  },
  "uptime_seconds": 3600
}
```

## CSV Validation

### Multipart Upload (Recommended for small files)

```bash
# Validate CSV with multipart/form-data
curl -X POST "http://localhost:3001/api/v1/validate_csv" \
  -H "X-Correlation-Id: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Idempotency-Key: unique-request-123" \
  -F "marketplace=AMAZON_BR" \
  -F "category=CELL_PHONE" \
  -F "file=@catalog.csv" \
  -F 'options={"strict_mode": true}'

# Response (Synchronous - files < 5MB)
{
  "ruleset_version": "1.0.0",
  "totals": {
    "total_rows": 1000,
    "valid_rows": 950,
    "error_rows": 50,
    "errors_count": 75,
    "warnings_count": 120,
    "info_count": 30
  },
  "items": [
    {
      "rule_id": "sku_required",
      "row": 12,
      "field": "sku",
      "severity": "ERROR",
      "message": "SKU is required",
      "before": null,
      "after": null
    }
  ],
  "processing_time_ms": 342,
  "job_id": "550e8400-e29b-41d4-a716-446655440001"
}

# Response (Asynchronous - files > 5MB)
HTTP/1.1 202 Accepted
{
  "job_id": "550e8400-e29b-41d4-a716-446655440002",
  "status": "accepted",
  "message": "File accepted for processing",
  "location": "/api/v1/jobs/550e8400-e29b-41d4-a716-446655440002"
}
```

## CSV Correction

```bash
# Correct CSV and download result
curl -X POST "http://localhost:3001/api/v1/correct_csv" \
  -H "X-Correlation-Id: 550e8400-e29b-41d4-a716-446655440003" \
  -F "marketplace=AMAZON_BR" \
  -F "category=CELL_PHONE" \
  -F "file=@catalog.csv" \
  --output catalog_corrected.csv

# Response headers
HTTP/1.1 200 OK
Content-Type: text/csv
Content-Disposition: attachment; filename=catalog_corrected.csv
X-Corrections-Applied: 45
X-Success-Rate: 95.5%
X-Correlation-Id: 550e8400-e29b-41d4-a716-446655440003
X-Job-Id: 550e8400-e29b-41d4-a716-446655440004
```

## Correction Preview

```bash
# Preview corrections without applying them
curl -X POST "http://localhost:3001/api/v1/correction_preview" \
  -H "X-Correlation-Id: 550e8400-e29b-41d4-a716-446655440005" \
  -F "marketplace=AMAZON_BR" \
  -F "category=CELL_PHONE" \
  -F "file=@catalog.csv" \
  -F "sample_strategy=random" \
  -F "sample_size=50" \
  -F "show_only_changed=true"

# Response
{
  "summary": {
    "total_corrections": 45,
    "success_rate": 95.5,
    "corrections_by_rule": {
      "normalize_price": 20,
      "fix_sku_format": 15,
      "standardize_color": 10
    },
    "affected_rows": [12, 15, 23, 45, 67, 89]
  },
  "preview_data": [
    {
      "row": 12,
      "sku": {
        "before": "ABC123",
        "after": "ABC-123"
      },
      "price": {
        "before": "29,99",
        "after": "29.99"
      }
    }
  ],
  "changes": [
    {
      "rule_id": "fix_sku_format",
      "row": 12,
      "field": "sku",
      "severity": "WARN",
      "message": "SKU format standardized",
      "before": "ABC123",
      "after": "ABC-123"
    }
  ],
  "job_id": "550e8400-e29b-41d4-a716-446655440006"
}
```

## Error Responses (RFC 7807)

```json
// 413 File Too Large
{
  "type": "https://validahub.com/errors/file-too-large",
  "title": "File Too Large",
  "status": 413,
  "detail": "File size exceeds maximum allowed size of 50MB",
  "instance": "/api/v1/validate_csv",
  "max_size_bytes": 52428800,
  "actual_size_bytes": 62914560,
  "timestamp": "2024-01-15T10:30:00Z",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440007"
}

// 429 Rate Limit Exceeded
{
  "type": "https://validahub.com/errors/rate-limit-exceeded",
  "title": "Rate Limit Exceeded",
  "status": 429,
  "detail": "You have exceeded the rate limit",
  "instance": "/api/v1/validate_csv",
  "retry_after_seconds": 30,
  "rate_limit_remaining": 0,
  "rate_limit_reset": "2024-01-15T10:31:00Z",
  "timestamp": "2024-01-15T10:30:30Z",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440008"
}

// 422 Validation Error
{
  "type": "https://validahub.com/errors/validation-failed",
  "title": "Validation Failed",
  "status": 422,
  "detail": "Invalid marketplace specified",
  "instance": "/api/v1/validate_csv",
  "validation_errors": {
    "marketplace": "Must be one of: AMAZON_BR, MERCADO_LIVRE, SHOPEE"
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440009"
}
```

## Response Headers

All API responses include these headers:

- `X-Correlation-Id`: Request correlation ID for tracing
- `X-Process-Time-Ms`: Processing time in milliseconds
- `X-RateLimit-Limit`: Rate limit ceiling for the client
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Unix timestamp when the rate limit resets

Correction endpoints also include:
- `X-Corrections-Applied`: Number of corrections applied
- `X-Success-Rate`: Percentage of successful corrections
- `X-Job-Id`: Unique job identifier for tracking

## Authentication (When Enabled)

```bash
# Bearer token
curl -X POST "http://localhost:3001/api/v1/validate_csv" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -F "marketplace=AMAZON_BR" \
  -F "category=CELL_PHONE" \
  -F "file=@catalog.csv"

# API Key
curl -X POST "http://localhost:3001/api/v1/validate_csv" \
  -H "X-API-Key: your-api-key-here" \
  -F "marketplace=AMAZON_BR" \
  -F "category=CELL_PHONE" \
  -F "file=@catalog.csv"
```