from typing import Callable

from orwynn.base.controller.defined_twice_controller_method_error import \
    DefinedTwiceControllerMethodError
from orwynn.base.controller.missing_controller_class_attribute_error import \
    MissingControllerClassAttributeError
from orwynn.base.middleware.middleware import Middleware
from orwynn.util.http.http import HTTPMethod, TestResponse
from orwynn.util.http.unsupported_http_method_error import \
    UnsupportedHTTPMethodError
from orwynn.util.validation.validation import (validate, validate_each,
                                               validate_route)

ControllerMethodReturnedData = dict | TestResponse


class Controller:
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
        METHODS:
            List of supported HTTP methods to be registered. Methods here can
            be either uppercase or lowercase, e.g. METHODS = ["get", "POST"]
        MIDDLEWARE (optional):
            List of Middleware classes to be applied to this controller.
    """
    ROUTE: str | None = None
    METHODS: list[str] | None = None
    MIDDLEWARE: list[Middleware] | None = None

    def __init__(self, *args) -> None:
        self._methods: list[HTTPMethod] = []

        if self.ROUTE is None:
            raise MissingControllerClassAttributeError(
                "you should set class attribute ROUTE for"
                f" controller {self.__class__}"
            )
        else:
            validate(self.ROUTE, str)
            validate_route(self.ROUTE)

        if self.METHODS is None:
            raise MissingControllerClassAttributeError(
                "you should set class attribute METHODS for"
                f" controller {self.__class__}"
            )
        else:
            validate_each(
                self.METHODS,
                str,
                expected_obj_type=list,
                should_check_if_empty=True
            )
            collected_methods: list[str] = []
            for method in self.METHODS:
                method = method.lower()
                if method not in [e.value for e in HTTPMethod]:
                    raise UnsupportedHTTPMethodError(
                        f"method {method} is not supported"
                    )
                if method in collected_methods:
                    raise DefinedTwiceControllerMethodError(
                        f"method {method} defined twice in controller"
                        f" {self.__class__}"
                    )
                collected_methods.append(method)
                self._methods.append(HTTPMethod(method))

        if self.MIDDLEWARE is None:
            self.MIDDLEWARE = []
        else:
            validate_each(
                self.MIDDLEWARE, Middleware, expected_obj_type=list
            )

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

    def get(self, *args, **kwargs) -> ControllerMethodReturnedData:
        raise NotImplementedError(
            "the method GET is not implemented for controller"
            f" {self.__class__}"
        )

    def post(self, *args, **kwargs) -> ControllerMethodReturnedData:
        raise NotImplementedError(
            "the method POST is not implemented for controller"
            f" {self.__class__}"
        )

    def put(self, *args, **kwargs) -> ControllerMethodReturnedData:
        raise NotImplementedError(
            "the method PUT is not implemented for controller"
            f" {self.__class__}"
        )

    def delete(self, *args, **kwargs) -> ControllerMethodReturnedData:
        raise NotImplementedError(
            "the method DELETE is not implemented for controller"
            f" {self.__class__}"
        )

    def patch(self, *args, **kwargs) -> ControllerMethodReturnedData:
        raise NotImplementedError(
            "the method PATCH is not implemented for controller"
            f" {self.__class__}"
        )

    def options(self, *args, **kwargs) -> ControllerMethodReturnedData:
        raise NotImplementedError(
            "the method OPTIONS is not implemented for controller"
            f" {self.__class__}"
        )
