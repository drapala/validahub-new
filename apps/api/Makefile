.PHONY: help install test lint format type-check run migrate

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -r requirements.txt
	pip install ruff mypy pytest-cov

test:  ## Run tests
	pytest -v --cov=src --cov-report=term-missing

lint:  ## Run linting
	ruff check src/ tests/ --fix

format:  ## Format code
	ruff format src/ tests/

type-check:  ## Run type checking
	mypy src/ --ignore-missing-imports

run:  ## Run development server
	uvicorn src.main:app --reload --port 3001

migrate:  ## Run database migrations
	alembic upgrade head

migrate-create:  ## Create new migration
	@read -p "Migration name: " name; \
	alembic revision --autogenerate -m "$$name"

clean:  ## Clean cache files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov

check: lint type-check test  ## Run all checks

docker-build:  ## Build Docker image
	docker build -t validahub-backend:local .

docker-run:  ## Run Docker container
	docker run -p 3001:8000 \
		-e DATABASE_URL=postgresql://validahub:validahub@host.docker.internal:5432/validahub \
		-e REDIS_URL=redis://host.docker.internal:6379/0 \
		validahub-backend:local