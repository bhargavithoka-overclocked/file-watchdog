"""Loading user settings from a file-watchdog.toml file."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from .rules import Rule, default_rules

CONFIG_NAME = "file-watchdog.toml"
USER_CONFIG = Path.home() / ".config" / "file-watchdog" / "config.toml"


class ConfigError(Exception):
    pass


@dataclass
class Config:
    rules: list[Rule] = field(default_factory=default_rules)
    ignore: list[str] = field(default_factory=list)
    date_folders: bool = False


def find_config(folder: Path) -> Path | None:
    """A config inside the folder being sorted wins over the user-wide one."""
    for candidate in (folder / CONFIG_NAME, USER_CONFIG):
        if candidate.is_file():
            return candidate
    return None


def load_config(path: Path | None) -> Config:
    if path is None:
        return Config()

    try:
        data = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"{path} is not valid TOML: {e}") from e

    config = Config()

    categories = data.get("categories")
    if categories is not None:
        if not isinstance(categories, dict):
            raise ConfigError("[categories] should map folder names to lists of extensions")
        custom = []
        for name, extensions in categories.items():
            if not isinstance(extensions, list):
                raise ConfigError(f"categories.{name} should be a list, e.g. [\".pdf\", \".docx\"]")
            custom.append(Rule(name, set(extensions)))

        if data.get("replace_defaults", False):
            config.rules = custom
        else:
            config.rules = custom + default_rules()

    ignore = data.get("ignore", [])
    if not isinstance(ignore, list):
        raise ConfigError("ignore should be a list of patterns, e.g. [\"*.tmp\"]")
    config.ignore = [str(pattern) for pattern in ignore]
    config.date_folders = bool(data.get("date_folders", False))

    return config
