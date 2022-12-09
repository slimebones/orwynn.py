from orwynn.src.base.model.model import Model
from orwynn.src.base.module.module import Module
from orwynn.src.base.module.root_module import RootModule
from orwynn.src.di.circular_dependency_error import CircularDependencyError


def _traverse(
    init_module: Module,
    modules: list[Module],
    chain: list[Module]
) -> list[Module]:
    # Just recursively collects all modules, but memorizes every module
    # traversed to find circular dependency errors.

    if init_module in chain:
        raise CircularDependencyError(
            "Module {} occured twice in dependency chain {}"
            .format(init_module, " -> ".join([str(x) for x in chain]))
        )
    chain.append(init_module)

    if init_module in modules:
        return modules
    else:
        if init_module.imports:
            if init_module in init_module.imports:
                raise CircularDependencyError(
                    "Module {} imports self".format(init_module)
                )
            for m in init_module.imports:
                _traverse(m, modules, chain)
        else:
            if init_module not in modules:
                modules.append(init_module)

    return modules
    


def collect_modules(
        root_module: RootModule
    ) -> list[Module]:
    """Collects all modules starting from root module."""
    modules: list[Module] = _traverse(root_module, [], []) 

    return modules