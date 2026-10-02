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

The **git tag is the single source of truth** for the released version. The
`version` fields committed in `BUILD` and `pyproject.toml` are intentionally
left at the `0.0.0` placeholder — do not bump them by hand. At build time the
release workflow overwrites every component's version to match the tag, so a
committed value would only drift.

When preparing a release, update only the changelog:

- `CHANGELOG.md` — add a new section for the version with a description of changes
  (for the core library this is `common/CHANGELOG.md`)

Leave these at `0.0.0`:
- `common/src/python/redcap_api/BUILD`
- `common/src/python/redcap_api/pyproject.toml`
- `tools/redcap_error_checks_import/src/python/redcap_error_checks_import/BUILD`

### Release Process

The CI build (`.github/workflows/build.yml`) triggers on git tags matching `v*`.
At build time it rewrites the `version` line in every packaged component's
`BUILD` and `pyproject.toml` to match the tag (minus the leading `v`), then
lints, tests, builds, and uploads the packages as a GitHub release.

To release:
1. Ensure the changelog is updated and merged to main
2. Create and push a git tag: `git tag v0.1.5 && git push origin v0.1.5`
3. The workflow does the rest

Note: the tag version applies to all packaged components at once (the core
library and the tools share the tag). Because the committed versions are
placeholders, there is nothing to keep in sync manually.

## Before Committing

Always run before pushing:
```bash
pants fmt ::
pants lint ::
pants test ::
```
