"""List of classes an user can subclass from."""
from orwynn.src.BaseSubclassable import BaseSubclassable
from orwynn.src.controller.Controller import Controller
from orwynn.src.error.Error import Error
from orwynn.src.error.ExceptionHandler import ExceptionHandler
from orwynn.src.middleware.Middleware import Middleware
from orwynn.src.model.Model import Model
from orwynn.src.service.Service import Service

# Note that here listed the most basic classes. E.g. Config is not listed
# since it is a derivative from the Model and on the stage of DI
# it will be checked to find these more specific classes.
SUBCLASSABLES: list[BaseSubclassable] = [
    Service,
    Controller,
    Middleware,
    Model,
    Error,
    ExceptionHandler
]
