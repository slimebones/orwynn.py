
from orwynn.base.controller.controller import Controller
from orwynn.base.middleware import GlobalMiddlewareSetup, Middleware
from orwynn.base.model.model import Model
from orwynn.base.module.module import Module
from orwynn.di.collecting.acceptordependencies import (
    collect_dependencies_for_acceptor,
)
from orwynn.di.container import DiContainer
from orwynn.http import HttpController, HttpMiddleware
from orwynn.proxy.boot import BootProxy
from orwynn.utils import validation
from orwynn.utils.url import join_routes
from orwynn.utils.validation import validate
from orwynn.websocket import WebsocketController, WebsocketMiddleware


class __CoveredRoutes(Model):
    http: list[str]
    websocket: list[str]


__ModuleToCoveredRoutes = tuple[Module, __CoveredRoutes]


def init_other_acceptors(
    container: DiContainer,
    modules: list[Module],
    global_middleware: GlobalMiddlewareSetup | None = None
) -> None:
    """Populates DI container with initialized non-provider acceptors.

    Attributes:
        container:
            DI container.
        modules:
            List of modules to collect acceptors from.
        global_middleware (optional):
            Global middleware setup setting. None is initialized by default.
    """
    if global_middleware is None:
        global_middleware = {}
    __init_modules(container, modules, global_middleware)


def __init_modules(
    container: DiContainer,
    modules: list[Module],
    global_middleware: GlobalMiddlewareSetup
) -> None:
    # Init global middleware first, and then normally module's defined.
    __init_middleware(
        container=container,
        source=global_middleware
    )

    _init_all_error_handlers(container)

    for module in modules:
        covered_routes: __CoveredRoutes = __init_controllers(container, module)
        __init_middleware(
            container=container,
            source=(module, covered_routes)
        )


def _init_all_error_handlers(
    container: DiContainer
) -> None:
    for Eh in BootProxy.ie().ErrorHandlers:
        container.add(
            Eh(**collect_dependencies_for_acceptor(
                Eh,
                container,
                None
            ))
        )


def __init_controllers(
    container: DiContainer,
    module: Module
) -> __CoveredRoutes:
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
            **collect_dependencies_for_acceptor(
                C,
                container,
                module
            )
        )
        final_route: str = join_routes(
            module.route, controller.route
        )

        container.add(
            controller
        )

        if issubclass(C, HttpController):
            http_covered_routes.append(final_route)
        elif issubclass(C, WebsocketController):
            # The final route should be duplicated for each controller's
            # event handler, since they are forming the controller's
            # subroute system
            for subroute in C.get_handler_subroutes():
                websocket_covered_routes.append(
                    join_routes(final_route, subroute)
                )
        elif type(C) is Controller:
            raise TypeError(
                f"abstract Controller instance {C} is disallowed"
            )
        else:
            raise TypeError(
                f"unrecognized controller {C}"
            )

    return __CoveredRoutes(
        http=http_covered_routes,
        websocket=websocket_covered_routes
    )


def __init_middleware(
    container: DiContainer,
    source: __ModuleToCoveredRoutes | GlobalMiddlewareSetup
) -> None:
    """
    Inits a middleware.

    Args:
        container:
        source:
            Module and it's covered routes or global middleware setting.
    """
    if isinstance(source, tuple):
        validation.validate_length(source, 2)
        __init_middleware_from_module(
            container=container,
            module=source[0],
            covered_routes=source[1]
        )
    elif isinstance(source, dict):
        __init_global_middleware(
            container=container,
            setup=source
        )
    else:
        raise TypeError(
            f"unrecognized source object {source}"
        )


def __init_global_middleware(
    container: DiContainer,
    setup: GlobalMiddlewareSetup
) -> None:
    for Middleware_, covered_routes_arr in setup.items():
        __register_middleware_in_container(
            container=container,
            Middleware_=Middleware_,
            covered_routes_arr=covered_routes_arr,
            # Omit the availability check
            module=None
        )


def __init_middleware_from_module(
    *,
    container: DiContainer,
    module: Module,
    covered_routes: __CoveredRoutes
) -> None:
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

        __register_middleware_in_container(
            container=container,
            Middleware_=Mw,
            covered_routes_arr=final_covered_routes,
            module=module
        )


def __register_middleware_in_container(
    *,
    container: DiContainer,
    Middleware_: type[Middleware],
    covered_routes_arr: list[str],
    module: Module | None
) -> None:
    """
    Adds a middleware to the container.

    Args:
        ...
        module:
            Module to check dependencies availability from. If None, all
            initialized dependencies will be available.
    """
    container.add(
        Middleware_(
            covered_routes=covered_routes_arr,
            **collect_dependencies_for_acceptor(
                Middleware_,
                container,
                module
            )
        )
    )
