#!/usr/bin/env python3
"""
Entrypoing for the REDCap Error Checks Import.
"""
import argparse
import logging

from pathlib import Path
from redcap_error_checks_import import REDCapErrorChecksImporter

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def entrypoint():
    parser = argparse.ArgumentParser(prog='REDCap Error Checks Importer')
    parser.add_argument('--version', action='version', version=f'Run Form Converter version 0.1.0')

    parser.add_argument('-p', '--aws-profile', dest="aws_profile", type=str, required=True,
                        help='The AWS profile to use; requires access to both the parameter store and S3 bucket')

    parser.add_argument('-b', '--s3-bucket', dest="s3_bucket", type=str, required=False,
                        default='nacc-qc-rules',
                        help='The S3 URI containing the error check CSVs; defaults to the NACC QC Rules bucket')
    parser.add_argument('-r', '--redcap-project-path', dest="redcap_project_path", type=str, required=False,
                        default='/redcap/aws/qcchecks/',
                        help='AWS parameter base path for the target REDCap project to import error checks to; '
                             + 'defaults to the NACC QC Checks project')

    parser.add_argument('-m', '--modules', dest="modules", type=str, required=False, default='all',
                        help='Comma-deliminated list of modules to perform the import for. Defaults to \'all\', '
                             + 'which just means it will run for every subdirectory found under CSV`')

    parser.add_argument('--fail-fast', dest="fail_fast", action='store_true',
                        help='Whether or not to fail fast during import')
    parser.add_argument('--dry-run', dest="dry_run", action='store_true',
                        help='Whether or not to do a dry run; will read CSVs but will not import into REDCap')

    args = parser.parse_args()

    log.info("Arguments:")
    log.info(f"aws_profile:\t\t{args.aws_profile}")
    log.info(f"s3_bucket:\t\t{args.s3_bucket}")
    log.info(f"redcap_project_path:\t{args.redcap_project_path}")
    log.info(f"modules:\t\t\t{args.modules}")
    log.info(f"fail_fast:\t\t{args.fail_fast}")
    log.info(f"dry_run:\t\t\t{args.dry_run}")

    s3_bucket = args.s3_bucket.replace('s3://', '').rstrip('/')
    redcap_project_path = args.redcap_project_path if args.redcap_project_path.endswith('/') \
        else f'{args.redcap_project_path}/'
    modules = [x.strip() for x in args.modules.split(',')]

    importer = REDCapErrorChecksImporter(aws_profile=args.aws_profile,
                                         s3_bucket=s3_bucket,
                                         redcap_project_path=redcap_project_path,
                                         modules=modules,
                                         fail_fast=args.fail_fast,
                                         dry_run=args.dry_run)
    importer.run()


if __name__ == "__main__":
    entrypoint()
