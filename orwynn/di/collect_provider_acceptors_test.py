from pytest import fixture
from orwynn.base.module.root_module import RootModule
from orwynn.di.collect_modules import collect_modules
from orwynn.di.collect_provider_acceptors import (ProvidersAcceptorsMap,
                                                  collect_provider_acceptors)
from orwynn.util.types.provider import Provider
from tests.std import Assertion


@fixture
def twice_occurence_structure() -> RootModule:
    pass


def test_std(std_structure: RootModule):
    metamap: ProvidersAcceptorsMap = collect_provider_acceptors(
        collect_modules(std_structure)
    )

    assert metamap.Providers == Assertion.COLLECTED_PROVIDERS