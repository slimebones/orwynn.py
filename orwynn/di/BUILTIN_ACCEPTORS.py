from orwynn.controller.Controller import Controller
from orwynn.di.acceptor import Acceptor
from orwynn.di.BUILTIN_PROVIDERS import BUILTIN_PROVIDERS
from orwynn.error.catching.ErrorHandler import ErrorHandler
from orwynn.middleware.Middleware import Middleware

"""List of builtin classes are able to accept Providers.
"""
BUILTIN_ACCEPTORS: list[type[Acceptor]] = [
    # All Providers are Acceptors at the same time
    *BUILTIN_PROVIDERS,
    Controller,
    Middleware,
    ErrorHandler
]
