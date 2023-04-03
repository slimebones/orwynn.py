from orwynn.base.module import Module
from orwynn.base.module.errors import CircularDependencyError
from orwynn.utils import validation
from orwynn.utils.fmt import format_chain


class ModuleCollector:
    """Collects all modules starting from root module.

    What is checked:
    - Dependency circular errors for modules
    - Modules self imports
    - Imports of RootModule

    Attributes:
        root_module:
            Root module of the application.
        global_modules (optional):
            Modules to be imported globally for each encountered module.
            Empty by default
    """
    def __init__(
        self,
        root_module: Module,
        *,
        global_modules: list[Module] | None = None
    ) -> None:
        validation.validate(root_module, Module)
        if not global_modules:
            global_modules = []
        validation.validate_each(
            global_modules,
            Module,
            expected_sequence_type=list
        )

        self.__root_module: Module = root_module
        self.__global_modules: list[Module] = global_modules

        self.__collected_modules: list[Module] = []
        self.__chain: list[Module] = []
        # Start traversing from the root module
        self.__traverse(self.__root_module)

    @property
    def collected_modules(self) -> list[Module]:
        return self.__collected_modules.copy()

    def __traverse(
        self,
        init_module: Module
    ) -> None:
        # Just recursively collects all modules, but memorizes every module
        # traversed to find circular dependency errors.

        if init_module in self.__chain:
            raise CircularDependencyError(
                # Failed module is added second time to the chain for
                # error descriptiveness
                f"{init_module} occured twice in dependency chain"
                f" {format_chain(self.__chain + [init_module])}"
            )
        self.__chain.append(init_module)

        if init_module not in self.__collected_modules:
            self.__collected_modules.append(init_module)

            # Add all globally available modules to the current's module
            # imports, and only then continue to inspect the imports.
            #
            # But don't add global modules as imports to another global
            # modules :-)
            if init_module not in self.__global_modules:
                init_module._fw_add_imports(*self.__global_modules)

            if init_module._imports:
                if init_module in init_module._imports:
                    raise CircularDependencyError(
                        f"{init_module} imports self"
                    )
                for m in init_module._imports:
                    # And now start traversing but for an imported module
                    # recursively
                    self.__traverse(m)

        # On blocking case remove recently added module since we don't want
        # this module to appear in other branch, e.g.:
        #   A -> B (blocking: call chain.pop())-> C; A -> B -> D -> C;
        # If C hadn't been removed at the first iteration, we would have got a
        # circular error.
        self.__chain.pop()
