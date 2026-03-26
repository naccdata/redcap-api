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

## Versioning and Releases

Version numbers must be updated in three places before merging:

1. `CHANGELOG.md` — add a new section for the version with a description of changes
2. `BUILD` — update the `version` in `python_artifact()` (e.g., `version="0.1.5"`)
3. `pyproject.toml` — update the `version` field to match

For example, for the core library these files are:
- `common/CHANGELOG.md`
- `common/src/python/redcap_api/BUILD`
- `common/src/python/redcap_api/pyproject.toml`

### Release Process

The CI build (`.github/workflows/build.yml`) triggers on git tags matching `v*`. At build time, it overrides the `version=` line in BUILD files using `sed` to match the git tag. This means the git tag is the source of truth for the released artifact version.

To release:
1. Ensure all three version files are updated and merged to main
2. Create and push a git tag: `git tag v0.1.5 && git push origin v0.1.5`
3. The workflow will lint, test, build, and upload the packages as a GitHub release

Note: The workflow only overrides BUILD file versions, not `pyproject.toml`. Since Pants uses the BUILD file's `python_artifact` version for packaging, this doesn't affect the built artifact. Keep `pyproject.toml` in sync manually for consistency.

## Before Committing

Always run before pushing:
```bash
pants fmt ::
pants lint ::
pants test ::
```
