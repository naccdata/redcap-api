"""REDCap-specific parameter store dictionary types."""
from typing_extensions import TypedDict


class REDCapParameters(TypedDict):
    """Dictionary type for parameters needed to access a REDCap project."""
    url: str
    token: str


class REDCapReportParameters(TypedDict):
    """Dictionary type for parameters needed to access a REDCap report."""
    url: str
    token: str
    reportid: str
