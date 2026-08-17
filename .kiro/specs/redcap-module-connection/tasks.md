# Implementation Plan: REDCap Module Connection

## Overview

Implement `REDCapModuleConnection`, a new connection class in the `redcap_api` package for communicating with REDCap External Module endpoints. The implementation uses composition (not inheritance), follows the same authentication and rate-limiting patterns as `REDCapConnection`, and includes comprehensive property-based and unit tests.

## Tasks

- [x] 1. Create REDCapModuleConnection core module
  - [x] 1.1 Create `redcap_module_connection.py` with class skeleton, imports, and validation helpers
    - Create `common/src/python/redcap_api/redcap_module_connection.py`
    - Add imports: `json`, `re`, `typing`, `requests`, `ratelimit`, and `REDCapParameters`/`REDCapConnectionError` from existing modules
    - Implement `_validate_identifier` static method with `^[a-z0-9_]{1,64}$` regex check raising `REDCapConnectionError`
    - Implement `__init__` with keyword-only args (`token`, `url`, `module_prefix`), calling `_validate_identifier` on prefix
    - Add `url` and `module_prefix` read-only properties
    - _Requirements: 1.4, 1.5, 5.1, 5.2, 6.2_

  - [x] 1.2 Implement `_build_endpoint_url` and `create_from` factory method
    - Implement `_build_endpoint_url(action_page)` with trailing-slash normalization and query-string pattern
    - Implement `create_from` classmethod accepting `parameters: REDCapParameters` and `module_prefix: str` as keyword-only args
    - Factory raises `ValueError` for empty or non-string prefix
    - _Requirements: 1.1, 1.2, 1.3, 4.1, 4.2, 4.3, 4.4_

  - [x] 1.3 Implement `post_module_request` method
    - Add `@sleep_and_retry` and `@limits(calls=20, period=1)` decorators
    - Accept keyword-only args: `action_page: str`, `data: Dict[str, str]`, `return_format: str = "json"`
    - Validate `action_page` via `_validate_identifier`
    - Build endpoint URL, assemble payload with token and returnFormat
    - POST via `requests.post`, handle `ConnectionError`/`SSLError`
    - Parse JSON response or return text based on `return_format`
    - Raise `REDCapConnectionError` on HTTP errors (without exposing token) and JSON parse failures
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [x] 1.4 Update `__init__.py` to export `REDCapModuleConnection`
    - Add import of `REDCapModuleConnection` from `redcap_api.redcap_module_connection` to `common/src/python/redcap_api/__init__.py`
    - _Requirements: 7.1_

- [x] 2. Checkpoint - Verify module structure
  - Ensure all tests pass, ask the user if questions arise.

- [x] 3. Write unit tests for REDCapModuleConnection
  - [x] 3.1 Create test file with constructor and factory unit tests
    - Create `common/src/python/redcap_api/test/python/test_redcap_module_connection.py`
    - Test valid construction with keyword-only args
    - Test invalid prefix raises `REDCapConnectionError`
    - Test `create_from` with valid params produces correct properties
    - Test `create_from` with empty prefix raises `ValueError`
    - Test `create_from` with non-string prefix raises `ValueError`
    - Test positional args raise `TypeError`
    - _Requirements: 1.4, 4.1, 4.3, 4.4, 5.1_

  - [x] 3.2 Write unit tests for URL construction and request posting
    - Test URL pattern matches `<base_url>/api/?NOAUTH&type=module&prefix=<prefix>&page=<page>`
    - Test trailing-slash normalization produces same URL
    - Test different action pages produce correct URLs
    - Test successful JSON response returns parsed list of dicts
    - Test successful CSV/XML response returns text string
    - Test HTTP error raises `REDCapConnectionError` with status code and reason
    - Test network/SSL error raises `REDCapConnectionError`
    - Test invalid JSON response raises `REDCapConnectionError`
    - Test rate-limit decorator is present on `post_module_request`
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.4, 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4. Write property-based tests for correctness properties
  - [x] 4.1 Write property test for URL Round-Trip Construction (Property 1)
    - **Property 1: URL Round-Trip Construction**
    - Generate valid base URLs, module prefixes, and action pages; verify parsed URL components match expected pattern
    - **Validates: Requirements 1.1, 1.2, 6.1**

  - [x] 4.2 Write property test for Identifier Validation Boundary (Property 2)
    - **Property 2: Identifier Validation Boundary**
    - Generate valid identifiers matching `^[a-z0-9_]{1,64}$` and invalid strings; verify acceptance/rejection
    - **Validates: Requirements 1.4, 1.5, 6.2**

  - [x] 4.3 Write property test for Token Inclusion Invariant (Property 3)
    - **Property 3: Token Inclusion Invariant**
    - Generate random data dicts and action pages; mock POST and verify payload always contains token and returnFormat
    - **Validates: Requirements 2.1, 3.1, 3.2**

  - [x] 4.4 Write property test for Error Message Security (Property 4)
    - **Property 4: Error Message Security**
    - Generate random tokens and error responses; verify token value never appears in exception message
    - **Validates: Requirements 2.4, 3.3**

  - [x] 4.5 Write property test for JSON Response Pass-Through (Property 5)
    - **Property 5: JSON Response Pass-Through**
    - Generate random list-of-dicts; mock successful JSON response; verify returned value is identical
    - **Validates: Requirements 3.1**

  - [x] 4.6 Write property test for Text Response Pass-Through (Property 6)
    - **Property 6: Text Response Pass-Through**
    - Generate random text; mock successful response with csv/xml format; verify returned text is identical
    - **Validates: Requirements 3.2**

  - [x] 4.7 Write property test for Invalid JSON Detection (Property 7)
    - **Property 7: Invalid JSON Detection**
    - Generate non-JSON strings; mock response body; verify `REDCapConnectionError` is raised
    - **Validates: Requirements 3.5**

  - [x] 4.8 Write property test for Factory Construction Round-Trip (Property 8)
    - **Property 8: Factory Construction Round-Trip**
    - Generate valid `REDCapParameters` and prefix; call `create_from`; verify properties match inputs
    - **Validates: Requirements 4.1, 4.4**

- [x] 5. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties using Hypothesis with `max_examples=100`
- Unit tests validate specific scenarios and edge cases using pytest
- The existing `python_sources(name="redcap_api")` BUILD target auto-discovers new `.py` files
- The existing `python_tests(name="tests")` BUILD target auto-discovers new `test_*.py` files
- No BUILD file modifications are required

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2"] },
    { "id": 2, "tasks": ["1.3"] },
    { "id": 3, "tasks": ["1.4"] },
    { "id": 4, "tasks": ["3.1", "3.2"] },
    { "id": 5, "tasks": ["4.1", "4.2", "4.3", "4.4", "4.5", "4.6", "4.7", "4.8"] }
  ]
}
```
