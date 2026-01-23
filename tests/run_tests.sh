#!/bin/bash
# Run all tests with coverage report

set -e

echo "Running pytest with coverage..."
pytest tests/ -v --cov=create_image --cov-report=term-missing --cov-report=html

echo ""
echo "Coverage report generated in htmlcov/index.html"
echo ""
echo "To view coverage:"
echo "  open htmlcov/index.html    # macOS"
echo "  start htmlcov/index.html   # Windows"
