.PHONY: help test test-golden test-golden-ml test-golden-shopee test-golden-amazon clean

help:
	@echo "Available commands:"
	@echo "  make test           - Run all tests"
	@echo "  make test-golden    - Run all golden tests"
	@echo "  make test-golden-ml - Run Mercado Livre golden tests"
	@echo "  make test-golden-shopee - Run Shopee golden tests"
	@echo "  make test-golden-amazon - Run Amazon golden tests"
	@echo "  make golden-update  - Update golden test expected outputs"
	@echo "  make clean          - Clean artifacts and cache"

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