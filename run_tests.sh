#!/bin/bash
# Script to run tests

echo "Running tests..."

# Run all tests
pytest -v

# Run with coverage
# pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
# pytest tests/test_expense_splits.py -v

# Run specific test
# pytest tests/test_expense_splits.py::test_equal_split_with_rounding -v

