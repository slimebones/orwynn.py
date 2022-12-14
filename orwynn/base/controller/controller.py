from typing import Callable
from orwynn.base.controller.missing_controller_route import MissingControllerRoute
from orwynn.base.middleware.middleware import Middleware
from orwynn.http import HTTPMethod, TestResponse
from orwynn.validation import validate, validate_route

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
        MIDDLEWARE:
            List of Middleware classes to be applied to this controller.
    """
    ROUTE: str
    MIDDLEWARE: list[Middleware] = []

    def __init__(self, *args) -> None:
        if self.ROUTE is None:
            raise MissingControllerRoute(
                "you should set class attribute ROUTE for"
                f" controller {self.__class__}"
            )
        else:
            validate(self.ROUTE, str)
            validate_route(self.ROUTE)

    def get_fn_by_http_method(self, method: HTTPMethod) -> Callable:
        match method:
            case HTTPMethod.GET:
                return self.get
            case HTTPMethod.POST:
                return self.post
            case HTTPMethod.PUT:
                return self.put
            case HTTPMethod.DELETE:
                return self.delete
            case HTTPMethod.PATCH:
                return self.patch
            case HTTPMethod.OPTIONS:
                return self.options
            case _:
                raise NotImplementedError()

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
