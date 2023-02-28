from orwynn._di.Acceptor import Acceptor
from orwynn._di.BUILTIN_PROVIDERS import BUILTIN_PROVIDERS
from orwynn.base.controller._Controller import Controller
from orwynn.base.exchandler._ExceptionHandler import ExceptionHandler
from orwynn.base.middleware import Middleware

"""List of builtin classes are able to accept Providers.
"""
BUILTIN_ACCEPTORS: list[type[Acceptor]] = [
    # All Providers are Acceptors at the same time
    *BUILTIN_PROVIDERS,
    Controller,
    Middleware,
    ExceptionHandler
]
