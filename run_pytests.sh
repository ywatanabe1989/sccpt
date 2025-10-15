#!/bin/bash
# Run all tests in the tests directory

set -e

# Add current directory to PYTHONPATH for imports
export PYTHONPATH="$PWD:$PYTHONPATH"

echo "Running pytest on all tests..."
python -m pytest tests/ -v --tb=short

echo "Tests completed successfully!"