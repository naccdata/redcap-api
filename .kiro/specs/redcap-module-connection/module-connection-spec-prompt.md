# Spec Prompt: REDCap External Module Connection Base Class

## Goal

Add a general-purpose connection class to the `redcap_api` package that supports communication with REDCap External Modules. This class should serve as a reusable base that downstream consumers can build on to interact with any module (e.g., the Locking API module, or any other module that follows the standard REDCap External Module endpoint pattern).

## Background

The existing `REDCapConnection` class posts to the standard REDCap API endpoint using a fixed URL and `content`-based routing. REDCap External Modules expose their own endpoints using a different query-string pattern:

```
<base_url>/api/?NOAUTH&type=module&prefix=<module_prefix>&page=<action>
```

This package should not contain classes specific to individual modules. Instead, it should provide the building blocks so that consumers of this library can build module-specific clients on top.

## Requirements

1. Create a new class (e.g., `REDCapModuleConnection`) that can construct External Module endpoint URLs from a base REDCap URL, a module prefix, and an action page.

2. The class should reuse the same authentication pattern (API token in POST data) and rate-limiting behavior as `REDCapConnection`.

3. Provide a method for posting arbitrary parameter dictionaries to a module endpoint, returning the raw response or parsed response depending on the requested format.

4. Support the standard External Module URL pattern:
   ```
   POST <base_url>/api/?NOAUTH&type=module&prefix=<module_prefix>&page=<action>
   ```

5. Allow callers to specify:
   - The module prefix (e.g., `locking_api`, or any other module name)
   - The action page (e.g., `status`, `lock`, `unlock`, or any string the module defines)
   - Arbitrary POST parameters as a dictionary
   - Return format preference (JSON, CSV, XML)

6. Follow the existing patterns in the codebase:
   - Use keyword-only arguments for clarity
   - Raise `REDCapConnectionError` on failures
   - Use `@classmethod` factory methods (e.g., `create_from`) for construction
   - Integrate with `REDCapParameterStore` for credential management
   - Return typed values (`List[Dict[str, str]]` for JSON, `str` for CSV/XML)

7. Add unit tests following the existing test structure under `common/src/python/redcap_api/test/python/`.

## Non-Goals

- This package should NOT include module-specific wrapper classes (e.g., no `REDCapLockingAPI`). Consumers of the library are responsible for building those on top of `REDCapModuleConnection`.

## Constraints

- Python 3.12
- Must work within the Pants build system (update BUILD files as needed)
- Adhere to project linting (Ruff) and formatting (YAPF) standards
- Include type annotations; must pass MyPy strict checking

## Reference

REDCap External Modules use this general endpoint pattern:
```
POST <base_url>/api/?NOAUTH&type=module&prefix=<module_prefix>&page=<action>

Standard parameters:
  token (required): API token
  returnFormat (optional): csv, json, or xml (default)
  ...plus any module-specific parameters as POST data
```

Example module: Locking API (https://github.com/lsgs/redcap-locking-api) uses prefix `locking_api` with pages `status`, `lock`, `unlock`.
