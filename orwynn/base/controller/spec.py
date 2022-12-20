import functools
from typing import Callable
from orwynn.base.controller.EndpointSpec import EndpointSpec
from orwynn.base.controller.EndpointSpecsProxy import EndpointSpecsProxy


def spec(
    spec: EndpointSpec
) -> Callable:
    """Attaches spec for endpoint.
    """
    def wrapper(fn: Callable):
        @functools.wraps(fn)
        def inner(*args, **kwargs) -> Callable:
            return fn(*args, **kwargs)

        EndpointSpecsProxy.ie().add(fn, spec)

        return inner

    return wrapper
