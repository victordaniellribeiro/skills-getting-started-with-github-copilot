# FastAPI Tests

This directory contains comprehensive tests for the Mergington High School Activities FastAPI application.

## Test Structure

### Test Files

- **`test_api.py`** - Core API endpoint tests
  - Root endpoint (redirect functionality)
  - Activities endpoint (GET /activities)
  - Signup endpoint (POST /activities/{name}/signup)
  - Delete participant endpoint (DELETE /activities/{name}/participants/{email})
  - Integration scenarios and workflows

- **`test_static.py`** - Static file serving and application structure tests
  - Static file serving (HTML, CSS, JavaScript)
  - Application configuration validation
  - Error handling for invalid routes and methods

- **`test_validation.py`** - Data validation and edge case tests
  - Email validation patterns
  - Activity name handling with special characters
  - Data consistency and integrity checks
  - Edge cases (unicode, case sensitivity, long emails)
  - Performance tests

### Configuration Files

- **`conftest.py`** - Pytest configuration and fixtures
- **`__init__.py`** - Makes the tests directory a Python package
- **`../pytest.ini`** - Pytest configuration file

## Running Tests

### Basic Test Run
```bash
pytest tests/ -v
```

### With Coverage Report
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

### Generate HTML Coverage Report
```bash
pytest tests/ --cov=src --cov-report=html
```

### Using the Test Runner Script
```bash
./run_tests.sh
```

## Test Coverage

The test suite achieves **100% code coverage** of the FastAPI application, ensuring all endpoints and functionality are thoroughly tested.

## Test Categories

### Unit Tests
- Individual endpoint functionality
- Data validation
- Error handling

### Integration Tests
- Complete workflow scenarios
- Multi-step operations (signup → verify → delete)
- Cross-endpoint interactions

### Performance Tests
- Response time validation
- Repeated request handling
- Concurrent operation simulation

### Edge Case Tests
- Unicode character handling
- URL encoding scenarios
- Boundary conditions
- Invalid input handling

## Dependencies

The following packages are required for testing:

- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `httpx` - HTTP client for FastAPI testing

All dependencies are listed in `requirements.txt` and will be installed automatically when setting up the project.

## Test Results

When all tests pass, you should see:
- 34 tests collected and passed
- 100% code coverage
- No missing lines in coverage report
- All functionality validated across different scenarios

## Continuous Integration

These tests are designed to be run in CI/CD pipelines and provide comprehensive validation of the FastAPI application's functionality.