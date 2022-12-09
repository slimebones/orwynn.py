from typing import Self
from orwynn.src.base.controller.controller import Controller
from orwynn.src.base.middleware.middleware import Middleware

from orwynn.src.util.types.provider import Provider


class Module:
    """Provides metadata to organize the application structure.
    
    Attributes:
        Providers:
            List of Providers to be initialized and shared at least across this
            module.
        Controllers:
            List of Controllers to be initialized for this module.
        Middleware:
            List of Middleware classes applied to all module' controllers.
        imports:
            List of imported modules to use their exported providers in this
            module.
        exports:
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
        Providers: list[Provider] = [],
        Controllers: list[type[Controller]] = [],
        Middleware: list[type[Middleware]] = [],
        imports: list["Module"] = [],
        exports: list[Provider] = []
    ) -> None:
        super().__init__()
        self.Providers = Providers
        self.Controllers = Controllers
        self.Middleware = Middleware
        self.imports = imports
        self.exports = exports
