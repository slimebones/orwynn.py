from orwynn.app.app_service import AppService
from orwynn.base.module.module import Module
from orwynn.base.worker.worker import Worker
from orwynn.di.di_error import DIError
from orwynn.di.objects.di_object import DIObject
from orwynn.di.objects.missing_di_object_error import MissingDIObjectError
from orwynn.util.validation import validate

# DIObjects by their snake_cased names.
_DIContainer = dict[str, DIObject]


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

        self._container: _DIContainer = {}

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

        Keys are converted to snake_case from DI object names. So `AppService`
        becomes `app_service`.

        Args:
            key:
                String value to search with.

        Returns:
            A DIObject found.

        Raises:
            MissingDIObjectError:
                DIObject with given key is not found.
        """
        validate(key, str)

        try:
            return self._container[key]
        except KeyError:
            raise MissingDIObjectError()
