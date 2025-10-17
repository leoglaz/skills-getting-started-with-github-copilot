# Tests for Mergington High School Activities API

This directory contains comprehensive tests for the FastAPI application.

## Running Tests

To run all tests:
```bash
pytest tests/ -v
```

To run tests with coverage:
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

## Test Structure

- `conftest.py` - Test configuration and fixtures
- `test_api.py` - API endpoint tests

## Test Coverage

The tests cover:

### Root Endpoint
- Redirect functionality to static files

### Activities Endpoint  
- Retrieving all activities
- Data structure validation
- Activity details verification

### Signup Endpoint
- Successful signups
- Duplicate signup prevention
- Capacity validation  
- Non-existent activity handling
- Multiple activity signups

### Unregister Endpoint
- Successful unregistration
- Non-participant unregistration
- Non-existent activity handling
- Complete signup/unregister workflow

### Edge Cases
- Activity names with spaces
- Various email formats
- Case sensitivity testing

All tests achieve 100% code coverage of the FastAPI application.