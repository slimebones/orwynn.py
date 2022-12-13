from orwynn.app.app_service import AppService
from orwynn.base.module.module import Module
from orwynn.base.worker.worker import Worker
from orwynn.di.di_error import DIError
from orwynn.di.di_object.di_container import DIContainer
from orwynn.di.di_object.di_object import DIObject
from orwynn.validation import validate


class DI(Worker):
    """Resolves Dependency-injection related tasks for an application.

    Only objects in categories Providers and Acceptors take part in DI. For now
    only objects from BUILTIN_PROVIDERS and BUILTIN_ACCEPTORS are considered.
    In future it might be possible to add custom providers or acceptors (maybe
    using class decorators) in addition to builtin ones.

    Stages of DI:
    - Build a dependency tree, collecting all objects and their requested
        injections
    - Make an order of initialization for dependencies
    - Initialize dependencies according to the order for each making
        appropriate injections

    How high in order dependency will be placed depends on:
    - Dependency's priority, see BUILTIN_PROVIDERS
    - Amount of other dependencies and their priorities:
    ```
    dep1 * dep1_priority + dep2 * dep2_priority + ... + dep_n * dep_n_priority
    ```
    - Amount of imports of other modules at the module, where considered
        dependency resides

    Attributes:
        root_module:
            Root module of the app.
    """
    def __init__(self, root_module: Module) -> None:
        super().__init__()
        validate(root_module, Module)

        # So here we have generally two stages of DI:
        #   1. Collecting (module "di/collecting")
        #   2. Initializing (module "di/init")

        self._container: DIContainer

    @property
    def app_service(self) -> AppService:
        app = self.find("app_service")
        if isinstance(app, AppService):
            return app
        else:
            raise DIError(
                f"{app} is not an AppService instance"
            )

    def find(self, key: str) -> DIObject:
        """Returns DI object by its key.

        Note that searching is made using PascalCased keys, but actual object
        returned is an initialized instance of searched class.

        Args:
            key:
                String value to search with.

        Returns:
            A DIObject found.

        Raises:
            MissingDIObjectError:
                DIObject with given key is not found.
        """
        return self._container.find(key)
