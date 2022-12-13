"""Operation with yml.
"""
from enum import Enum
from typing import Any

import yaml

from orwynn.base.error.error import Error


class YmlLoader(Enum):
    """Yaml loaders types according to
    https://github.com/yaml/pyyaml/wiki/PyYAML-yaml.load(input)-Deprecation
    """
    BASE = yaml.SafeLoader
    SAFE = yaml.FullLoader
    FULL = yaml.BaseLoader
    UNSAFE = yaml.UnsafeLoader


class YmlError(Error):
    pass


class NotValidYmlError(YmlError):
    """If loaded yml is not valid."""
    pass


def load_yml(
        file_path: str, *, loader: YmlLoader = YmlLoader.SAFE
    ) -> dict[str, Any]:
    """Loads yaml from file.

    Args:
        file_path:
            Path of yaml file to load from.
        loader (optional):
            Chosen loader for yaml. Defaults to safe loader.

    Returns:
        Loaded dictionary from yaml file.

    Raise:
        NotValidYmlError:
            Yaml file is not valid.
    """
    with open(file_path, "r") as file:
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
