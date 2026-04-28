# Requirements Document

## Introduction

Add an `export_users()` method to the `REDCapProject` class that exports the list of users for a project via the REDCap API. This is the read counterpart to the existing `add_user()` method. The method enables callers to identify all users in a project regardless of whether they have a role assignment — a capability not provided by `export_user_role_assignments()`, which only returns users mapped to roles.

The primary use case is user management workflows that need to identify users who should be suspended from REDCap after their role is unassigned. A user can exist in a project without a role assignment (e.g., added via `add_user` with direct permissions, or had their role removed but still exists in the project).

## Glossary

- **REDCapProject**: The class that provides high-level project operations against the REDCap API, including export and import methods for instruments, user roles, user-role assignments, records, and events.
- **REDCapConnection**: The class managing low-level HTTP communication with the REDCap API, providing `request_json_value()` for JSON responses and `request_text_value()` for text responses.
- **REDCapConnectionError**: The exception class raised when an error occurs connecting to or receiving a response from the REDCap API.
- **User_Record**: A dictionary representing a single user in a REDCap project, containing identity fields (`username`, `email`, `firstname`, `lastname`), metadata fields (`expiration`, `data_access_group`), and privilege flags (e.g., `design`, `user_rights`, `data_export`, `api_export`).
- **Export_Users_Method**: The `export_users()` method on REDCapProject that sends a POST request with `content: "user"` to the REDCap API and returns the list of User_Records as JSON.

## Requirements

### Requirement 1: Export Users API Call

**User Story:** As a developer using the REDCap API library, I want to call `export_users()` on a REDCapProject instance, so that I can retrieve the list of all users in the project with their privileges.

#### Acceptance Criteria

1. WHEN `export_users()` is called, THE Export_Users_Method SHALL send a request to REDCapConnection with the data payload `{"content": "user"}` and the message `"exporting users"`.
2. WHEN `export_users()` is called, THE Export_Users_Method SHALL delegate to `request_json_value()` on the REDCapConnection instance to perform the HTTP POST and parse the JSON response.
3. WHEN the REDCap API returns a successful response, THE Export_Users_Method SHALL return the parsed JSON response as a `List[Dict[str, Any]]`.

### Requirement 2: Return Value Structure

**User Story:** As a developer consuming the export result, I want the returned list to contain user dictionaries with identity and privilege fields, so that I can inspect user details and permissions.

#### Acceptance Criteria

1. WHEN the REDCap API returns user records, THE Export_Users_Method SHALL return each record as a dictionary containing at minimum the keys `username`, `email`, `firstname`, and `lastname`.
2. WHEN the REDCap API returns user records, THE Export_Users_Method SHALL preserve all privilege flag fields (e.g., `design`, `user_rights`, `data_export`, `api_export`) in each returned dictionary without modification.
3. WHEN the REDCap API returns an empty list (no users in the project), THE Export_Users_Method SHALL return an empty list.

### Requirement 3: Error Handling

**User Story:** As a developer calling `export_users()`, I want API and connection errors to propagate as `REDCapConnectionError`, so that I can handle failures consistently with other REDCapProject methods.

#### Acceptance Criteria

1. IF the REDCap API returns an HTTP error response (e.g., 403 Forbidden due to insufficient permissions), THEN THE Export_Users_Method SHALL raise a REDCapConnectionError with a descriptive error message.
2. IF a network or SSL connection failure occurs during the request, THEN THE Export_Users_Method SHALL raise a REDCapConnectionError with a descriptive error message.
3. IF the REDCap API returns a response that cannot be parsed as JSON, THEN THE Export_Users_Method SHALL raise a REDCapConnectionError.

### Requirement 4: Consistency with Existing Export Methods

**User Story:** As a maintainer of the REDCap API library, I want `export_users()` to follow the same implementation pattern as `export_instruments()`, `export_user_roles()`, and `export_user_role_assignments()`, so that the codebase remains consistent and predictable.

#### Acceptance Criteria

1. THE Export_Users_Method SHALL follow the same method structure as `export_instruments()`: define a `message` string, define a `data` dictionary with the `content` key, and return the result of `request_json_value(data=data, message=message)`.
2. THE Export_Users_Method SHALL use the method signature `def export_users(self) -> List[Dict[str, Any]]` with no additional parameters.
3. THE Export_Users_Method SHALL include a docstring that describes the return value, documents the `username`, `email`, `firstname`, and `lastname` keys, and specifies that REDCapConnectionError is raised on error.

### Requirement 5: Test Coverage

**User Story:** As a developer maintaining the library, I want comprehensive unit tests for `export_users()`, so that regressions are caught early.

#### Acceptance Criteria

1. THE test suite SHALL include a test that verifies `export_users()` sends the correct data payload `{"content": "user"}` and message `"exporting users"` to `request_json_value()`.
2. THE test suite SHALL include a test that verifies `export_users()` returns the list of user dictionaries from the mocked `request_json_value()` response.
3. THE test suite SHALL include a test that verifies `export_users()` returns an empty list when `request_json_value()` returns an empty list.
4. THE test suite SHALL include a test that verifies REDCapConnectionError raised by `request_json_value()` propagates to the caller of `export_users()`.
5. THE test suite SHALL use `unittest.mock.create_autospec` to mock REDCapConnection, following the same pattern as the existing `TestExportUserRoleAssignments` test class.
