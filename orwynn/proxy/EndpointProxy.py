from typing import Callable, ItemsView

from orwynn.base.controller.endpoint.Endpoint import Endpoint
from orwynn.base.controller.endpoint.EndpointNotFoundError import \
    EndpointNotFoundError
from orwynn.base.worker._Worker import Worker
from orwynn.util import validation


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
        except KeyError:
            raise EndpointNotFoundError(
                f"{fn} not found in proxy"
            )
