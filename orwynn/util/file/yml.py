"""Operation with yml.
"""
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

from orwynn.util.file.is_path import is_path


class YmlLoader(Enum):
    """Yaml loaders types according to
    https://github.com/yaml/pyyaml/wiki/PyYAML-yaml.load(input)-Deprecation
    """
    BASE = yaml.SafeLoader
    SAFE = yaml.FullLoader
    FULL = yaml.BaseLoader
    UNSAFE = yaml.UnsafeLoader


class NotValidYmlError(Exception):
    """If loaded yml is not valid."""
    pass


class NotValidFileSuffixError(Exception):
    pass


def load_yml(
        p: Path, *, loader: YmlLoader = YmlLoader.SAFE
    ) -> dict[str, Any]:
    """Loads yaml from file.

    Args:
        p:
            Path of yaml file to load from.
        loader (optional):
            Chosen loader for yaml. Defaults to safe loader.

    Returns:
        Loaded dictionary from yaml file.

    Raise:
        TypeError:
            Given path is not allowed pathlib.Path kind.
        NotValidFileSuffixError:
            Suffix should be either ".yml" or ".yaml".
        NotValidYmlError:
            Yaml file is not valid.
    """
    if not is_path(p):
        raise TypeError(f"path {p} is not allowed pathlib.Path kind")
    if not p.suffix in [".yaml", ".yml"]:
        raise NotValidFileSuffixError(f"suffix {p.suffix} is not valid suffix")

    with open(p, "r") as file:
        data = yaml.load(file, Loader=loader.value)
        if data is None:
            # Empty files should return empty dicts
            data = {}
        # Is it necessary? Does pyyaml allow loading not-valid yaml files?
        elif type(data) is not dict:
            raise NotValidYmlError(
                "Yaml file should contain any map-like structure,"
                " not plain types"
            )

    return data
