import inspect

from orwynn.base.config import Config
from orwynn.base.model.model import Model
from orwynn.di.collecting.errors import (
    ProviderKeywordAttributeError,
)
from orwynn.di.errors import NoAnnotationError, NotProviderError
from orwynn.di.isprovider import is_provider
from orwynn.di.provider import Provider

ProviderParameters = list["ProviderParameter"]


class ProviderParameter(Model):
    name: str
    DependencyProvider: type[Provider]


def get_parameters_for_provider(
    P: type[Provider]
) -> ProviderParameters:
    # Inspects the provider and returns requested by it parameters.

    parameters: ProviderParameters = []

    for inspect_parameter in inspect.signature(P).parameters.values():
        if inspect_parameter.annotation is inspect._empty:
            raise NoAnnotationError(
                f"provider {P} has field \"{inspect_parameter.name}\" without"
                " annotation"
            )

        if (
            inspect_parameter.kind is inspect._ParameterKind.KEYWORD_ONLY
            and not issubclass(P, Config)
        ):
            raise ProviderKeywordAttributeError(
                f"provider {P} cannot have keyword only attributes"
            )

        # Comply to Liskov's principle - don't raise an error for *args and
        # **kwargs to be substitutable with base classes.
        # And yes, i haven't found any way to check if requested argument is
        # an either *positional or **keyword spreading, so conventional names
        # are checked.
        if inspect_parameter.name in ["args", "kwargs"]:
            continue

        # Note that on this stage all config parameters (even not providers) is
        # added, and later on additional checks is performed. Actually this
        # doesn't have much sense to not filter such non-provider parameters
        # here, and in future it might be refactored. But from other side it
        # might be useful later on to perform additional logic in DI's scope
        # on Config's non-provider fields, such as checking if it is not
        # waiting for other providers but i'm not sure that it's the case.

        if type(inspect_parameter.annotation) is str:
            raise NotImplementedError(
                "future string references,"
                f" like \"{inspect_parameter.annotation}\""
                f" in field \"{inspect_parameter.name}\""
                f" of provider {P}"
                " are not supported for now"
            )

        if (
            not inspect.isclass(inspect_parameter.annotation)
            or not is_provider(inspect_parameter.annotation)
        ):
            if issubclass(P, Config):
                continue
            else:
                raise NotProviderError(
                    f"argument annotation {inspect_parameter.annotation}"
                    f" for provider {P} should be provider"
                )

        parameters.append(
            ProviderParameter(
                name=inspect_parameter.name,
                DependencyProvider=inspect_parameter.annotation
            )
        )

    return parameters
