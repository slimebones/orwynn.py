"""List of classes an user can subclass from."""
from orwynn.controller.controller import Controller
from orwynn.errorhandler.errorhandler import ErrorHandler
from orwynn.middleware import Middleware
from orwynn.model.model import Model
from orwynn.service.service import Service

# Note that here listed the most basic classes. E.g. Config is not listed
# since it is a derivative from the Model and on the stage of DI
# it will be checked to find these more specific classes.
SUBCLASSABLES: list[type] = [
    Service,
    Controller,
    Middleware,
    Model,
    ErrorHandler
]

ENVIRONS: set[str] = {
    "ORWYNN_MODE",
    "ORWYNN_ROOT_DIR",
    "ORWYNN_RC_PATH",
    "ORWYNN_IS_CATCH_LOGGING_ENABLED_IN_TESTS"
}
"""
All environment variables the framework supports.
"""
