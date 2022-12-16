"""Common types.
"""
from pathlib import Path

# Represents resource location.
URI = str

# Representation of any source of data.
# "boot" value means that config will be populated by Boot worker.
Source = URI | Path
