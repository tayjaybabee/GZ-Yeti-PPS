from typing import Optional, Union
from .config.spec import CONFIG_SPECS, ConfigSpec
from .log_engine import ROOT_LOGGER as PARENT_LOGGER
from .common.constants import APP_DIRS as DEFAULT_APP_DIRS
from pathlib import Path



MOD_LOGGER = PARENT_LOGGER.get_child('cache')


class CacheConfig:
    DEFAULT_CONFIG_DIR = DEFAULT_APP_DIRS.user_config_path

    def __init__(
            self,
            spec: ConfigSpec,
            config_file_path: Optional[Union[str, Path]]
    ):
        # Set up backing variables
        self.__config_file_path = None
        self.__spec             = None
        self.__max_size         = None
        self.__ttl              = None

        self.spec = spec


    @property
    def spec(self) -> Optional[ConfigSpec]:
        return self.__spec

    @spec.setter
    def spec(self, new) -> None:
        if not isinstance(new, ConfigSpec):
            raise TypeError(f"Spec must be of type 'ConfigSpec' not {type(new)}!")

        if self.__spec is not None:
            raise ValueError(f"Spec already set to {self.__spec}!")

        self.__spec = new


class GetCacheConfig(CacheConfig):
    def __init__(self):
        super().__init__()

