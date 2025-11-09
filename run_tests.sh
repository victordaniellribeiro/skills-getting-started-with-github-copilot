#!/bin/bash

# Test runner script for the FastAPI application

echo "Running FastAPI Tests..."
echo "========================"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "Virtual environment activated"
fi

echo ""
echo "Installing/updating dependencies..."
pip install -r requirements.txt

echo ""
echo "Running tests with coverage..."
python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

echo ""
echo "Test run completed!"
echo ""
echo "Coverage report generated in htmlcov/ directory"
echo "Open htmlcov/index.html in a browser to view detailed coverage"