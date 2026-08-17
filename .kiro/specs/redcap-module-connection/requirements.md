# Requirements Document

## Introduction

Add a general-purpose connection class (`REDCapModuleConnection`) to the `redcap_api` package that supports communication with REDCap External Modules. This class serves as a reusable base that downstream consumers can build on to interact with any module that follows the standard REDCap External Module endpoint pattern. The package itself will not contain module-specific wrapper classes.

## Glossary

- **REDCapModuleConnection**: A connection class that constructs and posts requests to REDCap External Module endpoints.
- **REDCapConnection**: The existing connection class that posts to the standard REDCap API endpoint using content-based routing.
- **External_Module**: A REDCap plugin that exposes custom endpoints using a query-string URL pattern distinct from the standard API.
- **Module_Prefix**: The identifier string for a specific External Module (e.g., `locking_api`).
- **Action_Page**: The page parameter in the External Module URL that specifies the operation to perform (e.g., `status`, `lock`, `unlock`).
- **Base_URL**: The root URL of the REDCap instance (e.g., `https://redcap.example.com`).
- **REDCapParameters**: A TypedDict containing `url` and `token` fields used for credential management.
- **REDCapConnectionError**: The exception class raised when a connection or request to REDCap fails.

## Requirements

### Requirement 1: Module Endpoint URL Construction

**User Story:** As a library consumer, I want REDCapModuleConnection to construct External Module endpoint URLs from component parts, so that I can interact with any REDCap External Module without manually building URLs.

#### Acceptance Criteria

1. WHEN a REDCapModuleConnection is created with a base URL, module prefix, and action page, THE REDCapModuleConnection SHALL construct the endpoint URL following the pattern `<base_url>/api/?NOAUTH&type=module&prefix=<module_prefix>&page=<action_page>`.
2. WHEN the base URL contains a trailing slash, THE REDCapModuleConnection SHALL produce the same endpoint URL as when the trailing slash is absent.
3. WHEN a request is made with a different action page, THE REDCapModuleConnection SHALL construct a new endpoint URL using the specified action page while retaining the base URL and module prefix.
4. IF the module prefix or action page is empty or contains only whitespace, THEN THE REDCapModuleConnection SHALL raise a REDCapConnectionError indicating which parameter is invalid.
5. THE REDCapModuleConnection SHALL accept module prefix and action page values containing only alphanumeric characters and underscores, with a maximum length of 128 characters each.

### Requirement 2: Authentication and Rate Limiting

**User Story:** As a library consumer, I want REDCapModuleConnection to use the same authentication and rate-limiting patterns as REDCapConnection, so that module requests are authorized and do not exceed REDCap server limits.

#### Acceptance Criteria

1. WHEN a request is posted to a module endpoint, THE REDCapModuleConnection SHALL include the API token as the "token" field in the POST data payload.
2. THE REDCapModuleConnection SHALL enforce rate limiting of no more than 20 calls per 1-second window, consistent with REDCapConnection.
3. WHEN the rate limit is exceeded, THE REDCapModuleConnection SHALL sleep until the current 1-second rate window resets and then retry the request rather than failing immediately.
4. IF the server returns an error response to a module request, THEN THE REDCapModuleConnection SHALL raise a REDCapConnectionError that includes the HTTP status code and response reason without exposing the API token value.

### Requirement 3: Posting Requests to Module Endpoints

**User Story:** As a library consumer, I want to post arbitrary parameter dictionaries to a module endpoint, so that I can invoke any operation a module exposes.

#### Acceptance Criteria

1. WHEN a caller provides a dictionary of POST parameters and a return format of JSON, THE REDCapModuleConnection SHALL automatically include the API token and returnFormat in the POST data, post the combined parameters to the constructed module endpoint, and return the parsed JSON response as a list of dictionaries.
2. WHEN a caller provides a dictionary of POST parameters and a return format of CSV or XML, THE REDCapModuleConnection SHALL automatically include the API token and returnFormat in the POST data, post the combined parameters to the constructed module endpoint, and return the response as a text string.
3. WHEN the HTTP response indicates an error status, THE REDCapModuleConnection SHALL raise a REDCapConnectionError containing the HTTP status code, reason, and response text.
4. WHEN a network connection error or SSL error occurs, THE REDCapModuleConnection SHALL raise a REDCapConnectionError containing the underlying exception message.
5. WHEN the response for a JSON format request contains invalid JSON, THE REDCapModuleConnection SHALL raise a REDCapConnectionError indicating that JSON parsing failed.
6. THE REDCapModuleConnection SHALL enforce rate-limiting of no more than 20 requests per 1-second period, sleeping until the next allowed window before sending a request that would exceed this limit.

### Requirement 4: Factory Construction from Parameters

**User Story:** As a library consumer, I want to create a REDCapModuleConnection from a REDCapParameters object and a module prefix, so that I can integrate with the existing credential management patterns.

#### Acceptance Criteria

1. WHEN a REDCapParameters object and a non-empty module prefix string are provided as keyword-only arguments to the factory method, THE REDCapModuleConnection SHALL create a connection instance configured with the URL and token from the parameters and the specified module prefix.
2. THE REDCapModuleConnection factory method SHALL use the `@classmethod` decorator and be named `create_from`, consistent with existing connection classes.
3. IF the module prefix provided to the factory method is empty or not a string, THEN THE REDCapModuleConnection SHALL raise a ValueError indicating that a non-empty module prefix is required.
4. WHEN the factory method successfully creates a connection instance, THE REDCapModuleConnection SHALL expose the module prefix and URL as readable properties on the returned instance.

### Requirement 5: Keyword-Only Arguments and Type Annotations

**User Story:** As a library consumer, I want REDCapModuleConnection to use keyword-only arguments and full type annotations, so that the API is clear, self-documenting, and passes strict type checking.

#### Acceptance Criteria

1. THE REDCapModuleConnection constructor and factory classmethods SHALL accept all parameters as keyword-only arguments.
2. THE REDCapModuleConnection SHALL include type annotations for all method parameters and return values that pass MyPy strict checking.
3. THE REDCapModuleConnection public methods SHALL use typed return values: `List[Dict[str, Any]]` for JSON responses and `str` for CSV or XML responses.

### Requirement 6: Round-Trip URL Construction Property

**User Story:** As a library maintainer, I want the URL construction to be testable via a round-trip property, so that URL assembly correctness can be verified for arbitrary valid inputs.

#### Acceptance Criteria

1. FOR ALL combinations of a base URL (a string starting with `http://` or `https://` and containing a hostname), a module prefix (a non-empty string containing only lowercase alphanumeric characters and underscores, maximum 64 characters), and an action page (a non-empty string containing only lowercase alphanumeric characters and underscores, maximum 64 characters), THE REDCapModuleConnection SHALL produce a URL that, when parsed, contains the path ending in `/api/` and the query parameters `NOAUTH` (empty), `type=module`, `prefix=<module_prefix>`, and `page=<action_page>` (round-trip property).
2. IF the module prefix or action page contains characters outside the allowed set (lowercase alphanumeric and underscores) or is empty, THEN THE REDCapModuleConnection SHALL raise a REDCapConnectionError indicating the invalid parameter.

### Requirement 7: Build System Integration

**User Story:** As a library maintainer, I want the new module to integrate with the Pants build system, so that it is included in the package distribution and tests can be run via Pants.

#### Acceptance Criteria

1. WHEN the `redcap-api` distribution package is built via Pants, THE build system SHALL include the REDCapModuleConnection source file such that `from redcap_api.redcap_module_connection import REDCapModuleConnection` is importable from the installed package.
2. WHEN tests are run via Pants for the `common/src/python/redcap_api/test/python` target, THE build system SHALL discover and execute all REDCapModuleConnection unit tests that follow the `test_*.py` naming convention.
3. WHEN type checking and linting are run via Pants, THE build system SHALL verify that all REDCapModuleConnection source and test files pass MyPy strict mode and Ruff linting with zero errors.
