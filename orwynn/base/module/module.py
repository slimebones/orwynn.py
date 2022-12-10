from typing import Self
from orwynn.base.controller.controller import Controller
from orwynn.base.middleware.middleware import Middleware

from orwynn.util.types.provider import Provider


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
        /,
        route: str,
        Providers: list[Provider] = [],
        Controllers: list[type[Controller]] = [],
        Middleware: list[type[Middleware]] = [],
        imports: list["Module"] = [],
        exports: list[Provider] = []
    ) -> None:
        super().__init__()

        self.route = route
        self.Providers = Providers
        self.Controllers = Controllers
        self.Middleware = Middleware
        self.imports = imports
        self.exports = exports

    def __repr__(self) -> str:
        return "<{} \"{}\" at {}>".format(
            self.__class__.__name__,
            self.route,
            hex(id(self))
        )
