"""Common types in the framework.
"""
from pathlib import Path

# Represents resource location.
URI = str

# Representation of any source of data.
Source = URI | Path