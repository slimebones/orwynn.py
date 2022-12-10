from orwynn.base.model.model import Model
from orwynn.base.module.module import Module
from orwynn.base.module.root_module import RootModule
from orwynn.di.circular_dependency_error import CircularDependencyError


def _traverse(
    init_module: Module,
    modules: list[Module],
    chain: list[Module]
) -> list[Module]:
    # Just recursively collects all modules, but memorizes every module
    # traversed to find circular dependency errors.

    if init_module in chain:
        raise CircularDependencyError(
            "module {} occured twice in dependency chain {}"
            .format(
                init_module,
                # Init module is added second time to the chain for
                # error descriptiveness
                " -> ".join([str(x) for x in chain + [init_module]])
            )
        )
    chain.append(init_module)

    if init_module in modules:
        return modules
    else:
        if init_module not in modules:
            modules.append(init_module)
        if init_module.imports:
            if init_module in init_module.imports:
                raise CircularDependencyError(
                    "module {} imports self".format(init_module)
                )
            for m in init_module.imports:
                _traverse(m, modules, chain)

    return modules
    


def collect_modules(
        root_module: RootModule
    ) -> list[Module]:
    """Collects all modules starting from root module."""
    modules: list[Module] = _traverse(root_module, [], []) 

    return modules