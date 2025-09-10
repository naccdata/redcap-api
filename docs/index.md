# REDCap API

Provides library for interacting with REDCap projects, along with related tools.

# Tools

## REDCap Error Checks Import

Bulk imports error checks into REDCap.

The error check CSVs are created and uploaded to [uniform-data-set](https://github.com/naccdata/uniform-data-set), which are then reorganized and stored in [s3://nacc-qc-rules/CSV/](https://us-west-2.console.aws.amazon.com/s3/buckets/nacc-qc-rules?region=us-west-2&bucketType=general&prefix=CSV/&showversions=false). The gear then pulls the CSVs from S3 to perform the import to REDCap.

### Input Arguments

This tool takes in the following inputs. Aside from the profile, none are explicitly required and will use the listed default if not provided.

| Field | Default | Description |
| ----- | ------- | ----------- |
| `profile` | Required | The S3 profile to use - requires access to both the S3 bucket and parameter store |
| `s3_bucket` | `nacc-qc-rules` | The S3 URI containing the error check CSVs; expects files to be under `CSV/<MODULE>/<FORM_VER>/<PACKET>/form_<FORM_NAME>*error_checks_<TYPE>.csv` (PACKET is not required for all modules) |
| `redcap_project_path` | `/redcap/aws/qcchecks` | AWS parameter base path for the target REDCap project to import error checks to |
| `modules` | `all` | The comma-deliminated list of modules to perform the import for. If `all`, will run for every module directory found under `<checks_s3_bucket>/CSV` |
| `fail_fast` | `true` | Whether or not to fail fast during import - if set to true, any error check CSV that fails import will halt the gear |
| `dry_run` | `false` | Whether or not this is a dry run. If true, will pull and read the error checks but will **not** import them into REDCap |

### Running

To run, install the distribution and run via the CLI entrypoint. Example:
```bash
redcap-error-checks-import -p default -m 'UDS' --fail-fast --dry-run
```

for staging
```bash
redcap-error-checks-import -p default -m 'UDS' --redcap-project-path '/redcap/aws/qcchecks-staging' --s3-bucket 'nacc-qc-rules-staging' --fail-fast --dry-run
```