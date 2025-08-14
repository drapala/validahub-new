# CQRS Strategy for ValidaHub

## Executive Summary

ValidaHub will implement a pragmatic CQRS approach, starting simple and evolving based on real needs. The strategy focuses on audit requirements, CSV processing history, and analytics capabilities.

## Problem Context

### Requirements
- **Audit Trail**: Complete history of all validations, corrections, and downloads
- **Large Files**: Handle CSVs from 10MB to 1GB efficiently
- **Analytics**: Real-time dashboards and historical reports
- **Compliance**: Immutable audit log for regulatory purposes
- **Performance**: Sub-second queries for recent data, batch processing for analytics

### Constraints
- Small team, need pragmatic solutions
- Start simple, evolve with usage
- Maintain data consistency
- Cost-effective infrastructure

## Proposed Architecture

### Phase 1: CQRS Lite (Q1 2025) ✅

Start with a single PostgreSQL database but separate command and query models:

```
PostgreSQL Database
├── Write Models (Normalized)
│   ├── validation_jobs
│   ├── correction_events
│   ├── file_metadata
│   └── audit_log (append-only)
│
├── Read Models (Denormalized Views)
│   ├── validation_summary_view
│   ├── user_activity_view
│   ├── error_statistics_view
│   └── correction_history_view
│
└── Redis Cache
    ├── recent_validations
    ├── user_dashboards
    └── hot_queries
```

#### Implementation

**Commands (Write Side)**
```python
class CreateValidationCommand:
    file_id: UUID
    user_id: UUID
    marketplace: str
    category: str
    file_content: bytes
    
class ApplyCorrectionCommand:
    validation_id: UUID
    corrections: List[CorrectionDetail]
    applied_by: UUID
```

**Queries (Read Side)**
```python
class ValidationSummaryQuery:
    validation_id: UUID
    total_rows: int
    errors_by_type: Dict[str, int]
    corrections_applied: int
    processing_time_ms: int
    
class UserActivityQuery:
    user_id: UUID
    validations_last_30d: int
    most_common_errors: List[str]
    success_rate: float
```

**Audit Events Table**
```sql
CREATE TABLE audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(50) NOT NULL, -- file_uploaded, validation_started, etc
    aggregate_id UUID NOT NULL,       -- file_id or validation_id
    user_id UUID NOT NULL,
    payload JSONB NOT NULL,           -- event-specific data
    metadata JSONB,                   -- ip, user_agent, etc
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Append-only, no updates or deletes allowed
CREATE INDEX idx_audit_aggregate ON audit_events(aggregate_id, created_at DESC);
CREATE INDEX idx_audit_user ON audit_events(user_id, created_at DESC);
```

### Phase 2: Event Sourcing (Q3 2025)

Add event sourcing for critical flows while maintaining current system:

```
Event Store (PostgreSQL)          Projections
├── validation_events              ├── validation_state
├── correction_events              ├── correction_patterns
├── template_events                └── analytics_cache
└── user_events

Message Bus (Redis Streams/Kafka)
└── Async event processing
```

#### Event Examples

```python
@dataclass
class FileValidatedEvent:
    event_id: UUID
    aggregate_id: UUID  # file_id
    validation_id: UUID
    marketplace: str
    total_errors: int
    error_details: List[dict]
    occurred_at: datetime
    
@dataclass
class CorrectionAppliedEvent:
    event_id: UUID
    aggregate_id: UUID  # file_id
    correction_id: UUID
    corrections: List[dict]
    applied_by: UUID
    occurred_at: datetime
```

### Phase 3: Specialized Read Stores (Future)

When scale demands it, add specialized databases:

```
Write Side                    Read Side
PostgreSQL (Events)           ├── PostgreSQL (Current State)
                             ├── TimescaleDB (Time Series)
                             ├── S3 + Parquet (Historical CSVs)
                             └── Elasticsearch (Log Search)
```

## Audit Strategy

### Core Audit Requirements

1. **What to Audit**
   - Every file upload (original CSV stored)
   - Every validation run (rules applied, errors found)
   - Every correction (before/after state)
   - Every download (who, when, which version)
   - Every template change
   - System actions (auto-corrections)

2. **Storage Strategy**
   ```python
   # Audit event structure
   {
       "event_id": "uuid",
       "timestamp": "2025-01-15T10:30:00Z",
       "user_id": "uuid",
       "action": "validation_completed",
       "resource": {
           "type": "csv_file",
           "id": "file_uuid",
           "name": "products_mercadolivre.csv"
       },
       "changes": {
           "errors_found": 47,
           "rows_affected": [12, 45, 67, ...],
           "rule_violations": {
               "title_too_long": 15,
               "missing_sku": 32
           }
       },
       "metadata": {
           "ip": "192.168.1.1",
           "user_agent": "Mozilla/5.0...",
           "session_id": "uuid"
       }
   }
   ```

3. **CSV History Storage**
   ```
   S3/MinIO Structure:
   /validations/
     /{year}/{month}/{day}/
       /{validation_id}/
         /original.csv
         /validated.csv
         /corrected.csv
         /metadata.json
   ```

### Query Patterns

**For Operators/Support:**
- "Show all validations for user X in last 30 days"
- "Find all files that had SKU errors yesterday"
- "Which templates were used most this month?"

**For Users:**
- "My validation history"
- "Download original file from validation Y"
- "Show corrections applied to my file"

**For Analytics:**
- "Error trends by marketplace"
- "Average processing time by file size"
- "Most common correction patterns"

## Implementation Roadmap

### Sprint 1: Foundation (Current)
- [x] Basic PostgreSQL setup
- [ ] Create audit_events table
- [ ] Implement audit middleware
- [ ] Add file versioning

### Sprint 2: Read Models
- [ ] Create materialized views
- [ ] Implement query handlers
- [ ] Add Redis caching layer
- [ ] Build activity dashboard

### Sprint 3: Advanced Queries
- [ ] Historical CSV storage (S3)
- [ ] Analytics aggregations
- [ ] Export audit logs
- [ ] Compliance reports

### Sprint 4: Optimization
- [ ] Partition audit tables by month
- [ ] Async view refresh
- [ ] Query performance tuning
- [ ] Monitoring and alerts

## Decision Log

### Why Not Full CQRS Now?
- Overhead not justified for current scale
- Team needs to focus on core features
- Can evolve incrementally

### Why PostgreSQL for Events?
- Already in stack
- JSONB perfect for event payloads
- Good enough for millions of events
- Can migrate later if needed

### Why Redis for Cache?
- Already planned for async jobs
- Perfect for hot data
- Reduces database load

## Success Metrics

- Query performance: <100ms for recent data
- Audit completeness: 100% of actions logged
- Storage efficiency: <10% overhead for audit
- Recovery capability: Can rebuild state from events

## References

- [CQRS Journey by Microsoft](https://docs.microsoft.com/en-us/previous-versions/msp-n-p/jj554200(v=pandp.10))
- [Event Sourcing Pattern](https://martinfowler.com/eaaDev/EventSourcing.html)
- [Audit Logging Best Practices](https://www.postgresql.org/docs/current/sql-createtrigger.html)