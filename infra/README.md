# Infrastructure

This directory contains all infrastructure-related configurations and scripts.

## Structure

```
infra/
├── docker/           # Docker configurations
│   └── docker-compose.yml
├── scripts/          # Infrastructure scripts
│   ├── db.sh        # Database setup script
│   ├── init.sql     # Initial database schema
│   └── demo_data.sql # Demo data for testing
└── kubernetes/       # (Future) Kubernetes manifests
```

## Quick Start

### Local Development with Docker

```bash
# Start all services
cd infra/docker
docker-compose up -d

# Initialize database
cd ../scripts
./db.sh
```

### Database Management

The database scripts in `scripts/` handle:
- Initial schema creation (`init.sql`)
- Demo data loading (`demo_data.sql`)
- Database management utilities (`db.sh`)

## Services

The Docker Compose setup includes:
- PostgreSQL database
- Redis cache
- API service (when running in container mode)

## Environment Variables

See `docker/.env.example` for required environment variables.