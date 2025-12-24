# Test Functions Explained

This document explains what each test function does and what it validates.

## Test Folder Structure

```
tests/
├── conftest.py              # Test fixtures and setup (shared across all tests)
├── test_expense_splits.py   # Tests for expense splitting logic
├── test_balances.py         # Tests for balance calculations
└── test_users_groups.py     # Tests for user and group management
```

---

## `conftest.py` - Test Fixtures

This file contains reusable test fixtures (setup code) used by all tests.

### `db_session` fixture
- **What it does**: Creates a fresh in-memory SQLite database for each test
- **Purpose**: Ensures each test runs with a clean database
- **How it works**: 
  - Creates all tables before the test
  - Yields a database session
  - Drops all tables after the test completes

### `client` fixture
- **What it does**: Creates an HTTP test client for making API requests
- **Purpose**: Allows tests to make HTTP requests to the FastAPI app
- **How it works**: 
  - Overrides database and Redis dependencies with test versions
  - Provides an AsyncClient instance
  - Cleans up after the test

### `mock_redis` fixture
- **What it does**: Creates a mock Redis client (doesn't need real Redis)
- **Purpose**: Allows tests to run without a Redis server
- **How it works**: Returns a mock object that simulates Redis operations

### `test_user` fixture
- **What it does**: Creates a single test user in the database
- **Purpose**: Provides a ready-to-use user for tests
- **Returns**: A User object with name "Test User" and email "test@example.com"

### `test_users` fixture
- **What it does**: Creates 3 test users in the database
- **Purpose**: Provides multiple users for group/expense tests
- **Returns**: List of 3 User objects (User 1, User 2, User 3)

### `test_group` fixture
- **What it does**: Creates a test group with one member
- **Purpose**: Provides a ready-to-use group for tests
- **Returns**: A Group object with one member (test_user)

---

## `test_expense_splits.py` - Expense Splitting Tests

### `test_equal_split_with_rounding`
- **What it tests**: EQUAL split type with rounding
- **Scenario**: 
  - Creates a group with 3 users
  - Creates an expense of $100.00 split equally
  - $100 ÷ 3 = $33.33... (doesn't divide evenly)
- **Validates**:
  - ✅ All 3 splits are created
  - ✅ Total of all splits equals $100.00
  - ✅ Amounts are $33.33 or $33.34 (remainder distributed fairly)
- **Why it's important**: Tests that rounding is handled correctly and cents are distributed fairly

### `test_exact_split_validation_failure`
- **What it tests**: EXACT split validation (should fail)
- **Scenario**:
  - Creates an expense with EXACT split type
  - Provides splits that sum to $90.00 but total expense is $100.00
  - Sum doesn't match total (90 ≠ 100)
- **Validates**:
  - ✅ Request fails with 400 status code
  - ✅ Error message indicates sum must equal total
- **Why it's important**: Ensures data integrity - exact splits must match the total

### `test_exact_split_success`
- **What it tests**: EXACT split when validation passes
- **Scenario**:
  - Creates an expense with EXACT split type
  - Provides splits: $60.00 + $40.00 = $100.00
  - Sum matches total correctly
- **Validates**:
  - ✅ Expense is created successfully (201 status)
  - ✅ 2 splits are created
  - ✅ Split amounts are exactly $60.00 and $40.00
- **Why it's important**: Ensures valid exact splits work correctly

### `test_percent_split_validation_failure`
- **What it tests**: PERCENT split validation (should fail)
- **Scenario**:
  - Creates an expense with PERCENT split type
  - Provides percentages: 60% + 30% = 90% (not 100%)
  - Percentages don't sum to 100
- **Validates**:
  - ✅ Request fails with 400 status code
  - ✅ Error message indicates percentages must sum to 100
- **Why it's important**: Ensures percentage splits are valid (must total 100%)

### `test_percent_split_with_rounding`
- **What it tests**: PERCENT split with rounding
- **Scenario**:
  - Creates an expense of $100.00 with PERCENT split
  - Splits: 33.33%, 33.33%, 33.34% (sums to 100%)
  - Calculates amounts from percentages
- **Validates**:
  - ✅ Expense is created successfully
  - ✅ 3 splits are created
  - ✅ Total of split amounts equals $100.00
  - ✅ Percent values are stored correctly
- **Why it's important**: Tests percentage calculation and rounding handling

---

## `test_balances.py` - Balance Calculation Tests

### `test_raw_balances_after_expenses`
- **What it tests**: Raw balance calculation after multiple expenses
- **Scenario**:
  - Creates a group with 3 users
  - User 0 pays $100, split equally (each owes $33.33)
  - User 1 pays $60, split equally (each owes $20)
- **Expected balances**:
  - User 1 owes User 0: $33.33 - $20 = $13.33
  - User 2 owes User 0: $33.33
  - User 2 owes User 1: $20
- **Validates**:
  - ✅ Raw balances are calculated correctly
  - ✅ All balance amounts are positive
  - ✅ Balances reflect the net debts between users
- **Why it's important**: Ensures the ledger-style balance tracking works correctly

### `test_simplified_balances`
- **What it tests**: Simplified balance calculation (greedy algorithm)
- **Scenario**:
  - Creates a group with 2 users
  - User 0 pays $100, split equally
  - User 1 owes User 0 $50
- **Validates**:
  - ✅ Simplified balance shows 1 transfer
  - ✅ User 1 (payer) should pay User 0 (payee) $50
  - ✅ Amount is exactly $50.00
- **Why it's important**: Tests the balance simplification algorithm that minimizes number of transfers

### `test_settlement_reduces_balances`
- **What it tests**: Settlement reduces outstanding balances
- **Scenario**:
  - User 0 pays $100, split equally (User 1 owes $50)
  - User 1 makes a settlement of $30 to User 0
- **Validates**:
  - ✅ Initial balance is $50.00
  - ✅ After settlement, balance is $20.00 ($50 - $30)
  - ✅ Settlement correctly reduces the debt
- **Why it's important**: Ensures settlements update balances correctly

---

## `test_users_groups.py` - User and Group Management Tests

### `test_create_user`
- **What it tests**: Creating a new user via API
- **Scenario**: 
  - Sends POST request to create a user
  - Provides name and email
- **Validates**:
  - ✅ Request succeeds (201 status code)
  - ✅ User has correct name and email
  - ✅ User has an ID
- **Why it's important**: Tests basic user creation endpoint

### `test_get_user`
- **What it tests**: Retrieving a user by ID
- **Scenario**:
  - Uses `test_user` fixture (pre-created user)
  - Sends GET request for that user's ID
- **Validates**:
  - ✅ Request succeeds (200 status code)
  - ✅ Returned user has correct ID and email
- **Why it's important**: Tests user retrieval endpoint

### `test_create_group`
- **What it tests**: Creating a new group via API
- **Scenario**:
  - Sends POST request to create a group
  - Provides group name
- **Validates**:
  - ✅ Request succeeds (201 status code)
  - ✅ Group has correct name
  - ✅ Group has an ID
- **Why it's important**: Tests basic group creation endpoint

### `test_get_group_with_members`
- **What it tests**: Retrieving a group with its members
- **Scenario**:
  - Creates a group
  - Adds a member to the group
  - Retrieves the group
- **Validates**:
  - ✅ Request succeeds (200 status code)
  - ✅ Group has correct name
  - ✅ Group has 1 member
  - ✅ Member has correct user_id
- **Why it's important**: Tests group retrieval with relationship loading (members)

---

## Summary

The test suite covers:

1. **Expense Splitting Logic** (5 tests)
   - Equal splits with rounding
   - Exact splits (validation and success)
   - Percent splits (validation and rounding)

2. **Balance Calculations** (3 tests)
   - Raw balance tracking
   - Simplified balance algorithm
   - Settlement balance reduction

3. **User/Group Management** (4 tests)
   - User creation and retrieval
   - Group creation and retrieval with members

**Total: 12 tests** covering all critical functionality of the expense sharing API.



