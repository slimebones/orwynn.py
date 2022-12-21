from typing import Callable
from orwynn.base.model.Model import Model


class ErrorHandler(Model):
    # Can be defined for builtin exceptions too
    E: type[Exception]
    handler: Callable
