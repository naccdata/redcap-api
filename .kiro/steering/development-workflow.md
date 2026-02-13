---
inclusion: auto
description: Common Pants commands and development workflow for formatting, testing, and building
---

# Development Workflow

## Common Commands

### Formatting and Linting
```bash
pants fmt ::    # Auto-fix formatting issues
pants lint ::   # Run linter checks
```

### Testing
```bash
pants test ::                    # Run all tests
pants test :: --test-force       # Force run all tests (ignore cache)
pants test path/to/test_file.py  # Run specific test file
```

### Building Distributions
```bash
pants package common::                              # Build core library
pants package tools/redcap_error_checks_import::    # Build specific tool
```

Distributions are created in the `dist/` directory as both sdist and wheel formats.

## Python Environment

- Python 3.12 is required (interpreter_constraints = ["==3.12.*"])
- Pants will search for Python in PATH and PYENV locations
- The project uses a lockfile: `python-default.lock`

## Code Organization

- Source code goes in `src/python/` directories
- Tests go in `test/python/` directories
- Each component needs a BUILD file for Pants configuration
- Version numbers are set in BUILD files

## Before Committing

Always run before pushing:
```bash
pants fmt ::
pants lint ::
pants test ::
```
