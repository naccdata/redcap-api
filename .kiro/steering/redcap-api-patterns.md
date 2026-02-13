---
inclusion: auto
fileMatchPattern: "**/redcap_*"
---

# REDCap API Patterns

## Architecture

The library follows a layered architecture:

1. `REDCapConnection` - Low-level HTTP communication with REDCap API
2. `REDCapProject` - High-level project operations and business logic
3. `REDCapRepository` - Data access patterns (if applicable)
4. `REDCapParameterStore` - Configuration and credential management

## Common Patterns

### Connection Management
- Use `REDCapConnection` for all API requests
- Handle `REDCapConnectionError` exceptions
- Use `request_json_value()` for JSON responses
- Use `request_text_value()` for CSV/text responses

### Project Operations
- Create projects using `REDCapProject.create(redcap_con)`
- Access project properties via read-only properties
- Use descriptive method names: `export_*`, `import_*`, `add_*`

### Data Export/Import
- Support multiple formats: JSON (default) and CSV
- Use keyword arguments for optional filters
- Return typed values: `List[Dict[str, str]]` for JSON, `str` for CSV
- Use union types for format-dependent returns: `List[Dict[str, str]] | str`

### User Management
- Use role-based permissions via `REDCapRoles` constants
- Support both role assignment and direct permission setting
- Provide helper functions for common permission sets (e.g., `get_nacc_developer_permissions`)

### Error Handling
- Wrap API errors in `REDCapConnectionError`
- Include descriptive error messages with context
- Log errors before raising or returning False
- Use `error_message()` helper for consistent error formatting

### Method Signatures
- Use keyword-only arguments for clarity: `def method(*, param: type)`
- Provide sensible defaults for optional parameters
- Use `Optional[T]` for nullable parameters
- Return `Optional[T]` when operations might not find results

## REDCap API Content Types

Common content types used in API calls:
- `record` - Patient/subject records
- `instrument` - Data collection forms
- `event` - Longitudinal study events
- `user` - User accounts and permissions
- `userRole` - User role definitions
- `userRoleMapping` - User-to-role assignments
- `report` - Saved reports
- `project` - Project metadata
