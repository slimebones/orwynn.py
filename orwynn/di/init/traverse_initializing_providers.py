# import inspect

# from orwynn.base.config.config import Config
# from orwynn.base.model.model import Model
# from orwynn.base.module.module import Module
# from orwynn.base.service.framework_service import FrameworkService
# from orwynn.di.circular_dependency_error import CircularDependencyError
# from orwynn.di.di_object.di_container import DIContainer
# from orwynn.di.di_object.is_provider import is_provider
# from orwynn.di.collecting.not_provider_error import NotProviderError
# from orwynn.di.di_object.provider import Provider
# from orwynn.di.collecting.provider_not_available_error import \
#     ProviderNotAvailableError
# from orwynn.util.fmt import format_chain

# _ProviderParameters = list["_ProviderParameter"]


# class _ProviderParameter(Model):
#     name: str
#     RequiredProvider: type[Provider]


# def traverse_initializing_providers(
#     container: DIContainer,
#     modules: list[Module],
#     FrameworkServices: list[type[FrameworkService]]
# ) -> None:
#     """Collects providers traversing them with immediate initialization.

#     Given container object is populated with initialized providers.

#     Args:
#         container:
#             DI container to populate with initialized providers.
#         modules:
#             List of modules to collect providers from.
#         FrameworkServices:
#             Framework-level services to collect first.
#     """
#     pass
