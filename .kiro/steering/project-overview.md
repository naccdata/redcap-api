---
inclusion: auto
---

# NACC REDCap API Project Overview

This repository contains a Python library for interacting with the REDCap API, developed by NACC (National Alzheimer's Coordinating Center).

## Project Structure

- `common/src/python/redcap_api/` - Core REDCap API library
  - `redcap_connection.py` - HTTP connection handling
  - `redcap_project.py` - Project-level API operations
  - `redcap_repository.py` - Repository pattern implementation
  - `redcap_parameter_store.py` - Parameter storage utilities

- `tools/` - Internal tools that utilize the core library
  - `redcap_error_checks_import/` - Tool for importing error checks into REDCap

- `docs/` - Documentation files

## Key Technologies

- Python 3.12 (strict version requirement)
- Pants build system (v2.29.0) for monorepo management
- Ruff for linting
- YAPF for formatting
- MyPy for type checking
- Pytest for testing

## Build System

This is a Pants-based monorepo. Each component has its own BUILD file defining dependencies and build targets. Version numbers are set in BUILD files, not in setup.py or pyproject.toml.
