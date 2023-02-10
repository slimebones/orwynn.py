"""List of classes an user can subclass from."""
from orwynn.app.ErrorHandler import ErrorHandler
from orwynn.BaseSubclassable import BaseSubclassable
from orwynn.controller.Controller import Controller
from orwynn.error.Error import Error
from orwynn.middleware.Middleware import Middleware
from orwynn.model.Model import Model
from orwynn.service.Service import Service

# Note that here listed the most basic classes. E.g. Config is not listed
# since it is a derivative from the Model and on the stage of DI
# it will be checked to find these more specific classes.
SUBCLASSABLES: list[BaseSubclassable] = [
    Service,
    Controller,
    Middleware,
    Model,
    Error,
    ErrorHandler
]
