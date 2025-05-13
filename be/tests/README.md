# API Tests

This directory contains tests for the Digital Signature Verification API, focusing on testing API call flows from a user perspective.

## Test Structure

The tests are organized as follows:

- `conftest.py`: Contains pytest fixtures used across all tests
- `test_auth_api.py`: Tests for authentication flows (register, login, profile management)
- `test_verification_api.py`: Tests for digital signature verification flows
- `test_algorithms_api.py`: Tests for algorithm information endpoints

## Running Tests

The easiest way to run the tests is to use the provided script:

```bash
# From the 'be' directory:
./run_tests.sh

# To run a specific test file:
./run_tests.sh tests/test_auth_api.py

# To run a specific test:
./run_tests.sh tests/test_auth_api.py::test_register_user
```

Alternatively, you can run the tests manually:

```bash
# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Set environment variables
export TESTING=1
export DATABASE_URL=sqlite+aiosqlite:///./test.db

# Run all tests
pytest tests

# Run specific test file
pytest tests/test_auth_api.py

# Run with verbose output
pytest -v tests

# Generate coverage report
pytest --cov=src tests

# Generate detailed HTML coverage report
pytest --cov=src --cov-report=html tests
```

## Test Database

The tests use SQLite as a database backend for tests, which is automatically created and destroyed during test execution. This ensures that tests don't affect your main database.

## Authentication in Tests

The tests use a fixture to create test users and authentication tokens, making it easy to test endpoints that require authentication.

## Debugging Test Issues

If you encounter issues with the tests:

1. Run with verbose output: `./run_tests.sh -v`
2. Check the DEBUG logs which are enabled in pytest.ini
3. Run a single test to isolate the issue: `./run_tests.sh tests/test_auth_api.py::test_register_user`

## Adding New Tests

When adding new tests:

1. Follow the existing patterns in the test files
2. Use appropriate fixtures from `conftest.py`
3. Make sure to test both successful and error cases
4. Consider edge cases that might occur in real user scenarios 