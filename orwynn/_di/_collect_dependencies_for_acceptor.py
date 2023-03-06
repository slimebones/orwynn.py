import inspect
from typing import Callable

from orwynn._di.check_availability import check_availability
from orwynn._di.DiContainer import DiContainer
from orwynn._di.DiObject import DiObject
from orwynn._di.Provider import Provider
from orwynn.base.middleware import Middleware
from orwynn.base.module import Module


def collect_dependencies_for_acceptor(
    acceptor_callable: Callable,
    container: DiContainer,
    acceptor_module: Module | None
) -> dict[str, Provider]:
    """
    Collects all dependencies for given acceptor.

    Note that availabily check won't be performed in any of two cases:
    - acceptor_module is None
    - acceptor_callable is not a class

    Args:
        acceptor_callable:
            Callable acceptor object to inspect.
        container:
            DI container to operate with.
        acceptor_module:
            Module to check dependencies availability from. If None, the
            availability check won't be performed.
    """
    result: dict[str, Provider] = {}
    for param in inspect.signature(acceptor_callable).parameters.values():
        # Skip special case for middleware
        if (
            param.name == "covered_routes"
            and inspect.isclass(acceptor_callable)
            and issubclass(acceptor_callable, Middleware)
        ):
            continue

        dependency: DiObject = container.find(param.annotation.__name__)
        result[param.name] = dependency

        if (
            acceptor_module is not None
            and inspect.isclass(acceptor_callable)
        ):
            check_availability(
                acceptor_callable,
                type(dependency),
                acceptor_module
            )

    return result
