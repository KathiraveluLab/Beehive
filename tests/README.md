# Tests Directory

This directory contains all test files for the Beehive project.

## Structure

- `conftest.py`: Common fixtures and database setup
  - Test database configuration
  - Flask app test client
  - Database cleanup utilities

- `test_basic.py`: Basic application tests
  - Index route
  - App configuration

- `test_database.py`: Database operations
  - User creation/retrieval
  - Data validation
  - Database utilities

- `test_images.py`: Image handling
  - Image upload/download
  - Metadata management
  - Image operations

- `test_routes.py`: Route accessibility
  - Authentication routes
  - Admin access
  - Static file serving

- `test_user_utils.py`: User utilities
  - Username validation
  - User permissions

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest test_images.py

# Run with coverage
pytest --cov=./ --cov-report=term-missing

# Run specific test
pytest test_routes.py::test_home_route
```

## Writing New Tests

1. Choose the appropriate file based on functionality
2. Use fixtures from `conftest.py`
3. Follow existing test patterns
4. Ensure proper cleanup in database tests
5. Add docstrings to test functions 