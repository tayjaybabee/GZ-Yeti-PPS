from configparser import ConfigParser
from pathlib import Path
from platformdirs import PlatformDirs
from ..common.constants import PROG as PROG_NAME, AUTHOR


class ConfigBase(ConfigParser):
    """
    Base class for managing configuration systems.
    Automatically handles creating, loading, and updating INI-based configurations.

    Subclasses must provide a valid CONFIG_SPEC class constant initialized from ConfigSpec.

    Features:
        - Automatically writes config to disk if deviations from defaults occur.
        - Handles config version mismatches and updates files accordingly.

    Example:
        class LoggerConfig(ConfigBase):
            CONFIG_SPEC = ConfigSpec('logger')

    """

    APP_NAME = PROG_NAME
    AUTHOR   = AUTHOR

    CONFIG_SPEC = None  # Override in subclasses

    def __init__(self):
        super().__init__()

        if not self.CONFIG_SPEC:
            raise ValueError('CONFIG_SPEC must be defined in subclass.')

        self.config_dir = Path(
            PlatformDirs(self.APP_NAME, self.AUTHOR).user_config_path
        )
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.config_file = self.config_dir / f"{self.CONFIG_SPEC.config_system}.ini"

        self._load_config()
        self._check_config_version()

    def _load_config(self):
        """Load config from disk, create from defaults if missing."""
        if not self.config_file.exists():
            self._create_default_config()
            return

        self.read(self.config_file)

        updated = False
        for key, spec in self.CONFIG_SPEC.spec.items():
            if not self.has_option('DEFAULT', key):
                self.set('DEFAULT', key, str(spec['default']))
                updated = True

        if updated:
            self._save()

    def _create_default_config(self):
        """Creates a default config based on CONFIG_SPEC."""
        self['DEFAULT'] = {
            key: str(spec['default'])
            for key, spec in self.CONFIG_SPEC.spec.items()
        }
        self['META'] = {
            'config_version': str(self.CONFIG_SPEC.meta['config_version'])
        }
        self._save()

    def _check_config_version(self):
        """Checks if config version matches, updates if necessary."""
        disk_version = self.getint('META', 'config_version', fallback=0)
        spec_version = self.CONFIG_SPEC.meta.get('config_version', 0)

        if disk_version != spec_version:
            self['META']['config_version'] = str(spec_version)

            # Add new keys from spec if they're missing
            for key, spec in self.CONFIG_SPEC.spec.items():
                if not self.has_option('DEFAULT', key):
                    self.set('DEFAULT', key, str(spec['default']))

            self._save()

    def _save(self):
        """Saves the current configuration to disk."""
        with self.config_file.open('w') as f:
            self.write(f)

    def set_option(self, key, value):
        """Set a config option and immediately save."""
        if key not in self.CONFIG_SPEC.spec:
            raise KeyError(f"'{key}' is not a valid configuration option.")

        self.set('DEFAULT', key, str(value))
        self._save()

    def get_option(self, key):
        """Retrieve a config option with correct type."""
        spec = self.CONFIG_SPEC.spec.get(key)
        if not spec:
            raise KeyError(f"'{key}' is not a valid configuration option.")

        type_map = {
            'bool': self.getboolean,
            'int': self.getint,
            'float': self.getfloat,
            'string': self.get,
            'path': lambda section, opt: Path(self.get(section, opt)),
        }

        getter = type_map.get(spec['type'], self.get)

        return getter('DEFAULT', key)
