from dataclasses import dataclass, field
from pathlib import Path
import json
from typing import Optional


@dataclass(frozen=True)
class ConfigLocator:
    default_app_dir: Path
    pointer_file_name: str            = field(init=False, default="config_location.json",)
    custom_config_dir: Optional[Path] = field(init=False, default=None)

    def __post_init__(self):
        object.__setattr__(self, 'custom_config_dir', self._load_pointer_file())

    @property
    def pointer_file(self) -> Path:
        return self.default_app_dir / self.pointer_file_name

    def _load_pointer_file(self) -> Optional[Path]:
        if self.pointer_file.exists():
            with self.pointer_file.open('r') as f:
                data = json.load(f)
            return Path(data.get("custom_config_dir"))
        return None

    def custom_config_set(self) -> bool:
        """ Checks whether the custom config location has been set. """
        return self.custom_config_dir is not None

    def spill_the_beans(self) -> Optional[Path]:
        """ Returns custom config path if set, else None. """
        return self.custom_config_dir

    def scribble_new_location(self, new_config_path: Path) -> None:
        """ Sets (or updates) the custom config path pointer. """
        self.default_app_dir.mkdir(parents=True, exist_ok=True)
        with self.pointer_file.open('w') as f:
            json.dump({"custom_config_dir": str(new_config_path.resolve())}, f)
        object.__setattr__(self, 'custom_config_dir', new_config_path.resolve())

    def forget_custom_location(self) -> None:
        """ Removes the custom config pointer, reverting to default. """
        if self.pointer_file.exists():
            self.pointer_file.unlink()
        object.__setattr__(self, 'custom_config_dir', None)


__all__ = [
    'ConfigLocator'
]
