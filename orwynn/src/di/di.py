import inspect

from orwynn.src.base.model.model import Model
from orwynn.src.base.module.module import Module
from orwynn.src.base.module.root_module import RootModule
from orwynn.src.base.worker.worker import Worker
from orwynn.src.di.collect_modules import collect_modules
from orwynn.src.di.collect_providers import collect_providers
from orwynn.src.util.types.provider import Provider

ProviderParameters = list["Parameter"]
ParametersByProvider = dict[Provider, ProviderParameters]


class Parameter(Model):
    name: str
    tp: type


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
    def __init__(self, root_module: RootModule) -> None:
        super().__init__()

        collect_providers(
            collect_modules(root_module)
        )

    def _get_parameters_for_provider(
      self, provider: Provider
    ) -> ProviderParameters:
        """Inspects provider and returns requested by him parameters."""
        return [
        Parameter(name=inspect_parameter.name, tp=inspect_parameter.annotation)  
            for inspect_parameter in
            inspect.signature(provider).parameters.values()
        ]