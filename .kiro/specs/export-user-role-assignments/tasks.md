# Implementation Plan: Export User-Role Assignments

## Overview

Add `export_user_role_assignments()` to `REDCapProject`, following the existing delegation pattern. Set up the first test infrastructure for the `redcap_api` package with both unit and property-based tests.

## Tasks

- [x] 1. Add `export_user_role_assignments` method to `REDCapProject`
  - [x] 1.1 Add the `export_user_role_assignments` method to `REDCapProject` in `common/src/python/redcap_api/redcap_project.py`
    - Place the method after `export_user_roles()` and before `assign_user_role()`
    - Build the data dict with `{"content": "userRoleMapping"}`
    - Delegate to `self.__redcap_con.request_json_value(data=data, message=message)`
    - Return type annotation: `List[Dict[str, Any]]`
    - Include docstring describing return value, purpose, and raised exception
    - _Requirements: 1.1, 1.2, 1.3, 3.1, 3.2, 3.3_

- [x] 2. Set up test infrastructure for `redcap_api`
  - [x] 2.1 Create the test directory and Pants BUILD file at `common/src/python/redcap_api/test/python/BUILD`
    - Define a `python_tests` target
    - Add dependencies on `common/src/python/redcap_api:redcap_api`
    - Reference existing test BUILD patterns from `tools/redcap_error_checks_import/test/python/BUILD`
    - _Requirements: 3.1_

- [x] 3. Checkpoint - Verify method and build setup
  - Ensure the new method passes type checking and linting, ask the user if questions arise.

- [x] 4. Write tests for `export_user_role_assignments`
  - [x] 4.1 Create `common/src/python/redcap_api/test/python/test_redcap_project.py` with unit tests
    - Test correct payload: mock `REDCapConnection`, call `export_user_role_assignments()`, assert `request_json_value` was called with `data={"content": "userRoleMapping"}` and `message="exporting user-role assignments"`
    - Test error propagation: mock `request_json_value` to raise `REDCapConnectionError`, assert it propagates unchanged
    - Test empty list: mock `request_json_value` to return `[]`, assert method returns `[]`
    - _Requirements: 1.2, 1.3, 2.1, 2.2_

  - [ ]* 4.2 Write property test for pass-through identity
    - **Property 1: Pass-through identity**
    - Use Hypothesis `@given` to generate random lists of `{"username": ..., "unique_role_name": ...}` dicts
    - Mock `request_json_value` to return the generated list
    - Assert `export_user_role_assignments()` returns the identical object
    - **Validates: Requirements 1.3, 1.4**

- [x] 5. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- The design uses Python, so all code examples target Python 3.12 with Pants build system
- Property tests use Hypothesis as the PBT library
- This creates the first test infrastructure for the core `redcap_api` package
