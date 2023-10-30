from typing import Callable, ClassVar, Literal

from orwynn.helpers.web import REQUEST_METHOD_BY_PROTOCOL, RequestMethod

from .endpoint.endpoint import Endpoint
from orwynn.base.controller.controller import Controller
from orwynn.utils.scheme import Scheme
from orwynn.http.errors import UnsupportedHttpMethodError
from .errors import \
    DefinedTwiceControllerMethodError
from orwynn.base.controller.errors import \
    MissingControllerClassAttributeError
from .endpoint.container import EndpointContainer
from orwynn.utils import validation


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

        self._methods: list[RequestMethod] = []

        if self.Endpoints is None:
            raise MissingControllerClassAttributeError(
                "you should set class attribute Endpoints for"
                f" controller {self.__class__}"
            )
        else:
            validation.validate_each(
                self.Endpoints,
                Endpoint,
                expected_sequence_type=list,
                should_check_if_empty=True
            )
            collected_str_methods: list[str] = []
            for endpoint in self.Endpoints:
                str_method = endpoint.method.lower()

                http_methods: list[RequestMethod] = [
                    method.value
                    for method in REQUEST_METHOD_BY_PROTOCOL[Scheme.HTTP]
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
                http_method: RequestMethod = RequestMethod(str_method)

                if (
                    http_method
                    not in REQUEST_METHOD_BY_PROTOCOL[Scheme.HTTP]
                ):
                    raise ValueError(f"cannot accept method {http_method}")

                self._methods.append(http_method)

                EndpointContainer.ie().add(
                    self.get_fn_by_http_method(http_method),
                    endpoint
                )

    @property
    def route(self) -> str:
        return self._route

    @property
    def methods(self) -> list[RequestMethod]:
        return self._methods

    def get_fn_by_http_method(self, method: RequestMethod) -> Callable:
        fn: Callable

        match method:
            case RequestMethod.GET:
                fn = self.get
            case RequestMethod.POST:
                fn = self.post
            case RequestMethod.PUT:
                fn = self.put
            case RequestMethod.DELETE:
                fn = self.delete
            case RequestMethod.PATCH:
                fn = self.patch
            case RequestMethod.OPTIONS:
                fn = self.options
            case _:
                raise

        return fn

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
