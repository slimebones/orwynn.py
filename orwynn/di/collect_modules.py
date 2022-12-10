import copy
from orwynn.base.model.model import Model
from orwynn.base.module.module import Module
from orwynn.base.module.root_module import RootModule
from orwynn.di.circular_dependency_error import CircularDependencyError
    

def collect_modules(
        root_module: RootModule
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
            "module {} occured twice in dependency chain {}"
            .format(
                init_module,
                # Init module is added second time to the chain for
                # error descriptiveness
                " -> ".join([str(x) for x in chain + [init_module]])
            )
        )
    chain.append(init_module)

    if not init_module in modules:
        if init_module not in modules:
            modules.append(init_module)
        if init_module.imports:
            if init_module in init_module.imports:
                raise CircularDependencyError(
                    "module {} imports self".format(init_module)
                )
            for m in init_module.imports:
                if isinstance(m, RootModule):
                    raise CircularDependencyError(
                        "{} imports root module".format(init_module)
                    )
                _traverse(m, modules, chain)

    # On blocking case remove recently added module since we don't want this
    # module to appear in other branch, e.g.:
    #   A -> B (blocking: call chain.pop())-> C; A -> B -> D -> C;
    # If C hadn't been removed at the first iteration, we would have got a
    # circular error.
    chain.pop()

    return modules