# ADR-004: Multi-Tenant Architecture for MVP

## Status
**Proposed** - 2025-01-24

## Context

ValidaHub is a multi-tenant SaaS platform for e-commerce CSV validation and correction. From the MVP stage, we need to address two fundamental requirements that seem conflicting:

1. **Strict data isolation between clients** - For security, compliance (LGPD/GDPR), and customer trust
2. **Ability to generate aggregated market intelligence** - To create network effects and provide valuable insights to customers about market trends and benchmarks

### Why Multi-Tenant from MVP?

- **Economies of scale**: Sharing resources significantly reduces operational costs
- **Network effects**: Aggregated and anonymized data generates exponential value (benchmarks, anomaly detection, correction suggestions based on market patterns)
- **Onboarding speed**: New customers can be provisioned instantly
- **Simplified maintenance**: Single version of code and schema to maintain

### Current Stack
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with TimescaleDB extension
- **Cache**: Redis
- **Async processing**: Celery
- **Storage**: S3
- **Observability**: Custom telemetry

## Options Considered

### Option 1: Shared Database + `tenant_id` with Row Level Security (RLS)

All tenants share the same database and schemas. Each table has a `tenant_id` column and RLS policies ensure isolation.

**Pros:**
- ✅ Lower operational cost (single database)
- ✅ Facilitates data aggregation for BI/analytics
- ✅ Simplified deployment and maintenance
- ✅ Better resource usage (connection pooling, cache)
- ✅ Single schema migration

**Cons:**
- ❌ Risk of data leakage if RLS fails
- ❌ Noisy neighbor problem (one tenant can impact others)
- ❌ Granular backup/restore more complex
- ❌ Database limits shared among all tenants

### Option 2: Schema-per-Tenant

Each tenant has their own PostgreSQL schema within the same database.

**Pros:**
- ✅ Better isolation than shared DB
- ✅ Backup/restore per schema is possible
- ✅ Lower risk of accidental leakage
- ✅ Possibility of per-tenant customization

**Cons:**
- ❌ Schema migration multiplied by N tenants
- ❌ Cross-tenant aggregation more complex
- ❌ PostgreSQL schema limits
- ❌ Higher operational complexity

### Option 3: Database-per-Tenant

Each tenant has their own PostgreSQL database.

**Pros:**
- ✅ Total isolation between tenants
- ✅ Independent backup/restore
- ✅ Guaranteed performance per tenant
- ✅ Maximum compliance for enterprise customers

**Cons:**
- ❌ Very high operational cost
- ❌ Extremely complex cross-tenant aggregation
- ❌ Connection and resource overhead
- ❌ Multiplied deployment and maintenance

## Evaluation Criteria

| Criteria | Weight | Shared DB + RLS | Schema-per-Tenant | DB-per-Tenant |
|----------|--------|-----------------|-------------------|---------------|
| Operational cost | 30% | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ |
| Technical simplicity | 25% | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Security/Isolation | 20% | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| BI/Analytics capability | 15% | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ |
| Scalability | 10% | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## Decision

**We will adopt Shared Database + `tenant_id` with Row Level Security (RLS) for the MVP**, with architectural preparation for selective evolution.

### Rationale

1. **Cost and complexity**: As a small team, we need to focus on delivering value quickly
2. **Network effects**: Data aggregation is core to our value proposition
3. **Solution maturity**: PostgreSQL RLS is mature and battle-tested
4. **Future flexibility**: We can migrate specific tenants to dedicated schemas/DBs as needed

## Technical Implementation

### 1. Base Schema with `tenant_id`

```sql
-- Base table with mandatory tenant_id
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    user_id UUID NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    -- other fields...
    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

-- Index for tenant query performance
CREATE INDEX idx_jobs_tenant_id ON jobs(tenant_id);

-- RLS Policy
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;

-- Policy for SELECT
CREATE POLICY tenant_isolation_select ON jobs
    FOR SELECT
    USING (tenant_id = current_setting('app.current_tenant')::UUID);

-- Policy for INSERT
CREATE POLICY tenant_isolation_insert ON jobs
    FOR INSERT
    WITH CHECK (tenant_id = current_setting('app.current_tenant')::UUID);

-- Policy for UPDATE
CREATE POLICY tenant_isolation_update ON jobs
    FOR UPDATE
    USING (tenant_id = current_setting('app.current_tenant')::UUID)
    WITH CHECK (tenant_id = current_setting('app.current_tenant')::UUID);

-- Policy for DELETE
CREATE POLICY tenant_isolation_delete ON jobs
    FOR DELETE
    USING (tenant_id = current_setting('app.current_tenant')::UUID);
```

### 2. FastAPI Middleware for Tenant Context

```python
from fastapi import Request, HTTPException
from typing import Optional
import asyncpg
from contextvars import ContextVar

# Context variable for tenant_id
current_tenant: ContextVar[Optional[str]] = ContextVar('current_tenant', default=None)

class TenantMiddleware:
    """Middleware to inject tenant_id into PostgreSQL context"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Extract tenant_id from header, JWT, or subdomain
            tenant_id = self._extract_tenant_id(request)
            
            if not tenant_id and not self._is_public_route(request.url.path):
                # Return 401 if no tenant_id on protected routes
                response = Response(content="Tenant not identified", status_code=401)
                await response(scope, receive, send)
                return
            
            # Set in context
            current_tenant.set(tenant_id)
            
            # Continue with request
            await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)
    
    def _extract_tenant_id(self, request: Request) -> Optional[str]:
        """Extract tenant_id from various possible sources"""
        # 1. X-Tenant-ID Header (for APIs)
        if "x-tenant-id" in request.headers:
            return request.headers["x-tenant-id"]
        
        # 2. JWT Token
        if "authorization" in request.headers:
            # Decode JWT and extract tenant_id
            token = request.headers["authorization"].replace("Bearer ", "")
            # payload = decode_jwt(token)
            # return payload.get("tenant_id")
        
        # 3. Subdomain (e.g., acme.validahub.com)
        host = request.headers.get("host", "")
        if "." in host:
            subdomain = host.split(".")[0]
            if subdomain not in ["www", "api", "app"]:
                return subdomain
        
        return None
    
    def _is_public_route(self, path: str) -> bool:
        """Check if route is public"""
        public_routes = ["/health", "/docs", "/openapi.json", "/auth/login", "/auth/register"]
        return any(path.startswith(route) for route in public_routes)
```

### 3. Repository with Tenant Context

```python
from typing import Optional, List
import asyncpg
from contextvars import ContextVar

class BaseRepository:
    """Base repository with multi-tenancy support"""
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
    
    async def _execute_with_tenant(self, query: str, *args, tenant_id: Optional[str] = None):
        """Execute query with tenant context"""
        async with self.db_pool.acquire() as conn:
            # Set tenant_id in PostgreSQL session context
            tenant = tenant_id or current_tenant.get()
            if tenant:
                await conn.execute(f"SET app.current_tenant = '{tenant}'")
            
            # Execute query
            result = await conn.fetch(query, *args)
            
            # Clear context
            if tenant:
                await conn.execute("RESET app.current_tenant")
            
            return result

class JobRepository(BaseRepository):
    """Job repository with automatic tenant isolation"""
    
    async def create_job(self, job_data: dict) -> dict:
        """Create a new job for current tenant"""
        # tenant_id is automatically injected from context
        tenant_id = current_tenant.get()
        if not tenant_id:
            raise ValueError("No tenant context set")
        
        query = """
            INSERT INTO jobs (tenant_id, user_id, status, file_name, marketplace)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *
        """
        
        result = await self._execute_with_tenant(
            query,
            tenant_id,
            job_data['user_id'],
            job_data['status'],
            job_data['file_name'],
            job_data['marketplace']
        )
        
        return dict(result[0])
    
    async def get_jobs(self, limit: int = 100) -> List[dict]:
        """Return jobs from current tenant (RLS ensures isolation)"""
        query = "SELECT * FROM jobs ORDER BY created_at DESC LIMIT $1"
        results = await self._execute_with_tenant(query, limit)
        return [dict(row) for row in results]
```

### 4. Protected Views for Joins

```sql
-- View for safe joins between tables
CREATE OR REPLACE VIEW v_jobs_with_results AS
SELECT 
    j.*,
    jr.total_rows,
    jr.valid_rows,
    jr.invalid_rows,
    jr.corrected_rows
FROM jobs j
LEFT JOIN job_results jr ON j.id = jr.job_id 
    AND j.tenant_id = jr.tenant_id  -- Ensure join by tenant
WHERE j.tenant_id = current_setting('app.current_tenant')::UUID;

-- Apply RLS to view as well
ALTER VIEW v_jobs_with_results SET (security_barrier = true);
```

## Consequences

### Positive

1. **Optimized cost**: Single PostgreSQL cluster for all tenants in MVP
2. **Accelerated time-to-market**: Simpler and faster development
3. **Facilitated analytics**: Direct cross-tenant queries to generate market insights
4. **Instant onboarding**: New customers provisioned in seconds
5. **Unified maintenance**: Single schema and code version

### Negative

1. **Noisy neighbor risk**: Intensive use by one tenant can impact others
2. **Future migration complexity**: Moving from shared to isolated is complex
3. **Shared limits**: Connection pool, CPU, memory divided
4. **Leakage risk**: RLS bug could expose data between tenants
5. **Complex granular backup**: Restoring single tenant data requires scripting

## Evolution Plan

### Phase 1: MVP (0-100 customers)
- **Architecture**: Shared DB + RLS
- **Focus**: Validate product-market fit
- **Monitoring**: Usage metrics per tenant

### Phase 2: Growth (100-1000 customers)
- **Hybrid architecture**: 
  - Majority in shared DB
  - Enterprise customers in dedicated schema
- **BI/DW**: ClickHouse or BigQuery for analytics
- **Cache**: Redis with namespace per tenant

### Phase 3: Scale (1000+ customers)
- **Tier segmentation**:
  - Free/Starter: Shared DB
  - Pro: Dedicated schema
  - Enterprise: Dedicated DB with SLA
- **Data Lake**: Separate layer for BI with pseudonymization
- **Edge caching**: CDN for assets per tenant

## Pitfalls and Mitigation

### 1. Ensure `tenant_id` in all tables

```python
# Development-time validation
def validate_migration(migration_file: str):
    """Validate that all CREATE TABLE include tenant_id"""
    with open(migration_file) as f:
        content = f.read()
        if "CREATE TABLE" in content and "tenant_id UUID NOT NULL" not in content:
            raise ValueError(f"Migration {migration_file} creates table without tenant_id")
```

### 2. Apply RLS by default

```sql
-- Trigger to automatically apply RLS to new tables
CREATE OR REPLACE FUNCTION apply_rls_to_new_tables()
RETURNS event_trigger AS $$
DECLARE
    obj record;
BEGIN
    FOR obj IN SELECT * FROM pg_event_trigger_ddl_commands() WHERE command_tag = 'CREATE TABLE'
    LOOP
        -- Automatically enable RLS
        EXECUTE format('ALTER TABLE %s ENABLE ROW LEVEL SECURITY', obj.object_identity);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

CREATE EVENT TRIGGER auto_enable_rls ON ddl_command_end
WHEN TAG IN ('CREATE TABLE')
EXECUTE FUNCTION apply_rls_to_new_tables();
```

### 3. Selective Backup/Restore

```bash
#!/bin/bash
# Script for specific tenant backup

TENANT_ID=$1
DB_URL=$2

# Export only tenant data
pg_dump $DB_URL \
  --data-only \
  --where="tenant_id='$TENANT_ID'" \
  --file="backup_tenant_${TENANT_ID}_$(date +%Y%m%d).sql"
```

### 4. Isolation Monitoring

```python
# Health check to validate isolation
async def test_tenant_isolation():
    """Test that queries don't leak data between tenants"""
    # Create two test tenants
    tenant_a = await create_test_tenant("test_a")
    tenant_b = await create_test_tenant("test_b")
    
    # Insert data in tenant_a
    async with tenant_context(tenant_a):
        job_a = await job_repo.create_job({"name": "Job A"})
    
    # Try to access from tenant_b
    async with tenant_context(tenant_b):
        jobs = await job_repo.get_jobs()
        assert len(jobs) == 0, "CRITICAL: Tenant isolation breach detected!"
    
    return True
```

## Success Metrics

1. **Zero data leaks between tenants** (measured by automated tests)
2. **Cost per tenant < $2/month** in MVP
3. **New tenant provisioning < 5 seconds**
4. **Query p99 latency < 100ms** even with 100+ tenants
5. **Cross-tenant report generation < 10 seconds**

## References

- [PostgreSQL Row Level Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Multi-tenant SaaS patterns on AWS](https://docs.aws.amazon.com/wellarchitected/latest/saas-lens/multi-tenant-architecture.html)
- [Stripe's approach to multi-tenancy](https://stripe.com/blog/online-migrations)
- [Building Multi-Tenant SaaS with PostgreSQL](https://www.citusdata.com/blog/2016/08/10/sharding-for-a-multi-tenant-app-with-postgres/)

## Conclusion

> **Decision: Adopt multi-tenant architecture with `tenant_id` + RLS for MVP, due to cost, operational simplicity, and compatibility with network effects, selectively evolving to schema/db-per-tenant as required by compliance/performance.**

This approach allows us to launch quickly, keep costs low, and create value through aggregated data, while maintaining the flexibility to evolve the architecture as we scale and serve different customer segments.