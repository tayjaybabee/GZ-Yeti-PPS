from inspyre_toolbox.exceptional import CustomRootException


class GZYetiPPSError(CustomRootException):
    """
    Base class for all GZYetiPPS errors.
    """
    default_message = "An error occurred in GZYetiPPS."

