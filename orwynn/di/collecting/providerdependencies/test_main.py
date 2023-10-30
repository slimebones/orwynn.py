import inspect

import pytest

from orwynn.base.config import Config
from orwynn.base.module import Module
from orwynn.di.collecting.modulecollector import ModuleCollector
from orwynn.di.collecting.providerdependencies.collect import (
    collect_provider_dependencies,
)
from orwynn.di.collecting.providerdependencies.map import (
    ProviderDependenciesMap,
)
from orwynn.di.isprovider import is_provider
from orwynn.di.provider import Provider
from orwynn.http.log.configs import LogHttpMiddlewareConfig
from orwynn.log import LogConfig
from tests.std.assertion import Assertion


@pytest.fixture
def std_provider_dependencies_map(
    std_modules: list[Module]
) -> ProviderDependenciesMap:
    return collect_provider_dependencies(std_modules)


def test_std(std_struct: Module):
    # TODO(ryzhovalex):
    #   Here we out of DI adding core providers, which is a duplicate
    #   operation. Need to consider better solutions.
    std_struct._fw_add_provider_or_skip(LogConfig)
    std_struct._fw_add_provider_or_skip(LogHttpMiddlewareConfig)

    metamap: ProviderDependenciesMap = collect_provider_dependencies(
        ModuleCollector(std_struct).collected_modules
    )

    # Order doesn't matter
    assert set(metamap.Providers) == set(Assertion.CollectedProviders)

    for P, dependencies in metamap.mapped_items:
        assertion_dependencies: list[type[Provider]] = []
        for inspect_parameter in inspect.signature(P).parameters.values():
            # Skip config's parseable parameters
            if (
                issubclass(P, Config)
                and (
                    not inspect.isclass(inspect_parameter.annotation)
                    or not is_provider(inspect_parameter.annotation)
                )
            ):
                continue
            if inspect_parameter.name in ["args", "kwargs"]:
                continue
            assertion_dependencies.append(inspect_parameter.annotation)
        assert dependencies == assertion_dependencies
