python_sources(name="redcap_api")

python_distribution(
    name="dist",
    dependencies=[":redcap_api"],
    wheel=True,
    sdist=True,
    provides=python_artifact(
        name="redcap-api",
        version="0.1.0",
        description="Library for interacting with the REDCap API",
        author="NACC",
        author_email="nacchelp@uw.edu",
        url="https://github.com/naccdata/redcap-api"),
)
