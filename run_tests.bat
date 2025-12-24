@echo off
REM Script to run tests on Windows

echo Running tests...

REM Run all tests
pytest -v

REM Run with coverage
REM pytest --cov=app --cov-report=html --cov-report=term

REM Run specific test file
REM pytest tests/test_expense_splits.py -v

REM Run specific test
REM pytest tests/test_expense_splits.py::test_equal_split_with_rounding -v

