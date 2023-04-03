"""Operation with yml.
"""
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

from orwynn.utils.validation import validate


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
    validate(p, Path)

    if p.suffix.lower() not in [".yaml", ".yml"]:
        raise NotValidFileSuffixError(f"suffix {p.suffix} is not valid suffix")

    with open(p) as file:
        data = yaml.load(file, Loader=loader.value)  # noqa: S506
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
