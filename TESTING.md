# Testing Guide

This document provides detailed instructions for running tests manually.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run all tests:**
   ```bash
   pytest
   ```

3. **Run with verbose output:**
   ```bash
   pytest -v
   ```

## Test Structure

The tests are organized in the `tests/` directory:

- `tests/test_expense_splits.py` - Tests for expense splitting logic
- `tests/test_balances.py` - Tests for balance calculations
- `tests/test_users_groups.py` - Tests for user and group management
- `tests/conftest.py` - Test fixtures and configuration

## Running Tests

### Run All Tests

```bash
pytest
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Specific Test File

```bash
# Test expense splits (EQUAL, EXACT, PERCENT)
pytest tests/test_expense_splits.py -v

# Test balance calculations
pytest tests/test_balances.py -v

# Test user and group endpoints
pytest tests/test_users_groups.py -v
```

### Run Specific Test Function

```bash
# Run a single test by name
pytest tests/test_expense_splits.py::test_equal_split_with_rounding -v
pytest tests/test_balances.py::test_simplified_balances -v
pytest tests/test_balances.py::test_settlement_reduces_balances -v
```

### Run Tests with Output

```bash
# Show print statements and output
pytest -v -s
```

### Run Tests with Coverage

```bash
# Generate coverage report
pytest --cov=app --cov-report=term --cov-report=html

# View HTML report
# Open htmlcov/index.html in your browser
```

### Run Tests Matching a Pattern

```bash
# Run all tests with "split" in the name
pytest -k split -v

# Run all balance tests
pytest -k balance -v
```

## Test Coverage

The test suite includes:

1. **Expense Split Tests** (`test_expense_splits.py`):
   - ✅ Equal split with rounding (3 members, $100 split)
   - ✅ Exact split validation (sum mismatch should fail)
   - ✅ Exact split success (correct sum)
   - ✅ Percent split validation (sum != 100 should fail)
   - ✅ Percent split with rounding

2. **Balance Tests** (`test_balances.py`):
   - ✅ Raw balances after multiple expenses
   - ✅ Simplified balances correctness
   - ✅ Settlement reduces balances

3. **User/Group Tests** (`test_users_groups.py`):
   - ✅ Create user
   - ✅ Get user by ID
   - ✅ Create group
   - ✅ Get group with members

## Test Environment

- **Database**: In-memory SQLite (no setup required)
- **Redis**: Mocked (no Redis server needed)
- **Isolation**: Each test gets a fresh database
- **Async**: All tests use async/await with pytest-asyncio

## Troubleshooting

### Import Errors

If you get import errors, make sure you're in the project root directory and dependencies are installed:

```bash
pip install -r requirements.txt
```

### Database Errors

Tests use an in-memory SQLite database, so no database setup is needed. If you see database-related errors, check that `aiosqlite` is installed:

```bash
pip install aiosqlite
```

### Async Errors

Make sure `pytest-asyncio` is installed:

```bash
pip install pytest-asyncio
```

### Redis Errors

Redis is mocked in tests, so you shouldn't need a Redis server. If you see Redis errors, check the `mock_redis` fixture in `tests/conftest.py`.

## Example Test Run Output

```
tests/test_expense_splits.py::test_equal_split_with_rounding PASSED
tests/test_expense_splits.py::test_exact_split_validation_failure PASSED
tests/test_expense_splits.py::test_exact_split_success PASSED
tests/test_expense_splits.py::test_percent_split_validation_failure PASSED
tests/test_expense_splits.py::test_percent_split_with_rounding PASSED
tests/test_balances.py::test_raw_balances_after_expenses PASSED
tests/test_balances.py::test_simplified_balances PASSED
tests/test_balances.py::test_settlement_reduces_balances PASSED
tests/test_users_groups.py::test_create_user PASSED
tests/test_users_groups.py::test_get_user PASSED
tests/test_users_groups.py::test_create_group PASSED
tests/test_users_groups.py::test_get_group_with_members PASSED

========================= 12 passed in 2.34s =========================
```

