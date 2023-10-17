"""Common types.
"""
from typing import Any, Callable, Coroutine, TypeVar

T = TypeVar("T")

CommonType = TypeVar("CommonType")
Class = TypeVar("Class", bound=type)
DecoratedCallable = TypeVar("DecoratedCallable", bound=Callable[..., Any])

Timestamp = float
Delta = float

CashOperator = str
"""
Special string literal starts with dollar sign `$` which holds a special
meaning to the acceptor logic.
"""

AnyCoro = Coroutine[Any, Any, Any]
