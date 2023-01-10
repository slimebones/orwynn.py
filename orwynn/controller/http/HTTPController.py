from typing import Callable, ClassVar

from orwynn.controller.Controller import Controller
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.http.DefinedTwiceControllerMethodError import \
    DefinedTwiceControllerMethodError
from orwynn.controller.MissingControllerClassAttributeError import \
    MissingControllerClassAttributeError
from orwynn.proxy.EndpointProxy import EndpointProxy
from orwynn import validation
from orwynn.web import HTTPMethod, UnsupportedHTTPMethodError


class HTTPController(Controller):
    """Handles incoming requests and returns responses to the client.

    Calls service or different services under the hood to prepare a response.

    Controller is not a Provider, and it has lower priority than Service which
    means services can be easily injected into controller to be used.

    Controller should be assigned at according Module.controllers field to be
    initialized and registered.

    Class-attributes:
        ROUTE:
            A subroute of Module's route (where controller attached) which
            controller will answer to. This attribute is required to be
            defined in subclasses explicitly or an error will be raised.
            It is allowed to be "/" to handle Module's root route requests.
        ENDPOINTS:
            List of endpoints enabled in this controller.
    """
    ROUTE: ClassVar[str | None] = None
    ENDPOINTS: ClassVar[list[Endpoint] | None] = None

    def __init__(self) -> None:
        self._methods: list[HTTPMethod] = []

        if self.ROUTE is None:
            raise MissingControllerClassAttributeError(
                "you should set class attribute ROUTE for"
                f" controller {self.__class__}"
            )
        else:
            validation.validate(self.ROUTE, str)
            validation.validate_route(self.ROUTE)
            self._route: str = self.ROUTE

        if self.ENDPOINTS is None:
            raise MissingControllerClassAttributeError(
                "you should set class attribute ENDPOINTS for"
                f" controller {self.__class__}"
            )
        else:
            validation.validate_each(
                self.ENDPOINTS,
                Endpoint,
                expected_sequence_type=list,
                should_check_if_empty=True
            )
            collected_str_methods: list[str] = []
            for endpoint in self.ENDPOINTS:
                str_method = endpoint.method.lower()

                if str_method not in [e.value for e in HTTPMethod]:
                    raise UnsupportedHTTPMethodError(
                        f"method {str_method} is not supported"
                    )
                if str_method in collected_str_methods:
                    raise DefinedTwiceControllerMethodError(
                        f"method {str_method} is defined twice for"
                        f" controller {self.__class__}"
                    )

                collected_str_methods.append(str_method)
                http_method: HTTPMethod = HTTPMethod(str_method)
                self._methods.append(http_method)

                EndpointProxy.ie().add(
                    self.get_fn_by_http_method(http_method),
                    endpoint
                )

    @property
    def route(self) -> str:
        return self._route

    @property
    def methods(self) -> list[HTTPMethod]:
        return self._methods

    def get_fn_by_http_method(self, method: HTTPMethod) -> Callable:
        fn: Callable

        match method:
            case HTTPMethod.GET:
                fn = self.get
            case HTTPMethod.POST:
                fn = self.post
            case HTTPMethod.PUT:
                fn = self.put
            case HTTPMethod.DELETE:
                fn = self.delete
            case HTTPMethod.PATCH:
                fn = self.patch
            case HTTPMethod.OPTIONS:
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
