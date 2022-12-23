from typing import Callable, ItemsView

from orwynn.base.controller.endpoint.EndpointSpec import EndpointSpec
from orwynn.base.controller.endpoint.EndpointSpecNotFoundError import \
    EndpointSpecNotFoundError
from orwynn.base.worker._Worker import Worker
from orwynn.util import validation


class EndpointSpecsProxy(Worker):
    """Collects endpoint specs to be used on routes registering."""
    def __init__(self) -> None:
        super().__init__()
        self.__spec_by_fn: dict[Callable, EndpointSpec] = {}

    @property
    def items(self) -> ItemsView[Callable, EndpointSpec]:
        return self.__spec_by_fn.items()

    def add(self, fn: Callable, spec: EndpointSpec) -> None:
        validation.validate(fn, Callable)
        validation.validate(spec, EndpointSpec)

        if fn in self.__spec_by_fn:
            raise ValueError(
                f"{fn} already declared for proxy"
            )
        self.__spec_by_fn[fn] = spec

    def find_spec(self, fn: Callable) -> EndpointSpec:
        validation.validate(fn, Callable)

        try:
            return self.__spec_by_fn[fn]
        except KeyError:
            raise EndpointSpecNotFoundError(
                f"{fn} not found in proxy"
            )
