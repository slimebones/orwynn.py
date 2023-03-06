"""List of classes an user can subclass from."""
from orwynn.base.controller._Controller import Controller
from orwynn.base.exchandler._ExceptionHandler import ExceptionHandler
from orwynn.base.middleware import Middleware
from orwynn.base.model._Model import Model
from orwynn.base.service._Service import Service
from orwynn.util.BaseSubclassable import BaseSubclassable

# Note that here listed the most basic classes. E.g. Config is not listed
# since it is a derivative from the Model and on the stage of DI
# it will be checked to find these more specific classes.
SUBCLASSABLES: list[BaseSubclassable] = [
    Service,
    Controller,
    Middleware,
    Model,
    ExceptionHandler
]
