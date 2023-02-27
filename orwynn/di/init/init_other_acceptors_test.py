from orwynn.util import validation
from orwynn.boot._Boot import Boot
from orwynn.base.controller.endpoint.Endpoint import Endpoint
from orwynn.base.controller.http.HttpController import HttpController
from orwynn.di.DiContainer import DiContainer
from orwynn.di.init.init_other_acceptors import init_other_acceptors
from orwynn.di.ProviderAvailabilityError import ProviderAvailabilityError
from orwynn.middleware.HttpMiddleware import HttpMiddleware
from orwynn.base.module.Module import Module
from orwynn.base.service.Service import Service
from tests.std.Assertion import Assertion


def test_std(
    std_di_container: DiContainer,
    std_modules: list[Module]
):
    init_other_acceptors(std_di_container, std_modules)

    for A in Assertion.COLLECTED_OTHER_ACCEPTORS:
        isinstance(std_di_container.find(A.__name__), A)


def test_controller_dependency_unavailability():
    """
    Controller shouldn't be allowed to request unavailable modules.
    """
    class UnavailableService(Service):
        pass

    class Ctrl1(HttpController):
        ROUTE = "/"
        ENDPOINTS = [
            Endpoint(method="get")
        ]

        def __init__(self, sv: UnavailableService) -> None:
            super().__init__()

        def get(self) -> dict:
            return {}

    key_module: Module = Module("/key", Controllers=[Ctrl1])
    unavailable_module: Module = Module(Providers=[UnavailableService])

    validation.expect(
        Boot,
        ProviderAvailabilityError,
        root_module=Module("/", imports=[key_module, unavailable_module])
    )


def test_middleware_dependency_unavailability():
    """
    Middleware shouldn't be allowed to request unavailable modules.
    """
    class UnavailableService(Service):
        pass

    class Mw1(HttpMiddleware):
        def __init__(
            self, covered_routes: list[str], sv: UnavailableService
        ) -> None:
            super().__init__(covered_routes)

    key_module: Module = Module("/key", Middleware=[Mw1])
    unavailable_module: Module = Module(Providers=[UnavailableService])

    validation.expect(
        Boot,
        ProviderAvailabilityError,
        root_module=Module("/", imports=[key_module, unavailable_module])
    )


def test_unavailability_imported_but_not_exported():
    """
    Check that a provider is not available if it's not exported from an
    imported module
    """
    class UnavailableService(Service):
        pass

    class Ctrl1(HttpController):
        ROUTE = "/"
        ENDPOINTS = [
            Endpoint(method="get")
        ]

        def __init__(self, sv: UnavailableService) -> None:
            super().__init__()

        def get(self) -> dict:
            return {}

    unavailable_module: Module = Module(Providers=[UnavailableService])
    key_module: Module = Module(
        "/key", Controllers=[Ctrl1], imports=[unavailable_module]
    )

    validation.expect(
        Boot,
        ProviderAvailabilityError,
        root_module=Module("/", imports=[key_module, unavailable_module])
    )
