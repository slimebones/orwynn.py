from types import NoneType
from orwynn.base.controller.controller import Controller
from orwynn.base.middleware.middleware import Middleware as MiddlewareClass

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
        Providers: list[Provider] | None = None,
        Controllers: list[type[Controller]] | None = None,
        Middleware: list[type[MiddlewareClass]] | None = None,
        imports: list["Module"] | None = None,
        exports: list[Provider] | None = None
    ) -> None:
        super().__init__()

        validate(route, str)
        validate(Providers, [list, NoneType])
        validate(Controllers, [list, NoneType])
        validate(Middleware, [list, NoneType])
        validate(imports, [list, NoneType])
        validate(exports, [list, NoneType])

        if route:
            self.route = route
        else:
            self.route = []
        if Providers:
            self.Providers = Providers
        else:
            self.Providers = []
        if Controllers:
            self.Controllers = Controllers
        else:
            self.Controllers = []
        if Middleware:
            self.Middleware = Middleware
        else:
            self.Middleware = []
        if imports:
            self.imports = imports
        else:
            self.imports = []
        if exports:
            self.exports = exports
        else:
            self.exports = []

    def __repr__(self) -> str:
        return "<{} \"{}\" at {}>".format(
            self.__class__.__name__,
            self.route,
            hex(id(self))
        )
