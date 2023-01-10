from typing import Callable, ItemsView

from orwynn import validation
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.endpoint.EndpointNotFoundError import (
    EndpointNotFoundError,
)
from orwynn.worker.Worker import Worker


class EndpointProxy(Worker):
    """Collects endpoint specs to be used on routes registering."""
    def __init__(self) -> None:
        super().__init__()
        self.__spec_by_fn: dict[Callable, Endpoint] = {}

    @property
    def items(self) -> ItemsView[Callable, Endpoint]:
        return self.__spec_by_fn.items()

    def add(self, fn: Callable, spec: Endpoint) -> None:
        validation.validate(fn, Callable)
        validation.validate(spec, Endpoint)

        if fn in self.__spec_by_fn:
            raise ValueError(
                f"{fn} already declared for proxy"
            )

        self.__spec_by_fn[fn] = spec

    def find_spec(self, fn: Callable) -> Endpoint:
        validation.validate(fn, Callable)

        try:
            return self.__spec_by_fn[fn]
        except KeyError as err:
            raise EndpointNotFoundError(
                f"{fn} not found in proxy"
            ) from err
