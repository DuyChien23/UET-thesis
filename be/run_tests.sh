#!/bin/bash

# Set environment variables for testing
export TESTING=1
export DATABASE_URL=sqlite+aiosqlite:///./test.db

# Run pytest with asyncio debugging options
source venv/bin/activate
python -m pytest tests/test_auth_api.py -v --asyncio-mode=auto --log-cli-level=INFO

# Exit with the status code from pytest
exit $? 