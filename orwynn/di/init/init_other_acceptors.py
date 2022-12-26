import inspect

from orwynn.base.controller.Controller import Controller
from orwynn.base.controller.http_controller.HTTPController import \
    HTTPController
from orwynn.base.middleware.Middleware import Middleware
from orwynn.base.module.Module import Module
from orwynn.di.acceptor import Acceptor
from orwynn.di.DIContainer import DIContainer
from orwynn.di.provider import Provider
from orwynn.proxy.BootProxy import BootProxy
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
        module_covered_routes_for_middleware: list[str] = []

        for C in module.Controllers:
            validate(C, Controller)

            controller: Controller = C(
                **__collect_dependencies_for_acceptor(C, container)
            )
            container.add(
                controller
            )

            # Middleware should accept modules only from HTTPControllers
            if isinstance(C, HTTPController):
                module_covered_routes_for_middleware.append(web.join_routes(
                    module.route, controller.route
                ))

        for Mw in module.Middleware:
            validate(Mw, Middleware)
            container.add(
                Mw(
                    covered_routes=module_covered_routes_for_middleware,
                    **__collect_dependencies_for_acceptor(Mw, container)
                )
            )

        for EH in BootProxy.ie().ErrorHandlers:
            container.add(
                EH(**__collect_dependencies_for_acceptor(EH, container))
            )


def __collect_dependencies_for_acceptor(
    A: type[Acceptor],
    container: DIContainer
) -> dict[str, Provider]:
    result: dict[str, Provider] = {}

    for param in inspect.signature(A).parameters.values():
        if param.name == "covered_routes":
            continue

        # See collect_provider_dependencies.py::_get_parameters_for_provider
        if param.name in ["args", "kwargs"]:
            continue

        result[param.name] = container.find(param.annotation.__name__)

    return result
