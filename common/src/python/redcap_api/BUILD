python_sources(name="redcap_api")

resource(name="license", source="LICENSE")
resource(
    name="py_typed",
    source="py.typed",
)
resource(name="pyproject", source="pyproject.toml")
resource(name="readme", source="README.md")

python_distribution(
    name="dist",
    dependencies=[":redcap_api", ":py_typed", ":license", ":readme", ":pyproject"],
    wheel=True,
    sdist=True,
    provides=python_artifact(
        name="redcap-api",
        version="0.1.3",
        description="Library for interacting with the REDCap API",
        author="NACC",
        author_email="nacchelp@uw.edu",
        url="https://github.com/naccdata/redcap-api",
    ),
)
