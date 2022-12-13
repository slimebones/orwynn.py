from pytest import fixture
from orwynn.app.app_service import AppService

from orwynn.base.module.module import Module
from orwynn.di.collecting.collect_modules import collect_modules
from orwynn.di.collecting.collect_providers_dependencies import \
    collect_providers_dependencies
from orwynn.di.di_object.di_container import DIContainer
from orwynn.di.init.traverse_initializing_providers import \
    traverse_initializing_providers
from tests.std import Assertion


@fixture
def twice_occurence_struct() -> Module:
    m1 = Module(route="/m1")
    m2 = Module(route="/m2", imports=[m1])

    m1.imports.append(m2)

    rm = Module(
        route="/",
        imports=[m1]
    )

    return rm


def test_std(std_struct: Module):
    container: DIContainer = traverse_initializing_providers(
        collect_providers_dependencies(
            collect_modules(std_struct),
            [AppService]
        )
    )

    for P in Assertion.COLLECTED_PROVIDERS:
        isinstance(container.find(P.__name__), P)
