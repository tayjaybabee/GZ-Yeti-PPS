from inspy_logger import InspyLogger, Loggable
from .common.constants import DEFAULT_LOG_LEVEL, PROG as PROG_NAME

ROOT_LOGGER = InspyLogger(PROG_NAME, console_level=DEFAULT_LOG_LEVEL, no_file_logging=True)


__all__ = [
    'ROOT_LOGGER',
    'Loggable'
]
