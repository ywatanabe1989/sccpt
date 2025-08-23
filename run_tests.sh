#!/bin/bash
# Run tests for sccpt package

set -e

echo "Running sccpt tests..."
echo "======================"

# Activate virtual environment if it exists
if [ -f ".env/bin/activate" ]; then
    source .env/bin/activate
elif [ -f ".env-3.11/bin/activate" ]; then
    source .env-3.11/bin/activate
fi

# Run pytest with coverage if available
if python -m pytest --version >/dev/null 2>&1; then
    python -m pytest tests/ -v --tb=short
else
    echo "pytest not installed. Install with: pip install pytest"
    exit 1
fi

echo ""
echo "Tests completed!"