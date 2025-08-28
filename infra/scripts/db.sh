#!/bin/bash

# Database management script for ValidaHub

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

function print_help() {
    echo "ValidaHub Database Management"
    echo ""
    echo "Usage: ./scripts/db.sh [command]"
    echo ""
    echo "Commands:"
    echo "  up        Start PostgreSQL and Redis containers"
    echo "  down      Stop all containers"
    echo "  reset     Reset database (delete all data)"
    echo "  migrate   Run Alembic migrations"
    echo "  seed      Load development seed data"
    echo "  shell     Open PostgreSQL shell"
    echo "  logs      Show container logs"
    echo "  status    Show container status"
    echo ""
}

function db_up() {
    echo -e "${GREEN}Starting database containers...${NC}"
    docker-compose up -d postgres redis pgadmin
    echo -e "${GREEN}Waiting for PostgreSQL to be ready...${NC}"
    sleep 5
    docker-compose exec -T postgres pg_isready -U validahub
    echo -e "${GREEN}Database is ready!${NC}"
    echo ""
    echo "Services running:"
    echo "  PostgreSQL: localhost:5432"
    echo "  pgAdmin:    http://localhost:5050"
    echo "  Redis:      localhost:6379"
}

function db_down() {
    echo -e "${YELLOW}Stopping database containers...${NC}"
    docker-compose down
}

function db_reset() {
    echo -e "${RED}WARNING: This will delete all data!${NC}"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v
        echo -e "${GREEN}Database reset complete${NC}"
    else
        echo "Cancelled"
    fi
}

function db_migrate() {
    echo -e "${GREEN}Running migrations...${NC}"
    cd apps/api
    alembic upgrade head
    cd ../..
    echo -e "${GREEN}Migrations complete${NC}"
}

function db_seed() {
    echo -e "${GREEN}Loading seed data...${NC}"
    
    # Option 1: Python seed script (if exists)
    if [ -f "apps/api/scripts/seed.py" ]; then
        cd apps/api
        python scripts/seed.py
        cd ../..
    fi
    
    # Option 2: SQL seed file
    if [ -f "scripts/demo_data.sql" ]; then
        echo -e "${GREEN}Loading SQL demo data...${NC}"
        docker-compose exec -T postgres psql -U validahub -d validahub_db < scripts/demo_data.sql
    fi
    
    echo -e "${GREEN}Seed data loaded${NC}"
}

function db_shell() {
    echo -e "${GREEN}Opening PostgreSQL shell...${NC}"
    docker-compose exec postgres psql -U validahub -d validahub_db
}

function db_logs() {
    docker-compose logs -f postgres redis
}

function db_status() {
    echo -e "${GREEN}Container status:${NC}"
    docker-compose ps
}

# Main script
case "$1" in
    up)
        db_up
        ;;
    down)
        db_down
        ;;
    reset)
        db_reset
        ;;
    migrate)
        db_migrate
        ;;
    seed)
        db_seed
        ;;
    shell)
        db_shell
        ;;
    logs)
        db_logs
        ;;
    status)
        db_status
        ;;
    *)
        print_help
        ;;
esac