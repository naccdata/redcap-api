# Implementation Plan: Export Users

## Overview

Add an `export_users()` method to the `REDCapProject` class and corresponding unit/property tests. The implementation follows the established export method pattern (`export_instruments()`, `export_user_roles()`, `export_user_role_assignments()`): define a data payload with `{"content": "user"}`, delegate to `request_json_value()`, and return the result. All code is Python targeting the existing Pants build system.

## Tasks

- [x] 1. Add `export_users()` method to `REDCapProject`
  - [x] 1.1 Implement the `export_users()` method in `common/src/python/redcap_api/redcap_project.py`
    - Add the method to the `REDCapProject` class following the `export_instruments()` pattern
    - Method signature: `def export_users(self) -> List[Dict[str, Any]]`
    - Define `message = "exporting users"` and `data = {"content": "user"}`
    - Return `self.__redcap_con.request_json_value(data=data, message=message)`
    - Include docstring documenting return value (`username`, `email`, `firstname`, `lastname` keys and privilege flags), and `REDCapConnectionError` on error
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 4.1, 4.2, 4.3_

- [x] 2. Add unit tests for `export_users()`
  - [x] 2.1 Add `TestExportUsers` test class to `common/src/python/redcap_api/test/python/test_redcap_project.py`
    - Follow the exact pattern of the existing `TestExportUserRoleAssignments` test class
    - Reuse the existing `mock_connection` and `project` pytest fixtures
    - Add `test_sends_correct_payload`: verify `request_json_value` is called with `data={"content": "user"}` and `message="exporting users"`
    - Add `test_returns_parsed_response`: mock returns a list of user dicts (with `username`, `email`, `firstname`, `lastname`, and privilege flags), verify the method returns them as-is
    - Add `test_returns_empty_list`: mock returns `[]`, verify the method returns `[]`
    - Add `test_propagates_api_error`: mock raises `REDCapConnectionError` with HTTP 403 message, verify it propagates
    - Add `test_propagates_connection_error`: mock raises `REDCapConnectionError` with connection failure message, verify it propagates
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x]* 2.2 Write property test for pass-through invariant
    - **Property 1: Pass-through invariant**
    - **Validates: Requirements 1.3, 2.1, 2.2, 2.3**
    - Use Hypothesis `@given` to generate random lists of dictionaries with string keys and mixed-type values
    - Mock `request_json_value` to return the generated list
    - Assert `export_users()` returns the identical object
    - Place in `TestExportUsers` class or a dedicated `TestExportUsersProperties` class in the same file

- [x] 3. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- The design uses Python, so all code targets Python 3.12 with the Pants build system
- Property tests use Hypothesis as the PBT library
- The implementation is a single thin pass-through method; the bulk of the work is in testing
