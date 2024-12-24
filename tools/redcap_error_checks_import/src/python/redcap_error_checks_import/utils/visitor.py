"""Module to handle downloading error check CSVs from S3."""
import logging
from csv import DictReader, Error
from typing import Any, Dict, List, TextIO

from .utils import ErrorCheckKey

log = logging.getLogger(__name__)


class ErrorCheckCSVVisitor:
    """Visitor for an Error Check CSV file."""

    # error_no, do_in_redcap, in_prev_versions,
    # questions, and any other extra headers ignored
    REQUIRED_HEADERS = ("error_code", "error_type", "form_name", "packet",
                        "var_name", "check_type", "test_name", "short_desc",
                        "full_desc", "test_logic", "comp_forms", "comp_vars")

    ALLOWED_EMPTY_FIELDS = ("comp_forms", "comp_vars")

    def __init__(self, key: ErrorCheckKey) -> None:
        """Initializer."""
        self.__key = key
        self.__validated_error_checks: List[Dict[str, Any]] = []

    @property
    def validated_error_checks(self) -> List[Dict[str, Any]]:
        """Get the validated error checks.

        Returns:
            The running list of error checks.
        """
        return self.__validated_error_checks

    def visit_header(self, header: List[str]) -> bool:
        """Adds the header, and asserts all required fields are present.

        Args:
          header: list of header names
        Returns:
          True if the header has all required fields, False otherwise
        """
        valid = True
        for h in self.REQUIRED_HEADERS:
            if h not in header:
                # in the case of the enrollment form, packet is
                # set to None and allowed to be missing
                if h == 'packet' and self.__key.packet is None:
                    continue

                log.error(f"Missing expeceted header: {h}")
                valid = False

        return valid

    def log_row_error(self, line_num: int, field: str, msg: str) -> bool:
        """Logs a row error and returns False.

        Args:
            line_num: The line number of the failure
            field: The field that failed
            msg: The error message to report
        Returns:
            False
        """
        log.error(f'Row {line_num}: Field {field} {msg}')
        return False


    def visit_row(self, row: Dict[str, Any], line_num: int) -> bool:
        """Visit the dictionary for a row (per DictReader). Ensure the row
        matches the expected form/packet and fields and data is filled for all
        files.

        Args:
          row: the dictionary for a row from a CSV file
          line_num: The line number of the row
        Returns:
          True if the row was processed without error, False otherwise
        """
        valid = True
        for field, value in row.items():
            if (not value and field not in self.ALLOWED_EMPTY_FIELDS
                    and field in self.REQUIRED_HEADERS):
                valid = self.log_row_error(line_num, field, 'cannot be empty')

        form_name = row.get('form_name', '')
        if form_name != self.__key.form_name:
            valid = self.log_row_error(line_num, field,
                f'does not match expected form name {self.__key.form_name}')

        error_code = row.get('error_code', '')
        if not error_code.startswith(self.__key.form_name):
            valid = self.log_row_error(line_num, field,
                f'does not start with expected form name {self.__key.form_name}')

        # check packet is consistent
        if self.__key.packet:
            visit_type = self.__key.get_visit_type()
            if visit_type and visit_type not in error_code:
                valid = self.log_row_error(line_num, field,
                    f'does not have expected visit type {visit_type}')

            packet = row.get('packet', '')
            if packet != self.__key.packet:
                valid = self.log_row_error(line_num, field,
                    f'does not match expected packet {self.__key.packet}')

        # only import items in REQUIRED_HEADERS if valid
        if valid:
            upload_row = {
                field: row[field]
                for field in self.REQUIRED_HEADERS if field in row
            }
            self.__validated_error_checks.append(upload_row)

        return valid


def read_csv(input_file: TextIO,
             visitor: ErrorCheckCSVVisitor,
             delimiter: str = ',') -> bool:
    """Reads CSV file and applies visitor to each row.

    Args:
      input_file: the input stream for the CSV file
      visitor: the visitor
      delimiter: Expected delimiter for the CSV
    Returns:
      True if the input file was processed without error, False otherwise
    """
    csv_sample = input_file.read(1024)
    if not csv_sample:
        log.error("CSV file is empty")
        return False

    input_file.seek(0)

    reader = DictReader(input_file, delimiter=delimiter)
    if not reader.fieldnames:
        log.error("CSV has no headers")
        return False

    # visitor should handle errors for invalid headers/rows
    success = visitor.visit_header(list(reader.fieldnames))
    if not success:
        return False

    try:
        for record in reader:
            row_success = visitor.visit_row(record, line_num=reader.line_num)
            success = row_success and success
    except Error as error:
        log.error(f"Encountered error reading CSV: {error}")
        return False

    return success
