"""Defines REDCap Import Error Checks."""
import json
import logging
from io import StringIO
from typing import Any, Dict, List, Optional

from pydantic import TypeAdapter, ValidationError
from redcap_api.redcap_connection import (
    REDCapConnection,
    REDCapConnectionError,
)
from redcap_api.redcap_parameter_store import REDCapParameters
from redcap_api.redcap_project import REDCapProject

from .utils.utils import (
    ErrorCheckImportStats,
    ErrorCheckKey,
    RuntimeException,
)
from .utils.visitor import ErrorCheckCSVVisitor, read_csv

log = logging.getLogger(__name__)


class REDCapErrorChecksImporter:
    """Class to define REDCap error checks importer."""

    def __init__(self,
                 aws_profile: str,
                 s3_bucket: str,
                 redcap_project_path: str,
                 modules: List[str],
                 fail_fast: bool = True,
                 dry_run: bool = False) -> None:
        """Initializer.

        Args:
            aws_profile: The AWS profile; expects to have read access
                from the S3 bucket and parameter store
            s3_bucket: The S3 bucket to read error check CSVs from; expects
                files to be under a `CSV` directory
            redcap_project_path: AWS parameter base path for the target
                REDCap project to import into
            modules: List of modules to import error checks for
            fail_fast: Whether or not to fail fast on error
            dry_run: Whether or not this is a dry run
        """
        session = boto3.Session(profile_name=aws_profile)

        # get S3 bucket
        self.__bucket = s3_bucket
        self.__s3 = session.resource('s3').Bucket(s3_bucket)

        # build redcap project from parameter store
        ssm = session.client('ssm')
        parameters = session.client('ssm').get_parameter(Name=redcap_project_path,
                                                         WithDecryption=True)
        type_adaptor = TypeAdaptor(REDCapParameters)
        try:
            redcap_params = type_adapter.validate_python(parameters)
            redcap_connection = REDCapConnection.create_from(redcap_params)
            self.__redcap_project = REDCapProject.create(redcap_connection)
        except (ParameterError, REDCapConnectionError) as error:
            raise RuntimeException(
                f"Failed to load REDCap project from {redcap_project_path}: {error}"
            ) from error

        # initialize new stats object
        self.__stats = ErrorCheckImportStats()

    @property
    def stats(self) -> ErrorCheckImportStats:
        """Returns the stats object."""
        return self.__stats

    def build_full_path(self, key: ErrorCheckKey) -> str:
        """Build the full S3 path as a string from the error check key."""
        return f's3://{self.__bucket}/{key.full_path}'

    @classmethod
    def load_error_check_csv(cls,
                             key: ErrorCheckKey,
                             file: Dict[Any, Any],
                             stats: ErrorCheckImportStats) -> Optional[List[Dict[str, Any]]]:
        """Load the error check CSV.

        Args:
            key: ErrorCheckKey containing details about the S3 key
            file: The S3 file object
        Returns:
            List of the validated and read in error checks.
        """
        visitor = ErrorCheckCSVVisitor(key=key)
        data = StringIO(file['Body'].read().decode('utf-8'))
        success = read_csv(input_file=data, visitor=visitor)

        if not success:
            log.error(f"Errors encountered while reading from {key.full_path}:")
            return None

        error_checks = visitor.validated_error_checks
        if not error_checks:
            log.error(f"No error checks found in {key.full_path}; invalid file?")
            return None

        # check for duplicates
        duplicates = stats.add_error_codes([x['error_code'] for x in error_checks])
        if duplicates:
            log.error(
                f"Found duplicated errors, will not import file: {duplicates}")
            return None

        return error_checks

    def import_to_redcap(self, error_checks: List[Dict[str, Any]]) -> None:
        """Import the error checks into REDCap in JSON format.

        Args:
            error_checks: The error check records to import.
        """
        if self.__dry_run:
            log.info("DRY RUN: Skipping import.")
            return

        # Upload to REDCap; import each record in JSON format
        try:
            num_records = self.__redcap_project.import_records(
                json.dumps(error_checks), data_format='json')
            log.info(f"Imported {num_records} records from {full_path}")
            self.__stats.add_to_total_records(num_records)
        except REDCapConnectionError as error:
            raise RuntimeException(error.message) from error

    def run(self) -> None:
        """Runs the REDCAP Error Checks import process."""
        log.info("Running REDCAP error check import")
        file_objects = self.__s3.filter(Prefix='CSV')

        if not file_objects:
            log.error(f"No files found in {self.__bucket}/CSV")
            return

        # keep track of import status
        for key, file in file_objects.items():
            if not key.endswith('.csv'):
                continue

            error_key = ErrorCheckKey.create_from_key(key)
            if self.__modules != ['all'] and error_key.module not in self.__modules:
                continue

            # Load from files from S3
            full_path = self.build_full_path(error_key)
            log.info(f"Loading error checks from {full_path}")
            error_checks = self.load_error_check_csv(error_key, file, stats)

            if not error_checks:
                if self.__fail_fast:
                    log.error("fail_fast set to True, halting execution")
                    return
                else:
                    log.info("Errors encountered, continuing to next file")
                    self.__stats.add_failed_file(key)
                    continue

            self.import_to_redcap(error_checks)

        # if we did not fail fast before, fail now
        if self.__stats.failed_files:
            raise RuntimeException("Failed to import the following:\n" +
                                   "\n".join(self.__stats.failed_files))

        log.info(f"Import complete! Imported {self.__stats.total_records} total records")
