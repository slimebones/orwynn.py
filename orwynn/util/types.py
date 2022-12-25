"""Common types.
"""
from typing import Any, Callable, TypeVar


Class = TypeVar("Class", bound=type)
DecoratedCallable = TypeVar("DecoratedCallable", bound=Callable[..., Any])
