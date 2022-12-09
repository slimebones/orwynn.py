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

    Attributes:
        RootServices:
            List of RootServices to be initialized for the whole application.
            Though it's not necessary, it's recommended that list of root
            services contain AppService for explicity.
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
    """
    def __init__(
        self,
        /,
        RootServices: list[type[RootService]] = [],
        Providers: list[Provider] = [], 
        Controllers: list[type[Controller]] = [],
        Middleware: list[type[Middleware]] = [], 
        imports: list[Module] = [], 
        exports: list[Provider] = []
    ) -> None:
        super().__init__(Providers, Controllers, Middleware, imports, exports)
        self.RootServices = RootServices
        if AppService not in self.RootServices:
            self.RootServices.append(AppService)
