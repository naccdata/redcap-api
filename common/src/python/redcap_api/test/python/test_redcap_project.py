"""Tests for REDCapProject export methods."""

from unittest.mock import create_autospec

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from redcap_api.redcap_connection import REDCapConnection, REDCapConnectionError
from redcap_api.redcap_project import REDCapProject


@pytest.fixture()
def mock_connection():
    """Create a mock REDCapConnection."""
    return create_autospec(REDCapConnection, instance=True)


@pytest.fixture()
def project(mock_connection):
    """Create a REDCapProject with a mock connection."""
    return REDCapProject(
        redcap_con=mock_connection,
        pid=1,
        title="Test Project",
        pk_field="record_id",
        longitudinal=False,
        repeating_ins=False,
    )


class TestExportUserRoleAssignments:
    """Tests for the export_user_role_assignments method."""

    def test_sends_correct_payload(self, project, mock_connection):
        """Test that the method sends the correct data payload."""
        mock_connection.request_json_value.return_value = []

        project.export_user_role_assignments()

        mock_connection.request_json_value.assert_called_once_with(
            data={"content": "userRoleMapping"},
            message="exporting user-role assignments",
        )

    def test_returns_parsed_response(self, project, mock_connection):
        """Test that the method returns the parsed JSON response."""
        expected = [
            {"username": "user1", "unique_role_name": "U-ABC123"},
            {"username": "user2", "unique_role_name": "U-DEF456"},
        ]
        mock_connection.request_json_value.return_value = expected

        result = project.export_user_role_assignments()

        assert result == expected

    def test_returns_empty_list(self, project, mock_connection):
        """Test that the method returns an empty list when no assignments."""
        mock_connection.request_json_value.return_value = []

        result = project.export_user_role_assignments()

        assert result == []

    def test_propagates_api_error(self, project, mock_connection):
        """Test that REDCapConnectionError propagates on API error."""
        mock_connection.request_json_value.side_effect = REDCapConnectionError(
            message="Error: exporting user-role assignments\n"
            "HTTP Error:403 Forbidden: no permission"
        )

        with pytest.raises(REDCapConnectionError):
            project.export_user_role_assignments()

    def test_propagates_connection_error(self, project, mock_connection):
        """Test that REDCapConnectionError propagates on connection failure."""
        mock_connection.request_json_value.side_effect = REDCapConnectionError(
            message="Error connecting to https://redcap.example.com - "
            "connection refused"
        )

        with pytest.raises(REDCapConnectionError):
            project.export_user_role_assignments()


class TestExportUsers:
    """Tests for the export_users method."""

    def test_sends_correct_payload(self, project, mock_connection):
        """Test that the method sends the correct data payload."""
        mock_connection.request_json_value.return_value = []

        project.export_users()

        mock_connection.request_json_value.assert_called_once_with(
            data={"content": "user"},
            message="exporting users",
        )

    def test_returns_parsed_response(self, project, mock_connection):
        """Test that the method returns the parsed JSON response."""
        expected = [
            {
                "username": "jsmith",
                "email": "jsmith@example.com",
                "firstname": "John",
                "lastname": "Smith",
                "design": 1,
                "user_rights": 1,
                "data_export": 2,
                "api_export": 1,
            },
            {
                "username": "mjones",
                "email": "mjones@example.com",
                "firstname": "Mary",
                "lastname": "Jones",
                "design": 0,
                "user_rights": 0,
                "data_export": 1,
                "api_export": 0,
            },
        ]
        mock_connection.request_json_value.return_value = expected

        result = project.export_users()

        assert result == expected

    def test_returns_empty_list(self, project, mock_connection):
        """Test that the method returns an empty list when no users."""
        mock_connection.request_json_value.return_value = []

        result = project.export_users()

        assert result == []

    def test_propagates_api_error(self, project, mock_connection):
        """Test that REDCapConnectionError propagates on API error."""
        mock_connection.request_json_value.side_effect = REDCapConnectionError(
            message="Error: exporting users\nHTTP Error:403 Forbidden: no permission"
        )

        with pytest.raises(REDCapConnectionError):
            project.export_users()

    def test_propagates_connection_error(self, project, mock_connection):
        """Test that REDCapConnectionError propagates on connection failure."""
        mock_connection.request_json_value.side_effect = REDCapConnectionError(
            message="Error connecting to https://redcap.example.com - "
            "connection refused"
        )

        with pytest.raises(REDCapConnectionError):
            project.export_users()


class TestExportUsersProperties:
    """Property-based tests for the export_users method.

    Feature: export-users
    Property 1: For any list of user dictionaries returned by
    request_json_value, export_users SHALL return the exact same list
    without modification.
    """

    @given(
        user_list=st.lists(
            st.dictionaries(
                keys=st.text(min_size=1, max_size=20),
                values=st.one_of(
                    st.text(max_size=50),
                    st.integers(min_value=0, max_value=100),
                    st.booleans(),
                    st.none(),
                ),
                min_size=0,
                max_size=10,
            ),
            min_size=0,
            max_size=10,
        )
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_pass_through_invariant(self, user_list, mock_connection, project):
        """**Validates: Requirements 1.3, 2.1, 2.2, 2.3**

        For any list of user dictionaries returned by request_json_value,
        export_users returns the exact same list without modification.
        """
        mock_connection.request_json_value.return_value = user_list

        result = project.export_users()

        assert result is user_list
