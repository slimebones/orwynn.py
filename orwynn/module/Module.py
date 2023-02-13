import copy
from types import NoneType

from orwynn.app.EmptyRouteError import EmptyRouteError
from orwynn.controller.Controller import Controller
from orwynn.di.is_provider import is_provider
from orwynn.di.NotProviderError import NotProviderError
from orwynn.di.Provider import Provider
from orwynn.middleware.Middleware import Middleware as MiddlewareClass
from orwynn.module.framework_service_module_reference_error import (
    FrameworkServiceModuleReferenceError,
)
from orwynn.service.FrameworkService import FrameworkService
from orwynn.validation import validate, validate_route


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
        route: str,
        *,
        Providers: list[type[Provider]] | None = None,
        Controllers: list[type[Controller]] | None = None,
        Middleware: list[type[MiddlewareClass]] | None = None,
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

        self._route: str = self._parse_route(route)
        self._Providers: list[type[Provider]] = self._parse_providers(
            Providers
        )
        self._Controllers: list[type[Controller]] = self._parse_controllers(
            Controllers
        )
        self._Middleware: list[type[MiddlewareClass]] = \
            self._parse_middleware(Middleware)
        self._imports: list["Module"] = self._parse_imports(imports)
        # TODO: Add check if exports present in Providers
        self._exports: list[type[Provider]] = self._parse_providers(Providers)

    def __repr__(self) -> str:
        return "<{} \"{}\" at {}>".format(
            self.__class__.__name__,
            self.route,
            hex(id(self))
        )

    @property
    def route(self) -> str:
        return self._route

    @property
    def Providers(self) -> list[type[Provider]]:
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
    def exports(self) -> list[type[Provider]]:
        return copy.copy(self._exports)

    @staticmethod
    def _parse_route(route: str) -> str:
        if route:
            validate_route(route)
        else:
            raise EmptyRouteError()

        return route

    def add_provider_or_skip(self, P: type[Provider]) -> None:
        if not is_provider(P):
            raise TypeError("should receive provider")
        if P not in self._Providers:
            self._Providers.append(P)

    def add_controller_or_skip(self, C: type[Controller]) -> None:
        validate(C, Controller)
        if C not in self._Controllers:
            self._Controllers.append(C)

    def add_middleware_or_skip(self, Mw: type[MiddlewareClass]) -> None:
        validate(Mw, MiddlewareClass)
        if Mw not in self._Middleware:
            self._Middleware.append(Mw)

    def _parse_providers(
        self,
        Providers: list[type[Provider]] | None
    ) -> list[type[Provider]]:
        res: list[type[Provider]]

        if Providers:
            for P in Providers:
                if not is_provider(P):
                    raise NotProviderError(FailedClass=P)
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
        Middleware: list[type[MiddlewareClass]] | None
    ) -> list[type[MiddlewareClass]]:
        res: list[type[MiddlewareClass]]

        if Middleware:
            for Middleware_ in Middleware:
                validate(Middleware_, MiddlewareClass)
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
