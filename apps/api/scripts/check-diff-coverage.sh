#!/bin/bash
# Check diff coverage for changes against main branch

set -e

echo "🔍 Checking diff coverage for changes..."

# Ensure we're in the API directory
cd "$(dirname "$0")/.."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run tests with coverage
echo "📊 Running tests with coverage..."
python -m pytest tests/ --cov=src --cov-report=xml --cov-report=term --no-cov-on-fail -q

# Check if we have changes against main
if git diff --quiet origin/main HEAD; then
    echo "✅ No changes detected against main branch"
    exit 0
fi

# Generate diff coverage report
echo "📈 Generating diff coverage report..."
diff-cover coverage.xml --compare-branch=origin/main --fail-under=85

# Check diff coverage for specific directories
echo ""
echo "📁 Directory-specific diff coverage:"
echo "=================================="

# Services (should have 90% coverage)
diff-cover coverage.xml --compare-branch=origin/main --include="src/services/*" --fail-under=90 || true

# Validators (should have 95% coverage)  
diff-cover coverage.xml --compare-branch=origin/main --include="src/validators/*" --fail-under=95 || true

# Core business logic (should have 90% coverage)
diff-cover coverage.xml --compare-branch=origin/main --include="src/core/*" --fail-under=90 || true

echo ""
echo "✅ Diff coverage check complete!"