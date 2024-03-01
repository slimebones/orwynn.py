from typing import Callable, ClassVar, Literal

from orwynn.helpers.web import REQUEST_METHOD_BY_PROTOCOL
from orwynn.url import URLMethod

from .endpoint.endpoint import Endpoint
from orwynn.controller.controller import Controller
from orwynn.url import URLScheme
from orwynn.http.errors import UnsupportedHttpMethodError
from .errors import \
    DefinedTwiceControllerMethodError
from orwynn.controller.errors import \
    MissingControllerClassAttributeError
from .endpoint.container import EndpointContainer
from pykit import validation


class HttpController(Controller):
    """Handles incoming requests and returns responses to the client.

    Calls service or different services under the hood to prepare a response.

    Controller is not a Provider, and it has lower priority than Service which
    means services can be easily injected into controller to be used.

    Controller should be assigned at according Module.controllers field to be
    initialized and registered.

    Class-Attributes:
        Route:
            A subroute of Module's route (where controller attached) which
            controller will answer to. This attribute is required to be
            defined in subclasses explicitly or an error will be raised.
            It is allowed to be "/" to handle Module's root route requests.
        Endpoints:
            List of endpoints enabled in this controller.
        Version (optional):
            An API version the controller supports. Defaults to the latest one.
    """
    Route: ClassVar[str | None] = None
    Endpoints: ClassVar[list[Endpoint] | None] = None
    Version: ClassVar[int | set[int] | Literal["*"] | None] = None

    def __init__(self) -> None:
        super().__init__()

        self._methods: list[URLMethod] = []

        if self.Endpoints is None:
            raise MissingControllerClassAttributeError(
                "you should set class attribute Endpoints for"
                f" controller {self.__class__}"
            )
        else:
            check.instance_each(
                self.Endpoints,
                Endpoint,
                expected_sequence_type=list,
                should_check_if_empty=True
            )
            collected_str_methods: list[str] = []
            for endpoint in self.Endpoints:
                str_method = endpoint.method.lower()

                http_methods: list[str] = [
                    method.value
                    for method in REQUEST_METHOD_BY_PROTOCOL[URLScheme.HTTP]
                ]
                if str_method not in http_methods:
                    raise UnsupportedHttpMethodError(
                        f"method {str_method} is not supported"
                    )
                if str_method in collected_str_methods:
                    raise DefinedTwiceControllerMethodError(
                        f"method {str_method} is defined twice for"
                        f" controller {self.__class__}"
                    )

                collected_str_methods.append(str_method)
                http_method: URLMethod = URLMethod(str_method)

                if (
                    http_method
                    not in REQUEST_METHOD_BY_PROTOCOL[URLScheme.HTTP]
                ):
                    raise ValueError(f"cannot accept method {http_method}")

                self._methods.append(http_method)

                EndpointContainer.ie().add(
                    self.get_func_by_http_method(http_method),
                    endpoint
                )

    @property
    def route(self) -> str:
        return self._route

    @property
    def methods(self) -> list[URLMethod]:
        return self._methods

    def has_method(self, method: URLMethod):
        return method in self.methods

    def get_func_by_http_method(self, method: URLMethod) -> Callable:
        func: Callable

        match method:
            case URLMethod.Get:
                func = self.get
            case URLMethod.Post:
                func = self.post
            case URLMethod.Put:
                func = self.put
            case URLMethod.Delete:
                func = self.delete
            case URLMethod.Patch:
                func = self.patch
            case URLMethod.Options:
                func = self.options
            case _:
                raise

        return func

    def get(self, *args, **kwargs) -> dict:
        raise NotImplementedError(
            "the method GET is not implemented for controller"
            f" {self.__class__}"
        )

    def post(self, *args, **kwargs) -> dict:
        raise NotImplementedError(
            "the method POST is not implemented for controller"
            f" {self.__class__}"
        )

    def put(self, *args, **kwargs) -> dict:
        raise NotImplementedError(
            "the method PUT is not implemented for controller"
            f" {self.__class__}"
        )

    def delete(self, *args, **kwargs) -> dict:
        raise NotImplementedError(
            "the method DELETE is not implemented for controller"
            f" {self.__class__}"
        )

    def patch(self, *args, **kwargs) -> dict:
        raise NotImplementedError(
            "the method PATCH is not implemented for controller"
            f" {self.__class__}"
        )

    def options(self, *args, **kwargs) -> dict:
        raise NotImplementedError(
            "the method OPTIONS is not implemented for controller"
            f" {self.__class__}"
        )
