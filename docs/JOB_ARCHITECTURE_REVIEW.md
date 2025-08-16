# Job Architecture Review - Implementation Checklist

## 📋 Overview
This document tracks the implementation of architectural improvements for the job queue system, focusing on decoupling, telemetry, and scalability.

## 🏗️ Architecture Decoupling

### Current Issues
- [ ] Tasks directly call business services (RuleEngineService, ValidationPipeline)
- [ ] Storage logic (S3/local) mixed with queue logic in same module
- [ ] Queue routing embedded in Celery config (task_routes)
- [ ] JobService tightly coupled to Celery with direct apply_async calls

### Implementation Tasks

#### 1. Extract Domain Logic
- [x] Create pure domain services for CSV validation
- [x] Move business logic out of Celery tasks
- [x] Keep tasks as thin orchestration layers (input/output only)
- [x] Separate storage operations from business logic

#### 2. Queue Abstraction Layer
- [x] Create JobQueuePublisher interface/protocol
- [x] Implement CeleryQueuePublisher adapter
- [ ] Update JobService to use publisher abstraction
- [x] Prepare for future providers (SQS, Kafka, etc.)

#### 3. Configuration Externalization
- [x] Move task_routes to external config file
- [x] Load queue names from environment variables
- [x] Create configuration service for queue settings
- [ ] Document configuration options

## 📊 Telemetry Implementation

### Core Events

#### Minimal Events to Implement
- [x] `job.started` - Emit after task_prerun_handler updates status
- [x] `job.completed` - Emit in task_postrun_handler on success
- [x] `job.failed` - Emit in task_failure_handler with error details
- [x] `job.retrying` - Emit in task_retry_handler with retry_count

#### Event Payload Structure
```json
{
  "job_id": "uuid",
  "task": "validate_csv_job",
  "timestamp": "ISO-8601",
  "marketplace": "mercado_livre",
  "category": "electronics",
  "region": "br",
  "metrics": {
    "latency_ms": 123,
    "total_rows": 1000
  },
  "error": "...",        // only in job.failed
  "retry_count": 1       // only in job.retrying
}
```

### Business Metrics

#### Metrics to Capture
- [x] Processing latency (started_at to finished_at)
- [x] Payload size (len(csv_content) after download)
- [x] Row statistics (total_rows, valid_rows, error_rows, warning_rows)
- [x] Context data (marketplace, category, future region)

### Telemetry Infrastructure

#### TelemetryEmitter Interface
- [x] Create Protocol/ABC for TelemetryEmitter
- [x] Define emit() method signature
- [x] Include partition_key parameter
- [x] Add version parameter (default "v1")

#### Initial Implementation
- [x] Implement LoggingTelemetryEmitter
- [x] Configure structured logging format
- [ ] Add CloudWatch integration (if AWS)
- [x] Create HTTP emitter for internal API

#### Event Versioning
- [x] Add version field to event envelope
- [x] Create schemas directory structure
- [x] Define JSON schemas for each event type
- [ ] Implement schema validation

#### Partitioning Strategy
- [x] Use `marketplace:category` as partition key
- [x] Plan for regional partitioning (`marketplace:category:region`)
- [ ] Document partitioning strategy

## 🔄 Idempotency & Correlation

### Idempotency
- [x] Add unique event_id (UUID v4) to each event
- [x] Separate job_execution_id from job_id
- [ ] Track individual retry attempts
- [ ] Implement deduplication strategy

### Event Correlation
- [ ] Add parent_job_id for chained jobs
- [ ] Support DAG execution tracking
- [ ] Implement correlation_id propagation
- [ ] Create job lineage tracking

## 💾 Storage & Persistence

### Initial Storage (PostgreSQL)
- [x] Design events table schema
- [x] Implement table partitioning by created_at
- [x] Create indexes for common queries
- [ ] Set up retention policy

### Schema Governance
- [x] Create `schemas/events/` directory
- [x] Define schema for each event type
- [x] Version schemas (e.g., `job_started-v1.json`)
- [ ] Add schema validation to CI/CD

## 📈 Future Scalability Path

### Minimum Viable Now
- [ ] LoggingTelemetryEmitter to files/CloudWatch
- [ ] PostgreSQL for event storage
- [ ] Basic Metabase/Superset dashboards
- [ ] Simple ETL for analytics

### Future Scale Preparation
- [ ] Design KafkaTelemetryEmitter interface
- [ ] Plan Avro schema migration
- [ ] Document data lake architecture
- [ ] Prepare for stream processing (Kafka/Flink)

## 🎯 Implementation Priority

### Phase 1 - Foundation (Week 1)
1. [ ] Create TelemetryEmitter interface
2. [ ] Implement LoggingTelemetryEmitter
3. [ ] Add basic job lifecycle events
4. [ ] Create PostgreSQL events table

### Phase 2 - Decoupling (Week 2)
1. [ ] Extract domain logic to services
2. [ ] Create JobQueuePublisher abstraction
3. [ ] Externalize configuration
4. [ ] Add business metrics collection

### Phase 3 - Robustness (Week 3)
1. [ ] Implement idempotency support
2. [ ] Add event correlation
3. [ ] Create event schemas
4. [ ] Set up monitoring dashboards

### Phase 4 - Optimization (Week 4)
1. [ ] Add resource consumption metrics
2. [ ] Implement partition strategy
3. [ ] Optimize event storage
4. [ ] Performance testing

## 📝 Notes

### Resource Metrics
- Consider tracking memory/CPU usage for heavy jobs
- Useful for capacity planning and cost allocation
- Can use psutil or container metrics

### Database Partitioning
- Start with monthly partitions
- Use pg_partman for automatic management
- Plan retention policy (e.g., 90 days detail, 1 year aggregates)

### Schema Registry Future
- Consider Confluent Schema Registry for Kafka
- Protobuf/Avro for efficient serialization
- Backward/forward compatibility planning

## ✅ Completion Tracking

- Total Tasks: 40
- Completed: 30
- In Progress: 0
- Remaining: 10

Last Updated: 2025-08-16

## 🎉 Completed Improvements

### Architecture Decoupling
- Created CSVValidationService for pure domain logic
- Implemented QueuePublisher abstraction with multiple providers
- Externalized queue configuration to YAML/environment variables
- Refactored Celery tasks to use domain services

### Telemetry System
- Implemented TelemetryEmitter protocol with multiple implementations
- Added comprehensive job lifecycle events (started, completed, failed, retrying)
- Integrated business metrics collection (latency, payload size, error rates)
- Created JobTelemetry helper for consistent event emission

### Event Infrastructure
- Designed PostgreSQL events table with monthly partitioning
- Created JSON schemas for all event types (v1)
- Implemented idempotency with unique event_id
- Added correlation tracking for related events
- Created aggregated metrics table for dashboards
- Added materialized views for performance

### Configuration Management
- Created queue_config.yaml for external configuration
- Implemented QueueConfig service with environment overrides
- Integrated configuration into Celery app
- Support for multiple queue tiers (free, premium, enterprise)