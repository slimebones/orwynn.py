import copy
from types import NoneType
from typing import Self

from orwynn.base.controller import Controller
from orwynn.base.middleware import Middleware as MiddlewareClass
from orwynn.base.module.errors import (
    CircularDependencyError,
    EmptyRouteError,
    FrameworkServiceModuleReferenceError,
)
from orwynn.base.service.framework import FrameworkService
from orwynn.utils import validation
from orwynn.utils.validation import validate, validate_route


class Module:
    """Provides metadata to organize the application structure.

    Attributes:
        route (optional):
            All controllers defined under this module will
            operate under this route. By default the module has no route and
            hence cannot accept any controllers and middlewares.
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
        route: str | None = None,
        *,
        Providers: list[type] | None = None,
        Controllers: list[type[Controller]] | None = None,
        Middleware: list[type[MiddlewareClass]] | None = None,
        imports: list["Module"] | None = None,
        exports: list[type] | None = None
    ) -> None:
        super().__init__()
        validate(route, [str, NoneType])
        validate(Providers, [list, NoneType])
        validate(Controllers, [list, NoneType])
        validate(Middleware, [list, NoneType])
        validate(imports, [list, NoneType])
        validate(exports, [list, NoneType])

        self.__route: str | None
        if route is None:
            self.__route = route

            # Module without route cannot accept Controller and Middleware
            if Controllers is not None:
                raise ValueError(
                    f"module {self} has not route and cannot accept"
                    " controllers"
                )
            elif Middleware is not None:
                raise ValueError(
                    f"module {self} has not route and cannot accept"
                    " middleware"
                )
        else:
            self.__route = self.__parse_route(route)

        self._Providers: list[type] = self._parse_providers(
            Providers
        )
        self._Controllers: list[type[Controller]] = self._parse_controllers(
            Controllers
        )
        self._Middleware: list[type[MiddlewareClass]] = \
            self._parse_middleware(Middleware)
        self._imports: list["Module"] = self._parse_imports(imports)

        # Validate and assign exports
        if not exports:
            exports = []
        self._exports: list[type] = exports

    def __repr__(self) -> str:
        return "<{} \"{}\" at {}>".format(
            self.__class__.__name__,
            self.route or "no-route",
            hex(id(self))
        )

    @property
    def route(self) -> str | None:
        return self.__route

    @property
    def Providers(self) -> list[type]:
        return copy.copy(self._Providers)

    @property
    def Controllers(self) -> list[type[Controller]]:
        return copy.copy(self._Controllers)

    @property
    def Middleware(self) -> list[type[MiddlewareClass]]:
        return copy.copy(self._Middleware)

    @property
    def imports(self) -> list["Module"]:
        return copy.copy(self._imports)

    @property
    def exports(self) -> list[type]:
        return copy.copy(self._exports)

    @staticmethod
    def __parse_route(route: str) -> str:
        if route:
            validate_route(route)
        else:
            raise EmptyRouteError()

        return route

    def _fw_add_provider_or_skip(self, P: type) -> None:
        if P not in self._Providers:
            self._Providers.append(P)

    def _fw_add_controller_or_skip(self, C: type[Controller]) -> None:
        validate(C, Controller)
        if C not in self._Controllers:
            self._Controllers.append(C)

    def _fw_add_middleware_or_skip(self, Mw: type[MiddlewareClass]) -> None:
        validate(Mw, MiddlewareClass)
        if Mw not in self._Middleware:
            self._Middleware.append(Mw)

    def _fw_add_imports(self, *modules: Self) -> None:
        """Adds imported modules.

        Generally used to add global imports.
        """
        for module in modules:
            validation.validate(module, Module)
            if module in self._imports:
                raise CircularDependencyError(
                    f"module {module} has been already added to containing"
                    f" module {self}"
                )
            self._imports.append(module)

    def _parse_providers(
        self,
        Providers: list[type] | None
    ) -> list[type]:
        res: list[type]

        if Providers:
            for P in Providers:
                if issubclass(P, FrameworkService):
                    raise FrameworkServiceModuleReferenceError(
                        f"a framework service {P} cannot be referenced in"
                        f" the module {self}"
                    )
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
                # Rest validation done by controller itself
            res = Controllers
        else:
            res = []

        return res

    @staticmethod
    def _parse_middleware(
        Middleware_: list[type[MiddlewareClass]] | None
    ) -> list[type[MiddlewareClass]]:
        res: list[type[MiddlewareClass]]

        if Middleware_:
            for M in Middleware_:
                validate(M, MiddlewareClass)
            res = Middleware_
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
