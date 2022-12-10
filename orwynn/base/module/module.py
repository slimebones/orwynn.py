import re
from types import NoneType
from typing import Any
from orwynn.app.empty_route_error import EmptyRouteError
from orwynn.app.incorrect_route_error import IncorrectRouteError
from orwynn.base.controller.controller import Controller
from orwynn.base.middleware import middleware
from orwynn.di.BUILTIN_PROVIDERS import BUILTIN_PROVIDERS
from orwynn.di.not_provider_error import NotProviderError

from orwynn.util.types.provider import Provider
from orwynn.util.validation import validate


class Module:
    """Provides metadata to organize the application structure.
    
    Attributes:
        route:
            All controllers defined under this module will
            operate under this route. Route cannot be "/" to be distinguishable
            from other modules.
        Providers (optional):
            List of Providers to be initialized and shared at least across this
            module.
        Controllers (optional):
            List of Controllers to be initialized for this module.
        Middleware (optional):
            List of Middleware classes applied to all module' controllers.
        imports (optional):
            List of imported modules to use their exported providers in this
            module.
        exports (optional):
            Sublist of providers that are provided by this module for other
            modules importing this module. It cannot contain provider not
            referenced in `providers` field.

    Usage:
    ```py
    # medieval_module.py

    medieval_module = Module(
        Providers=[KingService, KnightService, KingConfig],
        Controllers=[KingController, KnightController],
        Middleware=[BlessingMiddleware],
        imports=[castle_module],
        exports=[KingService, KingConfig]
    )
    ```
    """
    def __init__(
        self,
        *,
        route: str,
        Providers: list[type[Provider]] | None = None,
        Controllers: list[type[Controller]] | None = None,
        Middleware: list[type[middleware.Middleware]] | None = None,
        imports: list["Module"] | None = None,
        exports: list[type[Provider]] | None = None
    ) -> None:
        super().__init__()

        validate(route, str)
        validate(Providers, [list, NoneType])
        validate(Controllers, [list, NoneType])
        validate(Middleware, [list, NoneType])
        validate(imports, [list, NoneType])
        validate(exports, [list, NoneType])

        self.route: str = self._parse_route(route)
        self.Providers: list[type[Provider]] = self._parse_providers(Providers)
        self.Controllers: list[type[Controller]] = self._parse_controllers(
            Controllers
        )
        self.Middleware: list[type[middleware.Middleware]] = self._parse_middleware(
            Middleware
        )
        self.imports: list["Module"] = self._parse_imports(imports)
        self.exports: list[type[Provider]] = self._parse_providers(Providers)

    def __repr__(self) -> str:
        return "<{} \"{}\" at {}>".format(
            self.__class__.__name__,
            self.route,
            hex(id(self))
        )

    @staticmethod
    def _parse_route(route: str) -> str:
        if route:
            if not re.match(r"^\/(.+\/?)+$", route) and route != "/":
                raise IncorrectRouteError(failed_route=route)
        else:
            raise EmptyRouteError()

        return route

    @staticmethod
    def _parse_providers(
        Providers: list[type[Provider]] | None
    ) -> list[type[Provider]]:
        res: list[type[Provider]]
        is_found_in_builtins: bool

        if Providers:
            for Provider_ in Providers:
                is_found_in_builtins = False
                for BuiltinProvider in BUILTIN_PROVIDERS:
                    if isinstance(BuiltinProvider, Provider_):
                        is_found_in_builtins = True
                if is_found_in_builtins:
                    raise NotProviderError(FailedClass=Provider_) 
            res = Providers
        else:
            res = []

        return res

    @staticmethod
    def _parse_controllers(
        Controllers: list[type[Controller]] | None
    ) -> list[type[Controller]]:
        res: list[type[Controller]]

        if Controllers:
            for Controller_ in Controllers:
                validate(Controller_, Controller)
            res = Controllers
        else:
            res = []

        return res

    @staticmethod
    def _parse_middleware(
        Middleware: list[type[middleware.Middleware]] | None
    ) -> list[type[middleware.Middleware]]:
        res: list[type[middleware.Middleware]]

        if Middleware:
            for Middleware_ in Middleware:
                validate(Middleware_, middleware.Middleware)
            res = Middleware
        else:
            res = []

        return res

    @staticmethod
    def _parse_imports(
        imports: list["Module"] | None
    ) -> list["Module"]:
        res: list["Module"]

        if imports:
            for import_ in imports:
                validate(import_, Module)
            res = imports
        else:
            res = []

        return res
