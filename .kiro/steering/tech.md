---
inclusion: auto
---

# Technology Stack

## Development Environment

**Dev Container** - Consistent development environment using Docker

This project uses dev containers for reproducible development environments. All commands should be executed inside the dev container.

### Container Management Scripts

Located in `bin/` directory:

- `start-devcontainer.sh` - Start the dev container (idempotent, safe to run multiple times)
- `stop-devcontainer.sh` - Stop the dev container
- `build-container.sh` - Rebuild the container after configuration changes
- `exec-in-devcontainer.sh` - Execute a command in the running container
- `terminal.sh` - Open an interactive shell in the container

**CRITICAL**: Always run `./bin/start-devcontainer.sh` before executing any commands to ensure the container is running.

## Build System

**Pants Build System** (v2.29.0) - <https://www.pantsbuild.org>

Pants is used for all builds, testing, linting, and packaging in this project.

## Language & Runtime

- **Python 3.12** (strict interpreter constraint: `==3.12.*`)
- Type checking with mypy
- Dev container provides Python 3.12 pre-installed

## Key Dependencies

### REDCap API

- `requests>=2.18.4` - HTTP library for REDCap API calls

### Testing Libraries

- `pytest>=7.2.0` - Testing framework

## Code Quality Tools

### Linting & Formatting

- **Ruff** - Fast Python linter and formatter
  - Line length: 88 characters
  - Indent: 4 spaces
  - Selected rules: A, B, E, W, F, I, RUF, SIM, C90, PLW0406, COM818, SLF001
  - Used for both code and BUILD file formatting

### Preventing E501 Line Length Errors

**CRITICAL**: Avoid E501 line length violations (lines > 88 characters) by using these patterns:

**❌ Avoid long strings inline:**
```python
long_url = "https://redcap.example.com/api/very/long/endpoint/path/that/exceeds/line/length"  # E501 error!
```

**✅ Use constants or string concatenation:**
```python
# Option 1: Constants
BASE_URL = "https://redcap.example.com/api"
ENDPOINT = "/very/long/endpoint/path"

# Option 2: String concatenation
long_url = (
    "https://redcap.example.com/api/very/long/"
    "endpoint/path/that/exceeds/line/length"
)
```

### Type Checking

- **mypy** with strict type checking
- `warn_unused_configs = True`
- `check_untyped_defs = True`

### Testing

- **pytest** with verbose output (`-vv`)

#### Using Tests for Information Gathering

When writing exploratory tests to gather information about behavior (e.g., debugging API responses, investigating data formats), add a failing assertion at the end to ensure output is printed:

```python
def test_investigate_api_response():
    """Exploratory test to understand API response structure."""
    # Gather information
    response = {"project_id": "123", "title": "Test Project"}
    
    print(f"Response keys: {response.keys()}")
    print(f"Response values: {response.values()}")
    
    # Force test to fail so output is printed
    assert False, "Exploratory test - review output above"
```

**Remember:** Delete these exploratory tests once you've learned what you needed. They should not be committed to the repository.

## Docker

### Dev Container

- Base image: Python 3.12 dev container
- Features: Docker-in-Docker
- VS Code extensions: Python, Docker, Ruff, Code Spell Checker
- Configuration: `.devcontainer/devcontainer.json`

## Common Commands

**IMPORTANT**: All commands must be executed inside the dev container. Use the wrapper scripts in `bin/` or open an interactive shell.

### Setup

```bash
# Ensure container is running (always run this first)
./bin/start-devcontainer.sh

# Install Pants
./bin/exec-in-devcontainer.sh bash get-pants.sh
```

### Building Distributions

```bash
# Build core library
./bin/exec-in-devcontainer.sh pants package common::

# Build specific tool
./bin/exec-in-devcontainer.sh pants package tools/redcap_error_checks_import::
```

### Code Quality

**IMPORTANT**: Always run `pants fmt` before `pants lint` to automatically fix formatting and import issues.

```bash
# Format code (ALWAYS run this first)
./bin/exec-in-devcontainer.sh pants fmt ::

# Run linters (after fmt)
./bin/exec-in-devcontainer.sh pants lint ::

# Type check
./bin/exec-in-devcontainer.sh pants check ::

# Run all checks (ALWAYS run fmt first to auto-fix issues)
./bin/exec-in-devcontainer.sh pants fmt :: && pants lint :: && pants check ::
```

### Testing

```bash
# Run all tests
./bin/exec-in-devcontainer.sh pants test ::

# Run tests with force flag (ignore cache)
./bin/exec-in-devcontainer.sh pants test :: --test-force

# Run tests for specific tool
./bin/exec-in-devcontainer.sh pants test tools/redcap_error_checks_import/test/python::

# Run specific test file
./bin/exec-in-devcontainer.sh pants test tools/redcap_error_checks_import/test/python/test_utils.py

# Run specific test method (use -- to pass pytest arguments)
./bin/exec-in-devcontainer.sh pants test tools/redcap_error_checks_import/test/python/test_utils.py -- -k test_method_name

# Run tests with verbose output
./bin/exec-in-devcontainer.sh pants test :: -- -v
```

### Interactive Shell (Recommended for Multiple Commands)

```bash
# Open shell in container
./bin/terminal.sh

# Then run commands directly:
pants fmt ::
pants lint ::
pants check ::
pants test ::
pants package common::
```

### Development Workflow

```bash
# Ensure container is running
./bin/start-devcontainer.sh

# Option 1: Run commands via wrapper
./bin/exec-in-devcontainer.sh pants fmt ::
./bin/exec-in-devcontainer.sh pants lint ::
./bin/exec-in-devcontainer.sh pants check ::
./bin/exec-in-devcontainer.sh pants test ::

# Option 2: Open interactive shell
./bin/terminal.sh
# Then run: pants fmt :: && pants lint :: && pants check :: && pants test ::

# Stop container when done
./bin/stop-devcontainer.sh
```

## Python Interpreter Setup

The dev container provides Python 3.12 pre-installed. No manual Python installation needed.

For local development outside the container, Pants searches for Python interpreters in:

1. System PATH
2. pyenv installations

Ensure Python 3.12 is available via one of these methods.

## Design Principles

### Dependency Injection over Flag Parameters

**Prefer dependency injection over boolean flags for configurable behavior.**

When designing classes that need configurable behavior, use dependency injection with strategy patterns rather than boolean flag parameters.

**❌ Avoid:**

```python
class RecordProcessor:
    def __init__(self, records: List[dict], use_fast_mode: bool = False):
        self.records = records
        self.use_fast_mode = use_fast_mode
    
    def process(self):
        if self.use_fast_mode:
            return self._fast_process()
        else:
            return self._thorough_process()
```

**✅ Prefer:**

```python
ProcessingStrategy = Callable[[List[dict]], Any]

def fast_strategy(records: List[dict]) -> Any:
    # Fast processing implementation
    pass

def thorough_strategy(records: List[dict]) -> Any:
    # Thorough processing implementation
    pass

class RecordProcessor:
    def __init__(self, records: List[dict], strategy: ProcessingStrategy = thorough_strategy):
        self.records = records
        self.strategy = strategy
    
    def process(self):
        return self.strategy(self.records)
```

**Benefits:**

- **Extensibility**: Easy to add new strategies without modifying existing code
- **Testability**: Each strategy can be tested independently
- **Single Responsibility**: Each strategy focuses on one approach
- **Open/Closed Principle**: Open for extension, closed for modification
- **Clear Intent**: Strategy names are more descriptive than boolean flags

### REDCap API Design Patterns

#### Error Handling

- Use custom exception classes (e.g., `REDCapConnectionError`)
- Include descriptive error messages with context
- Log errors before raising or returning failure indicators
- Handle API errors gracefully and provide meaningful feedback

#### Connection Management

- Centralize API communication in `REDCapConnection` class
- Reuse connection objects for multiple API calls
- Handle authentication and token management securely
- Use helper methods for consistent error formatting
