from orwynn.app.app_service import AppService
from orwynn.base.controller.controller import Controller
from orwynn.base.middleware.middleware import Middleware
from orwynn.base.module.module import Module
from orwynn.base.service.root_service import RootService
from orwynn.util.types.provider import Provider


class RootModule(Module):
    """Special module which rises above whole application structure.
    
    Root module can be defined only in one instance for the whole app. Only
    this module has the possibility to define RootServices through field
    `RootServices`.

    No other module can import the RootModule.

    Root module always has "/" route.

    Attributes:
        RootServices:
            List of RootServices to be initialized for the whole application.
            By default always have AppService initialized, but you still can
            add this like `RootServices=[AppService, ...]` for explicity.
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
    """
    def __init__(
        self,
        *,
        RootServices: list[type[RootService]] | None = None,
        Providers: list[Provider] | None = None,
        Controllers: list[type[Controller]] | None = None,
        Middleware: list[type[Middleware]] | None = None,
        imports: list["Module"] | None = None,
        exports: list[Provider] | None = None
    ) -> None:
        super().__init__(
            route="/",
            Providers=Providers,
            Controllers=Controllers,
            Middleware=Middleware,
            imports=imports,
            exports=exports
        )
        if RootServices:
            self.RootServices = RootServices
        else:
            self.RootServices = []
        if AppService not in self.RootServices:
            self.RootServices.append(AppService)