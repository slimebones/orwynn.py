"""Module with test structures.

Word "struct" used to refer to root module returned for the sake of
descriptiveness - e.g. for fixtures like "self_importing_module_struct" to
annotate that this root module has been built with some modules using self
importing.
"""
from pytest import fixture

from orwynn.base.module.module import Module
from tests.std.root_module import root_module as std_root_module


@fixture
def std_struct() -> Module:
    # Some predefined configuration for testing
    return std_root_module


@fixture
def self_importing_module_struct() -> Module:
    m1 = Module(route="/m1")
    m1._imports.append(m1)

    return Module(
        route="/",
        imports=[m1]
    )


@fixture
def circular_module_struct() -> Module:
    m1 = Module(route="/m1")
    m2 = Module(route="/m2", imports=[m1])

    m1._imports.append(m2)

    rm = Module(
        route="/",
        imports=[m1]
    )

    return rm


@fixture
def long_circular_module_struct() -> Module:
    m1 = Module(route="/m1")
    m2 = Module(route="/m2", imports=[m1])
    m3 = Module(route="/m3", imports=[m2])
    m4 = Module(route="/m4", imports=[m3])

    m1._imports.append(m4)

    rm = Module(
        route="/",
        imports=[m1]
    )

    return rm
