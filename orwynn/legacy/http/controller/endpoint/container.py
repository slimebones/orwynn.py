from typing import Callable, ItemsView

from pykit import validation

from orwynn.http.errors import EndpointNotFoundError
from orwynn.worker import Worker

from .endpoint import Endpoint


class EndpointContainer(Worker):
    """Collects endpoint specs to be used on routes registering."""
    def __init__(self) -> None:
        super().__init__()
        self.__spec_by_func: dict[Callable, Endpoint] = {}

    @property
    def items(self) -> ItemsView[Callable, Endpoint]:
        return self.__spec_by_func.items()

    def add(self, func: Callable, spec: Endpoint) -> None:
        check.instance(func, Callable)
        check.instance(spec, Endpoint)

        if func in self.__spec_by_func:
            raise ValueError(
                f"{func} already declared for proxy"
            )

        self.__spec_by_func[func] = spec

    def find_spec(self, func: Callable) -> Endpoint:
        check.instance(func, Callable)

        try:
            return self.__spec_by_func[func]
        except KeyError as err:
            raise EndpointNotFoundError(
                f"{func} not found in proxy"
            ) from err
