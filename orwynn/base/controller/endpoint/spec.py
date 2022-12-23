import functools
from typing import Callable
from orwynn.base.controller.endpoint.EndpointSpec import EndpointSpec
from orwynn.proxy.SpecsProxy import SpecsProxy


def spec(
    spec: EndpointSpec
) -> Callable:
    """Attaches spec for endpoint.
    """
    def wrapper(fn: Callable):
        @functools.wraps(fn)
        def inner(*args, **kwargs) -> Callable:
            return fn(*args, **kwargs)

        SpecsProxy.ie().add(fn, spec)

        return inner

    return wrapper
