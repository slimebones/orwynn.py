from orwynn import validation
from orwynn.boot.Boot import Boot
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.http.HttpController import HttpController
from orwynn.di.DiContainer import DiContainer
from orwynn.di.init.init_other_acceptors import init_other_acceptors
from orwynn.di.ProviderAvailabilityError import ProviderAvailabilityError
from orwynn.middleware.HttpMiddleware import HttpMiddleware
from orwynn.module.Module import Module
from orwynn.service.Service import Service
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

    class Mw1(HttpMiddleware):
        pass

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

