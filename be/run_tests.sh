#!/bin/bash

# Activate the virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set environment variables for testing
export TESTING=1
export AUTO_CREATE_TABLES=true
export DATABASE_URL=sqlite+aiosqlite:///./test.db
export AUTH_SECRET_KEY="testsecretkeythisiskeyfortestingpurposesonly"
export AUTH_TOKEN_EXPIRE_MINUTES=30
export MOCK_SERVICES=true

# Run the tests with passed arguments
python -m pytest $@ -v

# Deactivate virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi 