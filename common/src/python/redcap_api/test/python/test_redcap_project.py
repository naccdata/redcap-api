"""Tests for REDCapProject.export_user_role_assignments."""

from unittest.mock import create_autospec

import pytest
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
