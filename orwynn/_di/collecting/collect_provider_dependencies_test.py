import inspect

from pytest import fixture

from orwynn.config.Config import Config
from orwynn._di.collecting.collect_provider_dependencies import (
    ProviderDependenciesMap,
    collect_provider_dependencies,
)
from orwynn._di.collecting.ModuleCollector import ModuleCollector
from orwynn.internal.provider.is_provider import is_provider
from orwynn._di.Provider import Provider
from orwynn.base.module._Module import Module
from tests.std.Assertion import Assertion


@fixture
def std_provider_dependencies_map(
    std_modules: list[Module]
) -> ProviderDependenciesMap:
    return collect_provider_dependencies(std_modules)


def test_std(std_struct: Module):
    metamap: ProviderDependenciesMap = collect_provider_dependencies(
        ModuleCollector(std_struct).collected_modules
    )

    # Order doesn't matter
    assert set(metamap.Providers) == set(Assertion.COLLECTED_PROVIDERS)

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
