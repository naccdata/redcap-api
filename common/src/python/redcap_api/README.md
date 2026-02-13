# redcap-api

A Python library for interacting with the REDCap API.

## Overview

This library provides a clean, typed interface for working with REDCap projects through the REDCap API. It includes support for:

- Project management and metadata
- Record import/export
- Report generation
- User and role management
- Rate limiting and error handling
- Type-safe parameter handling

## Installation

```bash
pip install redcap-api
```

## Requirements

- Python >= 3.12
- requests
- ratelimit

## Quick Start

### Basic Connection

```python
from redcap_api.redcap_connection import REDCapConnection
from redcap_api.redcap_project import REDCapProject

# Create a connection
connection = REDCapConnection(
    token="your-api-token",
    url="https://redcap.example.com/api/"
)

# Get project information
project = REDCapProject.create(connection)
print(f"Project: {project.title} (PID: {project.pid})")
```

### Using Parameter Store

```python
from redcap_api.redcap_parameter_store import REDCapParameters
from redcap_api.redcap_connection import REDCapConnection

# Define parameters
params: REDCapParameters = {
    "url": "https://redcap.example.com/api/",
    "token": "your-api-token"
}

# Create connection from parameters
connection = REDCapConnection.create_from(params)
```

### Export Records

```python
# Export all records
records = project.export_records()

# Export specific records
records = project.export_records(
    record_ids=["001", "002"],
    fields=["record_id", "age", "gender"]
)

# Export with filters
records = project.export_records(
    filters="[age] > 30"
)
```

### Import Records

```python
import json

records = [
    {"record_id": "001", "age": "35", "gender": "1"},
    {"record_id": "002", "age": "42", "gender": "2"}
]

count = project.import_records(json.dumps(records))
print(f"Imported {count} records")
```

### Working with Reports

```python
from redcap_api.redcap_connection import REDCapReportConnection

# Connect to a specific report
report_conn = REDCapReportConnection(
    token="your-api-token",
    url="https://redcap.example.com/api/",
    report_id="12345"
)

# Get report data
records = report_conn.get_report_records()
```

## Main Components

### REDCapConnection

Manages API requests to a REDCap project with built-in rate limiting (20 calls per second).

### REDCapProject

Represents a REDCap project with methods for:
- Exporting/importing records
- Managing instruments and events
- User and role management
- Project metadata

### REDCapSuperUserConnection

Special connection type for administrative tasks like creating new projects (requires super API token).

### REDCapParametersRepository

Repository pattern for managing multiple REDCap project credentials.

## Error Handling

The library raises `REDCapConnectionError` for API-related errors:

```python
from redcap_api.redcap_connection import REDCapConnectionError

try:
    records = project.export_records()
except REDCapConnectionError as e:
    print(f"API Error: {e.message}")
```

## Type Safety

The library includes type hints and a `py.typed` marker for full type checking support with mypy and other type checkers.

## License

This project is licensed under the Mozilla Public License 2.0 (MPL-2.0).

## Author

NACC (nacchelp@uw.edu)

## Repository

https://github.com/naccdata/redcap-api
