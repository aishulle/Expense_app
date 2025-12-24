# Quick Start: Running Tests

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Run Tests

### Option A: Run All Tests (Recommended)
```bash
pytest -v
```

### Option B: Run Specific Test Categories

**Test expense splitting:**
```bash
pytest tests/test_expense_splits.py -v
```

**Test balance calculations:**
```bash
pytest tests/test_balances.py -v
```

**Test user/group endpoints:**
```bash
pytest tests/test_users_groups.py -v
```

### Option C: Run a Single Test

```bash
pytest tests/test_expense_splits.py::test_equal_split_with_rounding -v
```

## What to Expect

You should see output like:

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

## Troubleshooting

**If you get "No module named pytest":**
```bash
pip install pytest pytest-asyncio
```

**If you get import errors:**
Make sure you're in the project root directory and all dependencies are installed:
```bash
pip install -r requirements.txt
```

**For more help:**
See [TESTING.md](TESTING.md) for detailed testing documentation.

