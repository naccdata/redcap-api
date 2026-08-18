"""Tests for REDCapModuleConnection."""

import json
import re
from json import JSONDecodeError
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlparse

import pytest
import requests  # type: ignore[import-untyped]
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from redcap_api.redcap_connection import REDCapConnectionError
from redcap_api.redcap_module_connection import REDCapModuleConnection

# --- Fixtures ---


@pytest.fixture()
def connection():
    """Create a REDCapModuleConnection for testing."""
    return REDCapModuleConnection(
        token="ABCDEF123456",
        url="https://redcap.example.com/api/",
        module_prefix="locking_api",
    )


# --- Unit tests for constructor and factory (Task 3.1) ---


class TestREDCapModuleConnectionConstructor:
    """Tests for constructor and property behavior."""

    def test_valid_construction(self):
        """Test construction with valid keyword-only args."""
        conn = REDCapModuleConnection(
            token="test_token",
            url="https://redcap.example.com/api/",
            module_prefix="my_module",
        )
        assert conn.url == "https://redcap.example.com/api/"
        assert conn.module_prefix == "my_module"

    def test_invalid_prefix_raises_error(self):
        """Test that invalid module_prefix raises REDCapConnectionError."""
        with pytest.raises(REDCapConnectionError):
            REDCapModuleConnection(
                token="test_token",
                url="https://redcap.example.com/api/",
                module_prefix="Invalid-Prefix!",
            )

    def test_empty_prefix_raises_error(self):
        """Test that empty module_prefix raises REDCapConnectionError."""
        with pytest.raises(REDCapConnectionError):
            REDCapModuleConnection(
                token="test_token",
                url="https://redcap.example.com/api/",
                module_prefix="",
            )

    def test_positional_args_raise_type_error(self):
        """Test that positional arguments raise TypeError."""
        with pytest.raises(TypeError):
            REDCapModuleConnection(  # type: ignore[misc]
                "test_token", "https://redcap.example.com/api/", "my_module"
            )


class TestREDCapModuleConnectionFactory:
    """Tests for the create_from factory classmethod."""

    def test_valid_params_produces_correct_properties(self):
        """Test create_from with valid params produces correct properties."""
        params = {"url": "https://redcap.example.com/api/", "token": "my_token"}
        conn = REDCapModuleConnection.create_from(
            parameters=params, module_prefix="locking_api"
        )
        assert conn.url == "https://redcap.example.com/api/"
        assert conn.module_prefix == "locking_api"

    def test_empty_prefix_raises_connection_error(self):
        """Test create_from with empty prefix raises REDCapConnectionError."""
        params = {"url": "https://redcap.example.com/api/", "token": "my_token"}
        with pytest.raises(REDCapConnectionError):
            REDCapModuleConnection.create_from(parameters=params, module_prefix="")

    def test_invalid_prefix_raises_connection_error(self):
        """Test create_from with invalid prefix raises
        REDCapConnectionError."""
        params = {"url": "https://redcap.example.com/api/", "token": "my_token"}
        with pytest.raises(REDCapConnectionError):
            REDCapModuleConnection.create_from(
                parameters=params,
                module_prefix="Invalid-Prefix!",
            )


# --- Unit tests for URL construction (Task 3.2) ---


class TestREDCapModuleConnectionURL:
    """Tests for URL construction."""

    @patch("redcap_api.redcap_module_connection.requests.post")
    def test_url_pattern_matches_expected_format(self, mock_post, connection):
        """Test URL pattern matches the External Module endpoint format."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = []
        mock_post.return_value = mock_response

        connection.post_module_request(action_page="status", data={})

        actual_url = mock_post.call_args[0][0]
        parsed = urlparse(actual_url)
        query_params = parse_qs(parsed.query)

        assert parsed.scheme == "https"
        assert parsed.netloc == "redcap.example.com"
        assert parsed.path == "/api/"
        assert "NOAUTH" in parsed.query
        assert query_params["type"] == ["module"]
        assert query_params["prefix"] == ["locking_api"]
        assert query_params["page"] == ["status"]

    @patch("redcap_api.redcap_module_connection.requests.post")
    def test_trailing_slash_normalization(self, mock_post):
        """Test that trailing slash on base URL produces same endpoint."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = []
        mock_post.return_value = mock_response

        conn_with_slash = REDCapModuleConnection(
            token="token",
            url="https://redcap.example.com/api/",
            module_prefix="locking_api",
        )
        conn_without_slash = REDCapModuleConnection(
            token="token",
            url="https://redcap.example.com/api",
            module_prefix="locking_api",
        )

        conn_with_slash.post_module_request(action_page="lock", data={})
        url_with = mock_post.call_args[0][0]

        mock_post.reset_mock()
        mock_post.return_value = mock_response

        conn_without_slash.post_module_request(action_page="lock", data={})
        url_without = mock_post.call_args[0][0]

        assert url_with == url_without

    @patch("redcap_api.redcap_module_connection.requests.post")
    def test_different_action_pages_produce_correct_urls(self, mock_post, connection):
        """Test different action pages produce correct URLs."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = []
        mock_post.return_value = mock_response

        connection.post_module_request(action_page="status", data={})
        url_status = mock_post.call_args[0][0]

        connection.post_module_request(action_page="lock", data={})
        url_lock = mock_post.call_args[0][0]

        connection.post_module_request(action_page="unlock", data={})
        url_unlock = mock_post.call_args[0][0]

        assert "page=status" in url_status
        assert "page=lock" in url_lock
        assert "page=unlock" in url_unlock
        # All share the same prefix
        assert "prefix=locking_api" in url_status
        assert "prefix=locking_api" in url_lock
        assert "prefix=locking_api" in url_unlock


# --- Unit tests for post_module_request (Task 3.2) ---


class TestREDCapModuleConnectionPostRequest:
    """Tests for post_module_request method."""

    @patch("redcap_api.redcap_module_connection.requests.post")
    def test_successful_json_response(self, mock_post, connection):
        """Test successful JSON response returns parsed list of dicts."""
        expected = [{"record": "1", "status": "locked"}]
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = expected
        mock_post.return_value = mock_response

        result = connection.post_module_request(
            action_page="status",
            data={"record": "1"},
            return_format="json",
        )

        assert result == expected
        mock_post.assert_called_once()

    @patch("redcap_api.redcap_module_connection.requests.post")
    def test_successful_csv_response(self, mock_post, connection):
        """Test successful CSV response returns text string."""
        csv_text = "record,status\n1,locked\n2,unlocked"
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.text = csv_text
        mock_post.return_value = mock_response

        result = connection.post_module_request(
            action_page="status",
            data={"record": "1"},
            return_format="csv",
        )

        assert result == csv_text

    @patch("redcap_api.redcap_module_connection.requests.post")
    def test_successful_xml_response(self, mock_post, connection):
        """Test successful XML response returns text string."""
        xml_text = "<records><record><id>1</id></record></records>"
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.text = xml_text
        mock_post.return_value = mock_response

        result = connection.post_module_request(
            action_page="status",
            data={},
            return_format="xml",
        )

        assert result == xml_text

    @patch("redcap_api.redcap_module_connection.requests.post")
    def test_http_error_raises_connection_error(self, mock_post, connection):
        """Test HTTP error raises REDCapConnectionError with status and
        reason."""
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 403
        mock_response.reason = "Forbidden"
        mock_response.text = "no permission"
        mock_post.return_value = mock_response

        with pytest.raises(REDCapConnectionError) as exc_info:
            connection.post_module_request(
                action_page="lock",
                data={"record": "1"},
            )

        assert "403" in exc_info.value.message
        assert "Forbidden" in exc_info.value.message

    @patch("redcap_api.redcap_module_connection.requests.post")
    def test_network_error_raises_connection_error(self, mock_post, connection):
        """Test network connection error raises REDCapConnectionError."""
        mock_post.side_effect = requests.exceptions.ConnectionError(
            "Connection refused"
        )

        with pytest.raises(REDCapConnectionError) as exc_info:
            connection.post_module_request(
                action_page="status",
                data={},
            )

        assert "Connection refused" in exc_info.value.message

    @patch("redcap_api.redcap_module_connection.requests.post")
    def test_ssl_error_raises_connection_error(self, mock_post, connection):
        """Test SSL error raises REDCapConnectionError."""
        mock_post.side_effect = requests.exceptions.SSLError(
            "SSL certificate verify failed"
        )

        with pytest.raises(REDCapConnectionError) as exc_info:
            connection.post_module_request(
                action_page="status",
                data={},
            )

        assert "SSL" in exc_info.value.message

    @patch("redcap_api.redcap_module_connection.requests.post")
    def test_invalid_json_raises_connection_error(self, mock_post, connection):
        """Test invalid JSON response raises REDCapConnectionError."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.side_effect = JSONDecodeError(
            "Expecting value", "not json", 0
        )
        mock_post.return_value = mock_response

        with pytest.raises(REDCapConnectionError) as exc_info:
            connection.post_module_request(
                action_page="status",
                data={},
                return_format="json",
            )

        assert "JSON parsing failed" in exc_info.value.message

    def test_rate_limit_decorator_present(self):
        """Test that rate-limit decorator is present on post_module_request."""
        # The @sleep_and_retry and @limits decorators wrap the method,
        # so the original function is accessible via __wrapped__
        assert hasattr(REDCapModuleConnection.post_module_request, "__wrapped__")

    @patch("redcap_api.redcap_module_connection.requests.post")
    def test_token_included_in_payload(self, mock_post, connection):
        """Test that the API token is included in the POST payload."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = []
        mock_post.return_value = mock_response

        connection.post_module_request(
            action_page="status",
            data={"record": "1"},
        )

        call_kwargs = mock_post.call_args
        if "data" in call_kwargs[1]:
            payload = call_kwargs[1]["data"]
        else:
            payload = call_kwargs[0][1]
        assert payload["token"] == "ABCDEF123456"
        assert payload["returnFormat"] == "json"

    @patch("redcap_api.redcap_module_connection.requests.post")
    def test_posts_to_correct_url(self, mock_post, connection):
        """Test that requests.post is called with the correct endpoint URL."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = []
        mock_post.return_value = mock_response

        connection.post_module_request(
            action_page="status",
            data={},
        )

        call_args = mock_post.call_args
        actual_url = call_args[0][0] if call_args[0] else call_args[1].get("url", "")
        parsed = urlparse(actual_url)
        query_params = parse_qs(parsed.query)

        assert parsed.path == "/api/"
        assert "NOAUTH" in parsed.query
        assert query_params["type"] == ["module"]
        assert query_params["prefix"] == ["locking_api"]
        assert query_params["page"] == ["status"]

    @patch("redcap_api.redcap_module_connection.requests.post")
    def test_http_error_does_not_expose_token(self, mock_post):
        """Test that HTTP error message does not contain the API token."""
        token = "SECRET_TOKEN_VALUE_12345"
        conn = REDCapModuleConnection(
            token=token,
            url="https://redcap.example.com/api/",
            module_prefix="locking_api",
        )
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 403
        mock_response.reason = "Forbidden"
        mock_response.text = "no permission"
        mock_post.return_value = mock_response

        with pytest.raises(REDCapConnectionError) as exc_info:
            conn.post_module_request(
                action_page="lock",
                data={},
            )

        assert token not in exc_info.value.message

    def test_invalid_action_page_raises_error(self, connection):
        """Test that invalid action_page raises REDCapConnectionError."""
        with pytest.raises(REDCapConnectionError):
            connection.post_module_request(
                action_page="Invalid-Page!",
                data={},
            )


# --- Property-based tests for URL Round-Trip Construction (Task 4.1) ---


class TestURLRoundTripProperty:
    """Property-based tests for URL round-trip construction.

    Feature: redcap-module-connection, Property 1: URL Round-Trip Construction
    """

    @given(
        base_url=st.from_regex(r"https?://[a-z]+\.[a-z]+/api", fullmatch=True),
        prefix=st.from_regex(r"[a-z0-9_]{1,64}", fullmatch=True),
        action_page=st.from_regex(r"[a-z0-9_]{1,64}", fullmatch=True),
    )
    @settings(max_examples=100, deadline=None)
    def test_url_components_match_expected_pattern(self, base_url, prefix, action_page):
        """**Validates: Requirements 1.1, 1.2, 6.1**

        For any valid base URL (ending in /api), module prefix, and action
        page, the constructed endpoint URL SHALL have a path ending in /api/
        and query parameters containing NOAUTH, type=module, prefix=<prefix>,
        and page=<action_page>.
        """
        conn = REDCapModuleConnection(
            token="test_token",
            url=base_url,
            module_prefix=prefix,
        )

        with patch("redcap_api.redcap_module_connection.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.ok = True
            mock_response.json.return_value = []
            mock_post.return_value = mock_response

            conn.post_module_request(action_page=action_page, data={})

            endpoint_url = mock_post.call_args[0][0]

        parsed = urlparse(endpoint_url)
        query_params = parse_qs(parsed.query)

        # Path ends in /api/
        assert parsed.path.endswith("/api/")

        # Query parameters contain expected values
        assert "NOAUTH" in parsed.query
        assert query_params["type"] == ["module"]
        assert query_params["prefix"] == [prefix]
        assert query_params["page"] == [action_page]

    @given(
        base_url=st.from_regex(r"https?://[a-z]+\.[a-z]+/api", fullmatch=True),
        prefix=st.from_regex(r"[a-z0-9_]{1,64}", fullmatch=True),
        action_page=st.from_regex(r"[a-z0-9_]{1,64}", fullmatch=True),
    )
    @settings(max_examples=100, deadline=None)
    def test_trailing_slash_invariance(self, base_url, prefix, action_page):
        """**Validates: Requirements 1.2, 6.1**

        A base URL with a trailing slash SHALL produce the same endpoint
        URL as one without a trailing slash.
        """
        conn_without_slash = REDCapModuleConnection(
            token="test_token",
            url=base_url,
            module_prefix=prefix,
        )
        conn_with_slash = REDCapModuleConnection(
            token="test_token",
            url=base_url + "/",
            module_prefix=prefix,
        )

        with patch("redcap_api.redcap_module_connection.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.ok = True
            mock_response.json.return_value = []
            mock_post.return_value = mock_response

            conn_without_slash.post_module_request(action_page=action_page, data={})
            url_without = mock_post.call_args[0][0]

            mock_post.reset_mock()
            mock_post.return_value = mock_response

            conn_with_slash.post_module_request(action_page=action_page, data={})
            url_with = mock_post.call_args[0][0]

        assert url_without == url_with


# --- Property-based tests (Task 4.3) ---

# Strategy for valid identifier strings
# (lowercase alphanumeric + underscores, 1-64 chars)
valid_identifiers = st.from_regex(r"[a-z0-9_]{1,64}", fullmatch=True)

# Strategy for safe characters (excludes surrogates for well-formed strings)
_safe_characters = st.characters(
    blacklist_categories=("Cs",)  # type: ignore[arg-type]
)

# Strategy for data dict keys that won't collide with token/returnFormat
safe_dict_keys = st.text(
    alphabet=_safe_characters,
    min_size=1,
    max_size=20,
).filter(lambda k: k not in ("token", "returnFormat"))

# Strategy for data dictionaries with safe keys
safe_data_dicts = st.dictionaries(
    keys=safe_dict_keys,
    values=st.text(alphabet=_safe_characters, max_size=50),
    max_size=5,
)

# Strategy for return format
return_formats = st.sampled_from(["json", "csv", "xml"])


class TestTokenInclusionInvariantProperty:
    """Property-based tests for token inclusion invariant.

    Feature: redcap-module-connection, Property 3: Token Inclusion Invariant
    """

    @given(
        action_page=valid_identifiers,
        data=safe_data_dicts,
        return_format=return_formats,
    )
    @settings(
        max_examples=100,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @patch("redcap_api.redcap_module_connection.requests.post")
    def test_payload_always_contains_token_and_return_format(
        self, mock_post, action_page, data, return_format
    ):
        """**Validates: Requirements 2.1, 3.1, 3.2**

        For any valid action page and any dictionary of POST parameters,
        when post_module_request is called, the data sent to the server
        always contains the token field set to the connection's configured
        API token and the returnFormat field set to the requested format.
        """
        token = "TEST_TOKEN_ABC123"
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = []
        mock_response.text = ""
        mock_post.return_value = mock_response

        conn = REDCapModuleConnection(
            token=token,
            url="https://redcap.example.com/api/",
            module_prefix="test_module",
        )

        conn.post_module_request(
            action_page=action_page,
            data=data,
            return_format=return_format,
        )

        # Extract the payload from the mock call
        call_kwargs = mock_post.call_args
        payload = (
            call_kwargs[1]["data"] if "data" in call_kwargs[1] else call_kwargs[0][1]
        )

        # Token must always be present and match the configured value
        assert "token" in payload
        assert payload["token"] == token

        # returnFormat must always be present and match the requested format
        assert "returnFormat" in payload
        assert payload["returnFormat"] == return_format

        # All caller-provided data keys must also be present
        for key, value in data.items():
            assert key in payload
            assert payload[key] == value


# --- Property-based tests for JSON Response Pass-Through (Task 4.5) ---


class TestJSONResponsePassThroughProperty:
    """Property-based tests for JSON response pass-through.

    Feature: redcap-module-connection, Property 5: JSON Response Pass-Through
    """

    @given(
        json_data=st.lists(
            st.dictionaries(
                keys=st.text(
                    min_size=1,
                    max_size=20,
                    alphabet=_safe_characters,
                ),
                values=st.one_of(
                    st.text(
                        max_size=50,
                        alphabet=_safe_characters,
                    ),
                    st.integers(),
                    st.booleans(),
                    st.none(),
                ),
                min_size=0,
                max_size=5,
            ),
            min_size=0,
            max_size=10,
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_json_response_returned_without_modification(self, json_data):
        """**Validates: Requirements 3.1**

        For any list of dictionaries returned as a valid JSON HTTP response
        body, when post_module_request is called with return_format="json",
        the method SHALL return the exact same list without modification.
        """
        conn = REDCapModuleConnection(
            token="test_token",
            url="https://redcap.example.com/api/",
            module_prefix="test_module",
        )

        with patch("redcap_api.redcap_module_connection.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.ok = True
            mock_response.json.return_value = json_data
            mock_post.return_value = mock_response

            result = conn.post_module_request(
                action_page="test_action",
                data={},
                return_format="json",
            )

        assert result == json_data


# --- Property-based tests for Error Message Security (Task 4.4) ---


class TestErrorMessageSecurityProperty:
    """Property-based tests for error message security.

    Feature: redcap-module-connection, Property 4: Error Message Security
    """

    @given(
        token=st.text(
            alphabet=_safe_characters,
            min_size=8,
            max_size=64,
        ),
        status_code=st.integers(min_value=400, max_value=599),
        reason=st.text(
            alphabet=_safe_characters,
            min_size=1,
            max_size=50,
        ),
        response_text=st.text(
            alphabet=_safe_characters,
            max_size=200,
        ),
    )
    @settings(max_examples=100, deadline=None)
    @patch("redcap_api.redcap_module_connection.requests.post")
    def test_token_never_appears_in_error_message(
        self, mock_post, token, status_code, reason, response_text
    ):
        """**Validates: Requirements 2.4, 3.3**

        For any HTTP error response (status code, reason, response text)
        and any API token value, the raised REDCapConnectionError message
        SHALL contain the HTTP status code and reason but SHALL NOT contain
        the API token string.
        """
        from hypothesis import assume

        # Skip cases where the token coincidentally appears in server-provided
        # fields (reason, response text, or stringified status code).
        # The property tests that the *implementation* does not leak the token,
        # not that server-echoed data might match it.
        assume(token not in reason)
        assume(token not in response_text)
        assume(token not in str(status_code))
        assume(token != "posting module request")

        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = status_code
        mock_response.reason = reason
        mock_response.text = response_text
        mock_post.return_value = mock_response

        conn = REDCapModuleConnection(
            token=token,
            url="https://redcap.example.com/api/",
            module_prefix="test_module",
        )

        with pytest.raises(REDCapConnectionError) as exc_info:
            conn.post_module_request(
                action_page="test_action",
                data={},
            )

        error_message = exc_info.value.message

        # Error message SHALL contain the HTTP status code and reason
        assert str(status_code) in error_message
        assert reason in error_message

        # Error message SHALL NOT contain the API token
        assert token not in error_message


# --- Property-based tests for Identifier Validation Boundary (Task 4.2) ---


class TestIdentifierValidationBoundaryProperty:
    """Property-based tests for identifier validation.

    Feature: redcap-module-connection, Property 2: Identifier Validation Boundary
    """

    @given(
        identifier=st.from_regex(r"[a-z0-9_]{1,64}", fullmatch=True),
    )
    @settings(max_examples=100)
    def test_valid_identifiers_accepted(self, identifier):
        """**Validates: Requirements 1.4, 1.5, 6.2**

        For any string matching ^[a-z0-9_]{1,64}$, the identifier validation
        SHALL accept it without error.
        """
        # Should not raise any exception
        REDCapModuleConnection._validate_identifier(  # noqa: SLF001
            identifier, "test_param"
        )

    @given(
        identifier=st.text().filter(lambda s: not re.match(r"^[a-z0-9_]{1,64}$", s)),
    )
    @settings(max_examples=100)
    def test_invalid_identifiers_rejected(self, identifier):
        """**Validates: Requirements 1.4, 1.5, 6.2**

        For any string that is empty, contains only whitespace, contains
        characters outside [a-z0-9_], or exceeds 64 characters, the identifier
        validation SHALL raise a REDCapConnectionError indicating which
        parameter is invalid.
        """
        with pytest.raises(REDCapConnectionError) as exc_info:
            REDCapModuleConnection._validate_identifier(  # noqa: SLF001
                identifier, "test_param"
            )

        assert "test_param" in exc_info.value.message


# --- Property-based tests for Text Response Pass-Through (Task 4.6) ---


class TestTextResponsePassThroughProperty:
    """Property-based tests for text response pass-through.

    Feature: redcap-module-connection, Property 6: Text Response Pass-Through
    """

    @given(
        response_text=st.text(
            alphabet=_safe_characters,
            max_size=500,
        ),
        return_format=st.sampled_from(["csv", "xml"]),
    )
    @settings(max_examples=100, deadline=None)
    def test_text_response_returned_without_modification(
        self, response_text, return_format
    ):
        """**Validates: Requirements 3.2**

        For any text string returned as an HTTP response body, when
        post_module_request is called with return_format of "csv" or "xml",
        the method SHALL return the exact response text without modification.
        """
        conn = REDCapModuleConnection(
            token="test_token",
            url="https://redcap.example.com/api/",
            module_prefix="test_module",
        )

        with patch("redcap_api.redcap_module_connection.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.ok = True
            mock_response.text = response_text
            mock_post.return_value = mock_response

            result = conn.post_module_request(
                action_page="test_action",
                data={},
                return_format=return_format,
            )

        assert result == response_text


# --- Property-based tests for Invalid JSON Detection (Task 4.7) ---


def _is_valid_json(s: str) -> bool:
    """Check if a string is valid JSON."""
    try:
        json.loads(s)
        return True
    except (json.JSONDecodeError, ValueError):
        return False


class TestInvalidJSONDetectionProperty:
    """Property-based tests for invalid JSON detection.

    Feature: redcap-module-connection, Property 7: Invalid JSON Detection
    """

    @given(
        response_body=st.text(
            alphabet=_safe_characters,
            min_size=1,
            max_size=200,
        ).filter(lambda s: not _is_valid_json(s)),
    )
    @settings(max_examples=100, deadline=None)
    @patch("redcap_api.redcap_module_connection.requests.post")
    def test_non_json_response_raises_connection_error(self, mock_post, response_body):
        """**Validates: Requirements 3.5**

        For any response body that is not valid JSON (given a successful
        HTTP status), when post_module_request is called with
        return_format="json", the method SHALL raise a
        REDCapConnectionError indicating that JSON parsing failed.
        """
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.side_effect = JSONDecodeError(
            "Expecting value", response_body, 0
        )
        mock_post.return_value = mock_response

        conn = REDCapModuleConnection(
            token="test_token",
            url="https://redcap.example.com/api/",
            module_prefix="test_module",
        )

        with pytest.raises(REDCapConnectionError) as exc_info:
            conn.post_module_request(
                action_page="test_action",
                data={},
                return_format="json",
            )

        assert "JSON parsing failed" in exc_info.value.message


# --- Property-based tests for Factory Construction Round-Trip (Task 4.8) ---


class TestFactoryConstructionRoundTripProperty:
    """Property-based tests for factory construction round-trip.

    Feature: redcap-module-connection, Property 8: Factory Construction Round-Trip
    """

    @given(
        url=st.from_regex(r"https?://[a-z]+\.[a-z]+/api", fullmatch=True),
        token=st.text(
            alphabet=_safe_characters,
            min_size=1,
            max_size=50,
        ),
        prefix=st.from_regex(r"[a-z0-9_]{1,64}", fullmatch=True),
    )
    @settings(max_examples=100)
    def test_factory_produces_matching_properties(self, url, token, prefix):
        """**Validates: Requirements 4.1, 4.4**

        For any valid REDCapParameters (containing a URL string and a token
        string) and any valid module prefix string, calling create_from SHALL
        produce an instance whose url property equals the parameters' URL and
        whose module_prefix property equals the provided module prefix.
        """
        parameters = {"url": url, "token": token}

        conn = REDCapModuleConnection.create_from(
            parameters=parameters, module_prefix=prefix
        )

        assert conn.url == url
        assert conn.module_prefix == prefix
