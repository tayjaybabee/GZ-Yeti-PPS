import json
from dataclasses import make_dataclass, field, asdict
from pathlib import Path
from ...log_engine import InspyLogger, Loggable
from inspyre_toolbox.humanize import Numerical


MOD_LOGGER = InspyLogger('GZ-Yeti-PPS', console_level='DEBUG', no_file_logging=True)


def get_file_dir():
    return Path(__file__).parent


CONFIG_SYSTEM_MAP = {

    'core': {
        'friendly_name': 'Core',
        'description': 'The configuration for the core system.',
        'spec_file': get_file_dir().joinpath('core_config.json')
    },

    'logger': {
        'friendly_name': 'Logger',
        'description': 'The configuration for the logging system.',
        'spec_file': get_file_dir().joinpath('logger_config.json')
    },

    'conn_check_cache': {
        'friendly_name': 'Connection Check Cache',
        'description': 'The configuration for the connection check cache.',
        'spec_file': get_file_dir().joinpath('conn_check_cache_config.json')
    },

    'get_cache': {
        'friendly_name': 'Get Cache',
        'description': 'The configuration for the get cache.',
        'spec_file': get_file_dir().joinpath('get_cache_config.json')
    },

    'state_cache': {
        'friendly_name': 'State Cache',
        'description': 'The configuration for the state cache.',
        'spec_file': get_file_dir().joinpath('state_cache_config.json')
    }
}


CONFIG_SYSTEM_NAMES = list(CONFIG_SYSTEM_MAP.keys())
MOD_LOGGER.debug(f'CONFIG_SYSTEM_NAMES: {", ".join(CONFIG_SYSTEM_NAMES)}')


fields = [
    (key, Path, field(default=CONFIG_SYSTEM_MAP[key]['spec_file']))
    for key in CONFIG_SYSTEM_MAP
]

SpecFiles = make_dataclass('SpecFiles', fields, frozen=True)

SPEC_FILE_PATHS = SpecFiles()


del fields
del SpecFiles
del CONFIG_SYSTEM_MAP


class ConfigSpec(Loggable):
    """
    The ConfigSpec class is used to store the configuration for a specific system.

    Properties:
        config_system (str):
            The name of the configuration system.

        defaults (dict):
            The default values for the configuration system.

        file_path (Path):
            The path to the configuration file.

        meta (dict):
            The meta-data for the configuration system specification.

        spec (dict):
            The configuration for the configuration system.
    """
    SPEC_DIR        = get_file_dir()
    SPEC_FILE_PATHS = asdict(SPEC_FILE_PATHS)
    _instances      = {}

    def __new__(cls, config_system):
        """
        Creates a new instance of the ConfigSpec class.

        Parameters:
            config_system (str):
                The name of the configuration system.

        Returns:
            ConfigSpec:
                A new instance of the ConfigSpec class.
        """
        config_system = config_system.lower()

        if config_system not in cls._instances:
            instance = super(ConfigSpec, cls).__new__(cls)
            cls._instances[config_system] = instance

        return cls._instances[config_system]

    def __init__(self, config_system: str, skip_auto_load: bool = False):
        """
        Initializes an instance of the ConfigSpec class.

        Parameters:
            config_system (str):
                The name of the configuration system.

            skip_auto_load (bool, optional):
                Whether to *skip* automatically loading the spec file.
        """
        if hasattr(self, '_initialized') and self._initialized:
            return

        self.__config_system = None
        self.__defaults      = None
        self.__file_path     = None
        self.__meta          = None
        self.__spec          = None

        super().__init__(MOD_LOGGER)
        log = self.class_logger
        log.debug('Checking if initialized...')

        self._initialized = False
        self.config_system = config_system

        if not skip_auto_load:
            log.debug(f'Auto-loading config spec for {config_system}...')
            _ = self.spec
        else:
            log.debug(f'Skipping auto-loading config spec for {config_system}...')
            self.__skip_auto_load = True

        self._initialized = True
        log.debug(f'Config spec for "{self.config_system}" initialized {"-but not loaded-" if skip_auto_load else ""} successfully!')

    @property
    def config_system(self) -> str:
        return self.__config_system

    @config_system.setter
    def config_system(self, config_system: str) -> None:
        log = self.method_logger
        log.debug(f'Received request to set `config_system` to {config_system}...')

        if hasattr(self, '_initialized') and self._initialized:
            log.error('Cannot modify config system after initialization.')
            raise AttributeError('Cannot modify config system after initialization')

        log.debug(f'Validating new value: {config_system}...')
        if not isinstance(config_system, str):
            log.error(f'Config system must be a string, not {type(config_system)}')
            raise TypeError(f'Config system must be a string, not {type(config_system)}')

        config_system = config_system.lower()

        log.debug(f'Ensuring config system is listed in `CONFIG_SYSTEM_NAMES`...')
        if config_system not in CONFIG_SYSTEM_NAMES:
            log.error(f'Config system must be one of {CONFIG_SYSTEM_NAMES}, not {config_system}')
            raise ValueError(f'Config system must be one of {CONFIG_SYSTEM_NAMES}, not {config_system}')

        self.__config_system = config_system
        log.debug(f'Set `config_system` to "{self.config_system}".')

        if not self.skip_auto_load and self.spec is None:
            log.debug(f'Auto-loading config spec for {config_system}...')
            _ = self.spec

    @property
    def defaults(self) -> dict:
        if self.__defaults is None:
            if self.__spec is None and not self.skip_auto_load:
                _ = self.spec
            elif self.__spec is None and self.skip_auto_load:
                self.method_logger.warning('Defaults not extracted because `skip_auto_load` is set to True, and there '
                                           'is no spec loaded.')

            if self.spec is None:
                self.__defaults = {}
            else:
                self.__defaults = self._extract_defaults()

        return self.__defaults

    @property
    def file_path(self) -> Path:
        """
        The path to the spec file.

        Returns:
            Path:
                The path to the spec file.
        """
        if not self.__file_path and self.config_system:
            self.method_logger.debug('Extracting file path from `SPEC_FILE_PATHS`...')
            self.__file_path = getattr(SPEC_FILE_PATHS, self.config_system)

        return self.__file_path

    @property
    def meta(self) -> dict:
        """
        Returns the meta-data from the spec file.

        Returns:
            dict:
                The meta-data from the spec file;
                    - 'config_version':
                        The version of the config spec file.

                    - 'config_system':
                        The name of the config system.
        """
        if self.__meta is None and not self.skip_auto_load:
            _ = self.spec

        return self.__meta

    @property
    def skip_auto_load(self) -> bool:
        """
        The flag to skip auto-loading the spec file.

        Returns:
            bool:
                True if auto-loading is to be skipped.
        """
        if not hasattr(self, '__skip_auto_load'):
            return False

        return self.__skip_auto_Load

    @property
    def spec(self) -> dict:
        """
        The configuration spec for the system.

        Returns:
            dict:
                The configuration spec for the system.
        """
        if self.__spec is None and self.file_path:
            self.method_logger.debug(f'Loading "{self.config_system}" spec from file...')
            self.__spec = self._load_spec_from_file()
            self.method_logger.debug('Defaults extracted successfully.')

        return self.__spec

    def _load_spec_from_file(self) -> dict:
        """
        Loads the spec from the spec-file.

        Returns:
            dict:
                The configuration spec for the system.
        """
        log = self.method_logger

        if not self.file_path:
            log.error('File path not set yet.')
            raise AttributeError('File path not set yet.')

        if not self.file_path.exists():
            log.error(f'File path does not exist: {self.file_path}')
            raise FileNotFoundError(f'File path does not exist: {self.file_path}')

        with open(self.file_path, 'r') as f:
            data = json.load(f)
            self.__meta = data.get('meta', None)
            spec = data.get('spec', None)

            if spec is None:
                err_msg = f'Spec not found in JSON file: {self.file_path}'
                log.error(err_msg)
                raise ValueError(err_msg)

            return spec

    def _extract_defaults(self) -> dict:
        """
        Returns the defaults from the spec file.

        Returns:
            dict:
                The defaults from the spec file.
        """
        defaults = {}

        for key, value in self.spec.items():
            default_value = value.get('default', None)
            defaults[key] = default_value

        return defaults

    def __str__(self) -> str:

        return json.dumps(self.spec, indent=4)

    def __repr__(self):

        return f'<ConfigSpec: {self.config_system} | @{hex(id(self))}>'


def are_specs_loaded() -> bool:
    """
    Checks if the config specs are loaded.

    Returns:
        bool:
            True if the config specs are loaded.
    """
    log = MOD_LOGGER.get_child('are_specs_loaded')
    log.debug('Checking if specs are loaded...')

    return hasattr(globals(), 'CONFIG_SPECS')


def get_config_specs() -> dict:
    """
    Returns the config specs.
    """
    log = MOD_LOGGER.get_child('get_config_specs')
    log.debug('Getting config specs...')
    if not are_specs_loaded():
        log.debug('Config specs not loaded yet. Loading...')
        globals()['CONFIG_SPECS'] = {}

        for system in CONFIG_SYSTEM_NAMES:
            log.debug(f'Loading config spec for "{system}"...')
            globals()['CONFIG_SPECS'][system] = ConfigSpec(system)

    num_spec = Numerical(len(globals()['CONFIG_SPECS']), 'spec')
    log.debug(f'Returning {num_spec.count_noun()}...')

    return globals()['CONFIG_SPECS']


if not are_specs_loaded():
    CONFIG_SPECS = get_config_specs()
    del get_config_specs
    del are_specs_loaded
    del ConfigSpec
    del get_file_dir


__all__ = [
    'ConfigSpec',
    'CONFIG_SPECS',
    'CONFIG_SYSTEM_NAMES'
]

