from pathlib import Path
from orwynn.src.util.types.uri import URI


"""Representation of any source of data.
"""
Source = URI | Path
    