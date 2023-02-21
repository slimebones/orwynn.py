from orwynn.src.controller.Controller import Controller
from orwynn.src.di.acceptor import Acceptor
from orwynn.src.di.BUILTIN_PROVIDERS import BUILTIN_PROVIDERS
from orwynn.src.error.ExceptionHandler import ExceptionHandler
from orwynn.src.middleware.Middleware import Middleware

"""List of builtin classes are able to accept Providers.
"""
BUILTIN_ACCEPTORS: list[type[Acceptor]] = [
    # All Providers are Acceptors at the same time
    *BUILTIN_PROVIDERS,
    Controller,
    Middleware,
    ExceptionHandler
]
