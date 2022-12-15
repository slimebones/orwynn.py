from orwynn.base.module.module import Module
from orwynn.di.circular_dependency_error import CircularDependencyError
from orwynn.util.fmt import format_chain


def collect_modules(
    root_module: Module
) -> list[Module]:
    """Collects all modules starting from root module.

    What is checked:
    - Dependency circular errors for modules
    - Modules self imports
    - Imports of RootModule

    Args:
        root_module:
            Root module of the application.

    Returns:
        List of modules collected.
    """
    modules: list[Module] = _traverse(root_module, [], [])

    return modules


def _traverse(
    init_module: Module,
    modules: list[Module],
    chain: list[Module]
) -> list[Module]:
    # Just recursively collects all modules, but memorizes every module
    # traversed to find circular dependency errors.

    if init_module in chain:
        raise CircularDependencyError(
            "{} occured twice in dependency chain {}"
            .format(
                init_module,
                # Failed module is added second time to the chain for
                # error descriptiveness
                format_chain(chain + [init_module])
            )
        )
    chain.append(init_module)

    if init_module not in modules:
        if init_module not in modules:
            modules.append(init_module)
        if init_module._imports:
            if init_module in init_module._imports:
                raise CircularDependencyError(
                    "{} imports self".format(init_module)
                )
            for m in init_module._imports:
                _traverse(m, modules, chain)

    # On blocking case remove recently added module since we don't want this
    # module to appear in other branch, e.g.:
    #   A -> B (blocking: call chain.pop())-> C; A -> B -> D -> C;
    # If C hadn't been removed at the first iteration, we would have got a
    # circular error.
    chain.pop()

    return modules
