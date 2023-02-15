from orwynn.di.DiContainer import DiContainer
from orwynn.di.init.init_other_acceptors import init_other_acceptors
from orwynn.module.Module import Module
from tests.std.Assertion import Assertion


def test_std(
    std_di_container: DiContainer,
    std_modules: list[Module]
):
    init_other_acceptors(std_di_container, std_modules)

    for A in Assertion.COLLECTED_OTHER_ACCEPTORS:
        isinstance(std_di_container.find(A.__name__), A)
