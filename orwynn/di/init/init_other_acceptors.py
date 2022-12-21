import inspect
from orwynn.base.controller.Controller import Controller
from orwynn.base.middleware._Middleware import Middleware
from orwynn.base.module.Module import Module
from orwynn.di.acceptor import Acceptor
from orwynn.di.DIContainer import DIContainer
from orwynn.di.provider import Provider
from orwynn.util import web
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
        module_covered_routes: list[str] = []

        for C in module.Controllers:
            validate(C, Controller)

            controller: Controller = C(
                *_collect_dependencies_for_acceptor(C, container)
            )
            container.add(
                controller
            )
            module_covered_routes.append(web.join_routes(
                module.route, controller.route
            ))

        for Mw in module.Middleware:
            validate(Mw, Middleware)
            container.add(
                Mw(
                    covered_routes=module_covered_routes,
                    *_collect_dependencies_for_acceptor(Mw, container)
                )
            )


def _collect_dependencies_for_acceptor(
    A: type[Acceptor],
    container: DIContainer
) -> list[Provider]:
    result: list[Provider] = []

    for param in inspect.signature(A).parameters.values():
        if param.name == "covered_routes":
            continue

        # See collect_provider_dependencies.py::_get_parameters_for_provider
        if param.name in ["args", "kwargs"]:
            continue

        result.append(container.find(param.annotation.__name__))

    return result
