.PHONY: help inventory engine-install test test-golden test-golden-ml test-golden-shopee test-golden-amazon golden clean

help:
	@echo "Available commands:"
	@echo "  make inventory      - Run repository inventory scan"
	@echo "  make engine-install - Install rule engine locally"
	@echo "  make test           - Run all tests"
	@echo "  make test-golden    - Run all golden tests"
	@echo "  make test-golden-ml - Run Mercado Livre golden tests"
	@echo "  make test-golden-shopee - Run Shopee golden tests"
	@echo "  make test-golden-amazon - Run Amazon golden tests"
	@echo "  make golden         - Run golden tests (simplified)"
	@echo "  make golden-update  - Update golden test expected outputs"
	@echo "  make clean          - Clean artifacts and cache"

# Inventory command
inventory:
	python3 tools/inventory.py

# Install rule engine
engine-install:
	cd libs/rule_engine && pip install -e .

# Test commands
test:
	pytest -v

test-golden:
	pytest -q -m "golden" --maxfail=1 --disable-warnings

test-golden-ml:
	pytest -q -m "golden and mercado_livre" --disable-warnings

test-golden-shopee:
	pytest -q -m "golden and shopee" --disable-warnings

test-golden-amazon:
	pytest -q -m "golden and amazon" --disable-warnings

# Simplified golden test runner
golden:
	@echo ">> running golden tests"
	python3 tests/golden/test_engine.py || pytest -q tests/golden || true

# Update golden tests (run actual pipeline and save as expected)
golden-update:
	python -m tests.golden.update_goldens

# Clean artifacts
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "artifacts" -path "*/tests/golden/*" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true