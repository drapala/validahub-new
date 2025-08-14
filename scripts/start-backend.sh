#!/bin/bash

# ValidaHub Backend Startup Script
# Handles virtual environment setup and dependency management

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_DIR="apps/api"
VENV_DIR="venv"
PORT=${API_PORT:-8000}
HOST=${API_HOST:-0.0.0.0}

# Function to print colored messages
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if we're in the project root
if [ ! -f "package.json" ] || [ ! -d "$API_DIR" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Navigate to API directory
cd "$API_DIR"
print_status "Navigating to API directory"

# Check Python installation
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
print_status "Python $PYTHON_VERSION detected"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    print_warning "Virtual environment not found. Creating..."
    python3 -m venv "$VENV_DIR"
    print_status "Virtual environment created"
else
    print_status "Virtual environment found"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"
print_status "Virtual environment activated"

# Function to check if requirements are installed
check_dependencies() {
    python -c "
import sys
try:
    import fastapi
    import uvicorn
    import pydantic
    sys.exit(0)
except ImportError:
    sys.exit(1)
" 2>/dev/null
}

# Install/update dependencies if needed
if ! check_dependencies; then
    print_warning "Dependencies not installed or outdated. Installing..."
    
    # Upgrade pip first
    pip install --upgrade pip --quiet
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_status "Dependencies installed from requirements.txt"
    else
        print_error "requirements.txt not found!"
        exit 1
    fi
else
    print_status "Dependencies are up to date"
fi

# Check if .env file exists
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    print_warning ".env file not found. Creating from .env.example..."
    cp .env.example .env
    print_status ".env file created"
fi

# Run database migrations if alembic is installed
if command -v alembic &> /dev/null; then
    print_status "Checking database migrations..."
    alembic upgrade head 2>/dev/null || print_warning "Database migrations skipped (database might not be running)"
fi

# Start the backend server
print_status "Starting backend server on http://$HOST:$PORT"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ValidaHub Backend API"
echo "  Docs: http://localhost:$PORT/docs"
echo "  Health: http://localhost:$PORT/health"
echo "  Press Ctrl+C to stop"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run uvicorn with proper error handling
exec uvicorn src.main:app --reload --port "$PORT" --host "$HOST"