---
inclusion: auto
description: Testing guidelines including test organization, pytest usage, and test structure
---

# Testing Guidelines

## Test Organization

- Tests are located in `test/python/` directories parallel to `src/python/`
- Test files should be named `test_*.py`
- Each test directory needs a BUILD file

## Running Tests

```bash
# Run all tests
pants test ::

# Run specific test file
pants test tools/redcap_error_checks_import/test/python/test_utils.py

# Force run (ignore cache)
pants test :: --test-force

# Verbose output
pants test :: -vv
```

Pytest is configured with `-vv` (very verbose) by default in `pants.toml`.

## Test Structure

- Use pytest framework
- Group related tests in classes if needed
- Use descriptive test function names: `test_<what>_<condition>_<expected>`
- Use fixtures for common setup
- Mock external dependencies (API calls, file I/O, etc.)

## Test Coverage

- Write tests for all public APIs
- Test both success and error paths
- Test edge cases and boundary conditions
- Mock REDCap API responses to avoid external dependencies

## Assertions

- Use pytest's assert statements
- Provide descriptive failure messages when helpful
- Test specific exception types with `pytest.raises()`
