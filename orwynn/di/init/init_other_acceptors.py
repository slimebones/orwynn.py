import inspect
from orwynn.base.controller import Controller
from orwynn.base.module import Module
from orwynn.di.acceptor import Acceptor
from orwynn.di.di_container import DIContainer
from orwynn.di.provider import Provider
from orwynn.util.validation import validate


def init_other_acceptors(
    container: DIContainer,
    modules: list[Module]
) -> None:
    """Populates DI container with initialized non-provider acceptors.

    Attributes:
        container:
            DI container.
        modules:
            List of modules to collect acceptors from.
    """
    for module in modules:
        for C in module._Controllers:
            validate(C, Controller)
            container.add(
                C(
                    *_collect_dependencies_for_acceptor(C, container)
                )
            )

        for M in module._Middleware:
            validate(M, Controller)
            container.add(
                M(
                    *_collect_dependencies_for_acceptor(M, container)
                )
            )


def _collect_dependencies_for_acceptor(
    A: type[Acceptor],
    container: DIContainer
) -> list[Provider]:
    result: list[Provider] = []

    for param in inspect.signature(A).parameters.values():
        # See collect_provider_dependencies.py::_get_parameters_for_provider
        if param.name in ["args", "kwargs"]:
            continue

        result.append(container.find(param.annotation.__name__))

    return result
