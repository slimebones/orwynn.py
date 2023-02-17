import inspect

from orwynn import web
from orwynn.controller.Controller import Controller
from orwynn.controller.http.HttpController import HttpController
from orwynn.controller.websocket.WebsocketController import WebsocketController
from orwynn.di.acceptor import Acceptor
from orwynn.di.DiContainer import DiContainer
from orwynn.di.Provider import Provider
from orwynn.middleware.HttpMiddleware import HttpMiddleware
from orwynn.middleware.Middleware import Middleware
from orwynn.middleware.WebsocketMiddleware import WebsocketMiddleware
from orwynn.model.Model import Model
from orwynn.module.Module import Module
from orwynn.proxy.BootProxy import BootProxy
from orwynn.validation import validate


class _CoveredRoutes(Model):
    http: list[str]
    websocket: list[str]


def init_other_acceptors(
    container: DiContainer,
    modules: list[Module]
) -> None:
    """Populates DI container with initialized non-provider acceptors.

    Attributes:
        container:
            DI container.
        modules:
            List of modules to collect acceptors from.
    """
    __init_modules(container, modules)


def __collect_dependencies_for_acceptor(
    A: type[Acceptor],
    container: DiContainer
) -> dict[str, Provider]:
    result: dict[str, Provider] = {}

    for param in inspect.signature(A).parameters.values():
        if (
            param.name == "covered_routes"
        ):
            continue

        # See collect_provider_dependencies.py::_get_parameters_for_provider
        if param.name in ["args", "kwargs"]:
            continue

        result[param.name] = container.find(param.annotation.__name__)

    return result


def __init_modules(
    container: DiContainer,
    modules: list[Module]
) -> None:
    for module in modules:
        covered_routes: _CoveredRoutes = __init_controllers(container, module)

        # FIXME: Move middleware and error handlers to separate functions
        for Mw in module.Middleware:
            validate(Mw, Middleware)

            if module.route is None:
                raise ValueError(
                    f"module {module} has not route and shouldn't have added"
                    " any controllers or middleware"
                )

            final_covered_routes: list[str]
            if issubclass(Mw, HttpMiddleware):
                final_covered_routes = covered_routes.http
            elif issubclass(Mw, WebsocketMiddleware):
                final_covered_routes = covered_routes.websocket
            elif type(Mw) is Middleware:
                raise TypeError(
                    f"abstract Middleware instance {Mw} is disallowed"
                )
            else:
                raise TypeError(
                    f"unrecognized middleware {Mw}"
                )

            container.add(
                Mw(
                    covered_routes=final_covered_routes,
                    **__collect_dependencies_for_acceptor(Mw, container)
                )
            )

        for Eh in BootProxy.ie().ErrorHandlers:
            container.add(
                Eh(**__collect_dependencies_for_acceptor(Eh, container))
            )


def __init_controllers(
    container: DiContainer,
    module: Module
) -> _CoveredRoutes:
    http_covered_routes: list[str] = []
    websocket_covered_routes: list[str] = []

    for C in module.Controllers:
        validate(C, Controller)

        if module.route is None:
            raise ValueError(
                f"module {module} has not route and shouldn't have added"
                " any controllers or middleware"
            )

        controller: Controller = C(
            **__collect_dependencies_for_acceptor(C, container)
        )
        container.add(
            controller
        )

        final_route: str = web.join_routes(
            module.route, controller.route
        )
        if issubclass(C, HttpController):
            http_covered_routes.append(final_route)
        elif issubclass(C, WebsocketController):
            # The final route should be duplicated for each controller's
            # event handler, since they are forming the controller's
            # subroute system
            for subroute in C.get_handler_subroutes():
                websocket_covered_routes.append(
                    web.join_routes(final_route, subroute)
                )
        elif type(C) is Controller:
            raise TypeError(
                f"abstract Controller instance {C} is disallowed"
            )
        else:
            raise TypeError(
                f"unrecognized controller {C}"
            )

    return _CoveredRoutes(
        http=http_covered_routes,
        websocket=websocket_covered_routes
    )
