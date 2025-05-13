#!/bin/bash

# Set environment variables for testing
export TESTING=1
export DATABASE_URL=sqlite+aiosqlite:///./test.db

# Run pytest with specific filters to ignore bcrypt warnings
PYTHONWARNINGS="ignore::DeprecationWarning:passlib.handlers.bcrypt" python -m pytest tests/ -v

# Exit with the status code from pytest
exit $? 