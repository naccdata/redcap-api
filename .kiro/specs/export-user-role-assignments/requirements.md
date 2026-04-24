# Requirements Document

## Introduction

Add an `export_user_role_assignments()` method to the `REDCapProject` class that exports the current mapping of users to roles in a REDCap project. This is the export counterpart to the existing `assign_user_role()` method (which imports/updates mappings). The method enables callers to query which users are assigned to which roles before making modifications.

## Glossary

- **REDCapProject**: The class representing a REDCap project, providing methods for interacting with the REDCap API. Defined in `redcap_project.py`.
- **REDCapConnection**: The class managing API requests to a REDCap project, providing `request_json_value` for JSON responses. Defined in `redcap_connection.py`.
- **REDCapConnectionError**: The exception raised when a REDCap API request fails due to connection or response errors.
- **User_Role_Assignment**: A JSON object containing a `username` key and a `unique_role_name` key, representing the mapping of a single user to a role in the project.
- **User_Role_Mapping_Payload**: A data dictionary with `content` set to `"userRoleMapping"`, used to request user-role assignments from the REDCap API. The REDCap API requires `content: "userRoleMapping"` and supports `format` and `returnFormat` parameters (handled by `request_json_value`).

## Requirements

### Requirement 1: Export User-Role Assignments

**User Story:** As a developer using the REDCap API library, I want to export the current user-role assignments from a project, so that I can check which users have roles before modifying them.

#### Acceptance Criteria

1. THE REDCapProject SHALL provide an `export_user_role_assignments` method that accepts no arguments and returns a list of User_Role_Assignment dicts.
2. WHEN `export_user_role_assignments` is called, THE REDCapProject SHALL send a User_Role_Mapping_Payload (with `content` set to `"userRoleMapping"`) to the REDCapConnection `request_json_value` method.
3. WHEN the REDCap API returns a successful response, THE REDCapProject SHALL return the parsed JSON array of User_Role_Assignment objects without modification.
4. WHEN the REDCap API returns a successful response, each User_Role_Assignment in the returned list SHALL contain a `username` key and a `unique_role_name` key.

### Requirement 2: Error Propagation

**User Story:** As a developer using the REDCap API library, I want API errors to propagate as REDCapConnectionError exceptions, so that I can handle failures consistently with other REDCap API methods.

#### Acceptance Criteria

1. IF the REDCap API returns an error response, THEN THE REDCapProject `export_user_role_assignments` method SHALL propagate the REDCapConnectionError raised by REDCapConnection.
2. IF a connection failure occurs during the request, THEN THE REDCapProject `export_user_role_assignments` method SHALL propagate the REDCapConnectionError raised by REDCapConnection.

### Requirement 3: Consistency with Existing API Methods

**User Story:** As a developer maintaining the REDCap API library, I want the new method to follow the same patterns as existing export methods, so that the codebase remains consistent and predictable.

#### Acceptance Criteria

1. THE REDCapProject `export_user_role_assignments` method SHALL follow the same implementation pattern as the `export_user_roles` method, delegating to `REDCapConnection.request_json_value`.
2. THE REDCapProject `export_user_role_assignments` method SHALL include a docstring describing the return value, the method purpose, and the raised exception, consistent with existing method documentation in the class.
3. THE REDCapProject `export_user_role_assignments` method SHALL use the return type annotation `List[Dict[str, Any]]`.
