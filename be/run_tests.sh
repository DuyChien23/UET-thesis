#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Set environment variables for testing
export TESTING=1
export DATABASE_URL=sqlite+aiosqlite:///./test.db

# Run tests
if [ $# -eq 0 ]; then
    # Run all tests if no arguments
    python -m pytest tests -v
else
    # Run specific tests
    python -m pytest "$@" -v
fi 