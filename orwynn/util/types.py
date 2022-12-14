"""Common types in the framework.
"""
from pathlib import Path
from typing import Literal

# Represents resource location.
URI = str

# Representation of any source of data.
# "boot" value means that config will be populated by Boot worker.
Source = URI | Path | Literal["boot"]
