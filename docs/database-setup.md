# Database Setup Guide

## Overview

ValidaHub uses PostgreSQL as the main database and Redis for caching and async job queues.

## Quick Start

### 1. Start the Database

```bash
# Start PostgreSQL, Redis, and pgAdmin
./scripts/db.sh up

# Or using docker-compose directly
docker-compose up -d
```

Services will be available at:
- **PostgreSQL**: `localhost:5432`
- **pgAdmin**: `http://localhost:5050`
- **Redis**: `localhost:6379`

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings (optional)
```

### 3. Run Migrations

```bash
# Navigate to API directory
cd apps/api

# Run migrations
alembic upgrade head
```

## Database Management

### Using the Helper Script

```bash
# Start services
./scripts/db.sh up

# Stop services
./scripts/db.sh down

# Reset database (WARNING: deletes all data)
./scripts/db.sh reset

# Run migrations
./scripts/db.sh migrate

# Open PostgreSQL shell
./scripts/db.sh shell

# View logs
./scripts/db.sh logs

# Check status
./scripts/db.sh status
```

### Manual Commands

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U validahub -d validahub_db

# Connect to Redis
docker-compose exec redis redis-cli -a redis_dev_2024

# Backup database
docker-compose exec postgres pg_dump -U validahub validahub_db > backup.sql

# Restore database
docker-compose exec -T postgres psql -U validahub validahub_db < backup.sql
```

## pgAdmin Access

1. Open `http://localhost:5050`
2. Login with:
   - Email: `admin@validahub.local`
   - Password: `admin_dev_2024`
3. Add server:
   - Host: `postgres` (or `host.docker.internal` on Mac)
   - Port: `5432`
   - Database: `validahub_db`
   - Username: `validahub`
   - Password: `validahub_dev_2024`

## Database Schema

### Core Tables

#### users
- User authentication and profile data
- Roles: admin, user, viewer

#### jobs
- Async job processing status
- File processing history

#### files
- Uploaded CSV files metadata
- S3 references

#### validation_history (to be created)
- Validation results history
- Error statistics

#### templates (to be created)
- User-defined mapping templates
- Marketplace-specific configurations

#### correction_cache (to be created)
- Cached corrections for performance
- Pattern-based auto-corrections

## Migrations

### Create a New Migration

```bash
cd apps/api
alembic revision -m "description of changes"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

### View Migration History

```bash
alembic history
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 5432
lsof -i :5432

# Kill the process
kill -9 <PID>
```

### Permission Denied

```bash
# Fix permissions on volumes
sudo chown -R $USER:$USER postgres_data pgadmin_data redis_data
```

### Connection Refused

1. Check if containers are running:
```bash
docker-compose ps
```

2. Check logs:
```bash
docker-compose logs postgres
```

3. Verify network:
```bash
docker network ls
docker network inspect validahub-new_validahub-network
```

## Production Considerations

1. **Security**:
   - Change all default passwords
   - Use SSL/TLS connections
   - Implement connection pooling
   - Regular backups

2. **Performance**:
   - Configure PostgreSQL tuning
   - Set up read replicas
   - Implement query optimization
   - Use connection pooling (pgBouncer)

3. **Monitoring**:
   - Set up pg_stat_statements
   - Monitor slow queries
   - Track connection usage
   - Set up alerts

## Backup Strategy

### Daily Backups

```bash
# Create backup script
cat > scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U validahub validahub_db | gzip > $BACKUP_DIR/backup_$TIMESTAMP.sql.gz
# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
EOF

chmod +x scripts/backup.sh

# Add to crontab
# 0 2 * * * /path/to/scripts/backup.sh
```

## Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Docker Compose Reference](https://docs.docker.com/compose/)