---
inclusion: auto
description: Overview of the NACC REDCap API project structure, technologies, and build system
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

This is a Pants-based monorepo. Each component has its own BUILD file defining dependencies and build targets.

Version numbers must be kept in sync across three files per package: `CHANGELOG.md`, `BUILD` (in `python_artifact()`), and `pyproject.toml`. The CI release workflow overrides the BUILD file version from the git tag at build time, but all three should be updated before merging. See the development workflow steering doc for full release details.
