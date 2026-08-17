"""Classes and methods for connecting to REDCap External Module endpoints."""

from __future__ import annotations

import re
from json import JSONDecodeError
from typing import Any, Dict, List, Literal
from urllib.parse import urlencode

import requests  # type: ignore
from ratelimit import limits, sleep_and_retry

from redcap_api.redcap_connection import REDCapConnectionError, error_message
from redcap_api.redcap_parameter_store import REDCapParameters

# Pattern for valid module identifiers: lowercase alphanumeric + underscores, 1-64 chars
_IDENTIFIER_PATTERN = re.compile(r"^[a-z0-9_]{1,64}$")


class REDCapModuleConnection:
    """Connection class for posting requests to REDCap External Module
    endpoints."""

    def __init__(self, *, token: str, url: str, module_prefix: str) -> None:
        """Initialize a module connection.

        Args:
            token: API token for the REDCap project.
            url: Base URL of the REDCap instance (e.g., "https://redcap.example.com").
            module_prefix: The module prefix identifier (e.g., "locking_api").

        Raises:
            REDCapConnectionError: If module_prefix is invalid.
        """
        self._validate_identifier(module_prefix, "module_prefix")
        self.__token = token
        self.__url = url
        self.__module_prefix = module_prefix

    @property
    def url(self) -> str:
        """The base REDCap URL."""
        return self.__url

    @property
    def module_prefix(self) -> str:
        """The module prefix for this connection."""
        return self.__module_prefix

    @classmethod
    def create_from(
        cls, *, parameters: REDCapParameters, module_prefix: str
    ) -> REDCapModuleConnection:
        """Create a module connection from REDCap parameters.

        Args:
            parameters: REDCapParameters with url and token.
            module_prefix: Non-empty module prefix string.

        Returns:
            Configured REDCapModuleConnection instance.

        Raises:
            REDCapConnectionError: If module_prefix is invalid.
        """
        return cls(
            token=parameters["token"],
            url=parameters["url"],
            module_prefix=module_prefix,
        )

    @sleep_and_retry
    @limits(calls=20, period=1)
    def post_module_request(
        self,
        *,
        action_page: str,
        data: Dict[str, str],
        return_format: Literal["json", "csv", "xml"] = "json",
    ) -> List[Dict[str, Any]] | str:
        """Post a request to a module endpoint.

        Args:
            action_page: The action page for the module endpoint.
            data: Dictionary of POST parameters to send.
            return_format: One of "json", "csv", or "xml".

        Returns:
            Parsed JSON as List[Dict[str, Any]] if return_format is "json",
            otherwise the response text as str.

        Raises:
            REDCapConnectionError: On invalid action_page, HTTP errors,
                network errors, or JSON parse failures.
        """
        self._validate_identifier(action_page, "action_page")
        endpoint_url = self._build_endpoint_url(action_page)

        payload: Dict[str, str] = {
            "token": self.__token,
            "returnFormat": return_format,
            **data,
        }

        try:
            response = requests.post(endpoint_url, data=payload)
        except (
            requests.exceptions.SSLError,
            requests.exceptions.ConnectionError,
        ) as error:
            raise REDCapConnectionError(
                message=f"Error connecting to {endpoint_url} - {error}"
            ) from error

        if not response.ok:
            raise REDCapConnectionError(
                message=error_message(
                    message="posting module request", response=response
                )
            )

        if return_format == "json":
            try:
                return response.json()
            except JSONDecodeError as error:
                raise REDCapConnectionError(
                    message="Error: JSON parsing failed for module response"
                ) from error

        return response.text

    def _build_endpoint_url(self, action_page: str) -> str:
        """Construct the full module endpoint URL.

        Combines base URL, module prefix, and action page into the standard
        External Module URL pattern.

        Args:
            action_page: The action page for the module endpoint.

        Returns:
            The full endpoint URL string.
        """
        base = self.__url.rstrip("/")
        params = urlencode(
            {
                "NOAUTH": "",
                "type": "module",
                "prefix": self.__module_prefix,
                "page": action_page,
            }
        )
        return f"{base}/api/?{params}"

    @staticmethod
    def _validate_identifier(value: str, name: str) -> None:
        """Validate that a string is a valid module identifier.

        Valid identifiers contain only lowercase alphanumeric characters and
        underscores, are non-empty, and are at most 64 characters long.

        Args:
            value: The string to validate.
            name: The parameter name (for error messages).

        Raises:
            REDCapConnectionError: If validation fails.
        """
        if not _IDENTIFIER_PATTERN.match(value):
            raise REDCapConnectionError(
                message=(
                    f"Invalid {name}: must contain only lowercase alphanumeric "
                    "characters and underscores, 1-64 characters long"
                )
            )
