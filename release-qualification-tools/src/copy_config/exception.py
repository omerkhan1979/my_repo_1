from enum import Enum, auto, unique
import sys
from typing import Any

from src.utils.console_printing import error_print, red


@unique
class CopyConfigErrorCodes(str, Enum):
    """
    Coordinate with error messages with an error code.
    """

    def __new__(cls, error_message, value):
        # __new__   helps control creation of a new instance
        # __init__  helps control of initialization of a new instance
        obj = str.__new__(cls, [value])
        obj._value_ = value
        obj.error_message = error_message
        return obj

    ERR_INCORRECT_ERRCODE = (
        "INVALID_CODE",
        auto(),
    )  # error code passed is not specified in enum ErrorCodes
    NO_SOURCE_DETAILS = ("No source details provided", auto())
    NO_SOURCE_ENV = ("Valid environmental source needs to be provided", auto())
    NO_TARGET_DETAILS = ("No target details provided", auto())
    PARSE_ERROR = ("Missing parameters", auto())
    NO_CLIENT = ("A Client was not provided", auto())
    NOT_VALID_CLIENT = ("Client was provided but not valid", auto())
    FAILED_SOURCE_RETRIEVAL = (
        "During the retrieval of configuration data from source, a failure occurred",
        auto(),
    )
    TARGET_TOKEN_INVALID = ("Token for Target is invalid", auto())
    FAILED_TARGET_UPDATE = (
        "During the update of configuration data on target, a failure occurred",
        auto(),
    )
    TARGET_CONFIG_INVALID = (
        "Unable to create the target config object. Check that the target details again.",
        auto(),
    )
    FILTER_FAILURE = ("Going through the filter process failed", auto())
    SANITY_CHECK_FAILURE = (
        "After performing the sanity check, the target environment "
        "configuration still defers from source. Please review all logs, try "
        "again. See @team-chamaeleon for further help.",
        auto(),
    )
    LOCATION_CREATION_FAILED = ("Unable to create location", auto())
    FLOW_RACK_COMPARE_SOURCE = ("Source flow rack was not formatted correctly", auto())
    FLOW_RACK_COMPARE_TARGET = ("Target flow rack was not formatted correctly", auto())
    FLOW_RACK_COMPARE_GENERATE = (
        "Unable to generate the flow rack difference between source and target",
        auto(),
    )
    TOTE_TYPE_COMPARE_SOURCE = ("Source tote type was not formatted correctly", auto())
    TOTE_TYPE_COMPARE_TARGET = ("Target tote type was not formatted correctly", auto())
    TOTE_TYPE_COMPARE_GENERATE = (
        "Unable to generate the tote type difference between source and target",
        auto(),
    )
    LOCATION_DOES_NOT_EXIST_SOURCE = (
        "The supplied location for source has no details",
        auto(),
    )
    SPOKE_DOES_NOT_EXIST_SOURCE = (
        "The supplied spoke for source has no details",
        auto(),
    )
    SPOKE_CREATION_FAILED = (
        "Unable to create spoke for location for retailer env",
        auto(),
    )
    SPOKE_UPDATE_FAILED = (
        "Unable to update spoke for a location for retailer env",
        auto(),
    )


class CopyConfigException(Exception):
    """Copy Configuration Exception"""

    code_exception = CopyConfigErrorCodes.ERR_INCORRECT_ERRCODE

    def __init__(self, code_exception: Any, message=""):
        """Create the CopyConfigException object based on the infromation
        passed in

        Args:
            code_exception (Any): used to check why type of error it is
            message (str, optional): message to provide in the exception.
            Defaults to "".

        Raises:
            CopyConfigException: what gets through
        """
        # Raise a separate exception in case the error code passed isn't
        # specified in the ErrorCodes enum
        if not isinstance(code_exception, CopyConfigErrorCodes):
            msg = "Error code passed in the error_code param must be of type "
            "{0}"
            raise CopyConfigException(
                self.code_exception,
                msg,
            )

        self.code_exception = code_exception

        # storing the traceback which provides useful information about where
        # the exception occurred
        self.traceback = sys.exc_info()

        # Prefixing the error code to the exception message
        try:
            msg = "[{0}] {1}".format(
                self.code_exception.name, str(self.code_exception.error_message)
            )
            error_print(red(msg))
        except (IndexError, KeyError):
            msg = "[{0}] {1}".format(self.error_code.name, message)
        super().__init__(msg)
