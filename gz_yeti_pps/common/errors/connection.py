from gz_yeti_pps.common.errors import GZYetiPPSError


class GZYetiPPSConnectionError(GZYetiPPSError):
    """
    Raised when there is an error connecting to the YetiPPS server.
    """
    default_message = "Unable to connect to YetiPPS device."

    def __init__(self, host: str = None, specific_error: str = None):
        if host is not None and isinstance(host, str):
            self.additional_message = f"Unable to connect to YetiPPS device at {host}."

        if specific_error is not None and isinstance(specific_error, str):
            self.additional_message += f'\n{specific_error}'

        super().__init__()


__all__ = [
    'GZYetiPPSConnectionError'
]
