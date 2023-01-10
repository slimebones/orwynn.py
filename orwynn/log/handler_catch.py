from typing import Callable

from orwynn.log.reraise_catch import reraise_catch
from orwynn.web import Request


def handler_catch(fn: Callable):
    """Catch all errors passed to error handlers by logger."""
    def inner(request: Request, error: Exception, *args, **kwargs):
        reraise_catch(error)
        return fn(request, error, *args, **kwargs)
    return inner
