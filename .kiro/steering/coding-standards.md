---
inclusion: auto
---

# Coding Standards

## Python Style

### Formatting
- Line length: 88 characters (Black-compatible)
- Indentation: 4 spaces
- Formatter: Ruff
- Target: Python 3.12

### Linting Rules (Ruff)
The project enforces these rule categories:
- `A` - Builtins shadowing
- `B` - Bugbear (common bugs and design problems)
- `E`, `W` - PEP 8 errors and warnings
- `F` - Pyflakes (logical errors)
- `I` - Import sorting
- `RUF` - Ruff-specific rules
- `SIM` - Code simplification
- `C90` - McCabe complexity
- `PLW0406` - Import self
- `COM818` - Trailing comma
- `SLF001` - Private member access

### Type Hints
- Use type hints for all function signatures
- MyPy type checking is enabled
- Use `Optional[T]` for nullable types
- Use `List[Dict[str, Any]]` style annotations (not `list[dict]` for consistency with Python 3.9+ style seen in codebase)

### Documentation
- Use docstrings for all public modules, classes, and functions
- Format: Google-style docstrings
- Include Args, Returns, and Raises sections where applicable

### Code Patterns

#### Error Handling
- Use custom exception classes (e.g., `REDCapConnectionError`)
- Log errors with appropriate context
- Raise exceptions with descriptive messages

#### Logging
- Use Python's logging module
- Get logger with `log = logging.getLogger()`
- Log at appropriate levels (error, warning, info, debug)

#### Class Design
- Use properties for read-only attributes (prefix private with `__`)
- Use `@classmethod` for alternative constructors
- Use type hints in `__init__` with `-> None`
- Use keyword-only arguments with `*` separator for clarity

#### API Methods
- Return typed values (List, Dict, int, str, etc.)
- Use Optional for nullable returns
- Provide sensible defaults for optional parameters
- Use descriptive parameter names
