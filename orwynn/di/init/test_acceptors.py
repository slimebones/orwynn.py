import pytest

from orwynn.base.module import Module
from orwynn.base.service import Service
from orwynn.boot.boot import Boot
from orwynn.di.container import DiContainer
from orwynn.di.errors import ProviderAvailabilityError
from orwynn.di.init.acceptors import init_other_acceptors
from orwynn.http import Endpoint, HttpController, HttpMiddleware
from orwynn.utils import validation
from tests.std.assertion import Assertion


@pytest.mark.asyncio
async def test_std(
    std_di_container: DiContainer,
    std_modules: list[Module]
):
    init_other_acceptors(std_di_container, std_modules)

    for A in Assertion.CollectedOtherAcceptors:
        isinstance(std_di_container.find(A.__name__), A)


@pytest.mark.asyncio
async def test_controller_dependency_unavailability():
    """
    Controller shouldn't be allowed to request unavailable modules.
    """
    class UnavailableService(Service):
        pass

    class Ctrl1(HttpController):
        Route = "/"
        Endpoints = [
            Endpoint(method="get")
        ]

        def __init__(self, sv: UnavailableService) -> None:
            super().__init__()

        def get(self) -> dict:
            return {}

    key_module: Module = Module("/key", Controllers=[Ctrl1])
    unavailable_module: Module = Module(Providers=[UnavailableService])

    await validation.expect_async(
        Boot.create(
            root_module=Module("/", imports=[key_module, unavailable_module])
        ),
        ProviderAvailabilityError
    )


@pytest.mark.asyncio
async def test_middleware_dependency_unavailability():
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

    await validation.expect_async(
        Boot.create(
            root_module=Module("/", imports=[key_module, unavailable_module])
        ),
        ProviderAvailabilityError
    )


@pytest.mark.asyncio
async def test_unavailability_imported_but_not_exported():
    """
    Check that a provider is not available if it's not exported from an
    imported module
    """
    class UnavailableService(Service):
        pass

    class Ctrl1(HttpController):
        Route = "/"
        Endpoints = [
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

    await validation.expect_async(
        Boot.create(
            root_module=Module("/", imports=[key_module, unavailable_module])
        ),
        ProviderAvailabilityError
    )
