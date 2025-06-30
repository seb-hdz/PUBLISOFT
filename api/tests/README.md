# Testing Guide

This directory contains comprehensive tests for the API project, following Clean Architecture principles and Domain-Driven Design patterns.

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_runner.py           # Test runner script
├── README.md               # This file
├── unit/                   # Unit tests
│   ├── test_user_entity.py
│   └── test_value_objects.py
├── integration/            # Integration tests
│   ├── test_auth_endpoints.py
│   └── test_user_repository.py
└── __init__.py
```

## Test Categories

### 1. Unit Tests (`tests/unit/`)

- **Purpose**: Test individual components in isolation
- **Scope**: Domain entities, value objects, services, and business logic
- **Dependencies**: Mocked external dependencies
- **Speed**: Fast execution

**Examples:**

- User entity creation and validation
- Value object validation (Email, UserCode, PasswordHash)
- Domain service logic
- Command/Query handlers

### 2. Integration Tests (`tests/integration/`)

- **Purpose**: Test component interactions and external integrations
- **Scope**: API endpoints, database operations, external services
- **Dependencies**: Real database (in-memory SQLite for testing)
- **Speed**: Medium execution time

**Examples:**

- API endpoint testing with FastAPI TestClient
- Database repository operations
- Message bus integration
- Authentication flow

## Running Tests

### Prerequisites

1. Install test dependencies:

```bash
pip install -r requirements.txt
```

2. Ensure you're in the project root directory.

### Basic Commands

#### Run All Tests

```bash
python -m pytest
```

#### Run Specific Test Categories

```bash
# Unit tests only
python -m pytest -m unit

# Integration tests only
python -m pytest -m integration

# API tests only
python -m pytest -m api

# Authentication tests only
python -m pytest -m auth
```

#### Run Specific Test Files

```bash
# Run specific test file
python -m pytest tests/unit/test_user_entity.py

# Run specific test class
python -m pytest tests/unit/test_user_entity.py::TestUserEntity

# Run specific test method
python -m pytest tests/unit/test_user_entity.py::TestUserEntity::test_user_creation_with_valid_data
```

### Using the Test Runner Script

The `test_runner.py` script provides convenient test execution:

```bash
# Run all tests
python tests/test_runner.py

# Run unit tests only
python tests/test_runner.py --type unit

# Run integration tests with verbose output
python tests/test_runner.py --type integration --verbose

# Run without coverage
python tests/test_runner.py --no-coverage

# Run specific test
python tests/test_runner.py --test tests/unit/test_user_entity.py

# List all available tests
python tests/test_runner.py --list
```

### Coverage Reports

Tests automatically generate coverage reports:

```bash
# Run tests with coverage
python -m pytest

# View coverage in terminal
python -m pytest --cov=modules --cov=common --cov-report=term-missing

# Generate HTML coverage report
python -m pytest --cov=modules --cov=common --cov-report=html:htmlcov
```

Coverage reports are generated in:

- `htmlcov/` - HTML report (open `htmlcov/index.html` in browser)
- `coverage.xml` - XML report for CI/CD integration

## Test Configuration

### Pytest Configuration (`pytest.ini`)

- **Test Discovery**: Automatically finds tests in `tests/` directory
- **Markers**: Defines test categories (unit, integration, api, auth, etc.)
- **Coverage**: Configures coverage reporting with 80% minimum threshold
- **Output**: Verbose output with colored results

### Test Fixtures (`conftest.py`)

Common test fixtures are defined in `conftest.py`:

- **`test_database`**: In-memory SQLite database for testing
- **`db_session`**: Database session for each test
- **`client`**: FastAPI TestClient for API testing
- **`mock_unit_of_work`**: Mocked unit of work
- **`mock_message_bus`**: Mocked message bus
- **`sample_user_data`**: Sample user data for testing
- **`sample_login_data`**: Sample login data for testing

## Writing Tests

### Test Naming Convention

- **Files**: `test_*.py`
- **Classes**: `Test*`
- **Methods**: `test_*`

### Test Structure (AAA Pattern)

```python
def test_something():
    """Test description."""
    # Arrange - Set up test data and conditions
    user_data = {"email": "test@example.com", "password": "test123"}

    # Act - Execute the code being tested
    result = register_user(user_data)

    # Assert - Verify the results
    assert result.status_code == 201
    assert result.json()["message"] == "User registered successfully"
```

### Test Categories with Markers

```python
import pytest

@pytest.mark.unit
def test_user_entity_creation():
    """Unit test for user entity creation."""
    pass

@pytest.mark.integration
def test_user_registration_endpoint():
    """Integration test for user registration endpoint."""
    pass

@pytest.mark.api
def test_auth_endpoints():
    """API test for authentication endpoints."""
    pass

@pytest.mark.auth
def test_login_flow():
    """Authentication-specific test."""
    pass
```

### Mocking External Dependencies

```python
from unittest.mock import patch, Mock

def test_with_mocked_dependency():
    with patch('module.external_service') as mock_service:
        mock_service.return_value = "mocked_result"
        # Test code here
        mock_service.assert_called_once()
```

### Database Testing

```python
def test_database_operation(db_session):
    """Test database operations with real session."""
    repository = UserRepository(db_session)
    user = create_test_user()

    repository.add(user)
    db_session.commit()

    result = repository.get_by_email("test@example.com")
    assert result is not None
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python -m pytest --cov=modules --cov=common --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## Best Practices

### 1. Test Isolation

- Each test should be independent
- Use fixtures for setup and teardown
- Clean up test data after each test

### 2. Descriptive Test Names

- Use clear, descriptive test names
- Follow the pattern: `test_[scenario]_[expected_result]`

### 3. Arrange-Act-Assert

- Structure tests with clear sections
- Keep tests focused on one behavior

### 4. Mock External Dependencies

- Mock external services and APIs
- Use real database for integration tests
- Mock time-dependent operations

### 5. Test Data Management

- Use factories for creating test data
- Keep test data minimal and focused
- Use meaningful test data

### 6. Error Testing

- Test both success and failure scenarios
- Test edge cases and boundary conditions
- Test error handling and exceptions

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running tests from the project root
2. **Database Errors**: Check that test database is properly configured
3. **Mock Issues**: Verify mock setup and assertions
4. **Coverage Issues**: Ensure all code paths are tested

### Debugging Tests

```bash
# Run tests with debug output
python -m pytest -v -s

# Run specific test with debug
python -m pytest tests/unit/test_user_entity.py::TestUserEntity::test_user_creation -v -s

# Run with pdb debugger
python -m pytest --pdb
```

## Contributing

When adding new tests:

1. Follow the existing test structure and naming conventions
2. Add appropriate markers to categorize tests
3. Ensure tests are isolated and don't depend on each other
4. Add comprehensive assertions
5. Update this README if adding new test categories or patterns
