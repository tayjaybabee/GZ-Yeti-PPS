from .base import ConfigBase
from .spec import CONFIG_SPECS


class LoggerConfig(ConfigBase):
    CONFIG_SPEC = CONFIG_SPECS['logger']

    def __init__(self):

