import pytest_asyncio

from orwynn.base.module.module import Module
from orwynn.boot.boot import Boot
from orwynn.di.collecting.providerdependencies.map import (
    ProviderDependenciesMap,
)
from orwynn.di.container import DiContainer
from orwynn.di.init.providers import init_providers


@pytest_asyncio.fixture
async def std_di_container(
    std_struct: Module,
    std_provider_dependencies_map: ProviderDependenciesMap
) -> DiContainer:
    await Boot.create(std_struct)
    return init_providers(std_provider_dependencies_map)
