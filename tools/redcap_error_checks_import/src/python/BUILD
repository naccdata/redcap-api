python_requirements(name="reqs")
python_sources(name="redcap_error_checks_import")

python_distribution(
    name="dist",
    dependencies=[":redcap_error_checks_import"],
    wheel=True,
    sdist=True,
    provides=python_artifact(
        name="redcap-error-checks-import",
        version="0.1.0",
        description="Imports error checks into REDCap",
        author="NACC",
        author_email="nacchelp@uw.edu",
        url="https://github.com/naccdata/redcap-api/tools/redcap_error_checks_import"),
)

pex_binary(name="bin", entry_point="bin/entrypoint.py")
