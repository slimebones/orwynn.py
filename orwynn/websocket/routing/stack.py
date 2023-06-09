import functools
from typing import Callable

from orwynn.base.error.errors import MalfunctionError
from orwynn.utils import url
from orwynn.websocket.websocket import Websocket

from .handlers import DispatchWebsocketHandler, WebsocketHandler
from .nextcall import NextCallHandler


class WebsocketStack:
    """
    Manages an order of calls on websocket's request way through middleware and
    controllers.

    Call stack is built from handler functions and their routes to respond to.
    These functions called one by one for each request according to the order
    they were inserted.

    These functions may be either WebsocketMiddleware.dispatch methods or
    certain WebsocketController methods.

    Attributes:
        handler_register:
            Registration entity for websocket handlers.
    """
    def __init__(
        self,
        handler_register: Callable
    ) -> None:
        self.__handler_register: Callable = handler_register
        self.__handlers_by_route: dict[str, list[WebsocketHandler]] = {}
        self.__is_registered: bool = False

    def add_call(
        self,
        handler: WebsocketHandler
    ) -> None:
        """
        Adds a call to the stack.

        Note that handler's route can be wildcard "*", i.e. this handler will
        process all routes, and it should be Middleware-based (have a dispatch
        function). The wildcarded Middleware always called before other route
        handlers.

        Also there is an error raised, if a dispatch handler is placed
        after non-dispatch handler for any route provided.

        Args:
            handler:
                Webscoket handler object to add.
        """
        if self.__is_registered:
            raise ValueError(
                "the stack has been already registered"
            )

        if handler.route not in self.__handlers_by_route:
            self.__handlers_by_route[handler.route] = []
        # Here we should be sure that the list for the route is not only
        # initialized, but also is populated with at least one value
        elif len(self.__handlers_by_route[handler.route]) < 1:
            raise MalfunctionError(
                f"handler list for route {handler.route} is initialized"
                " but no values are added, but should be at least one"
            )
        elif (
            isinstance(handler, DispatchWebsocketHandler)
            # Check only last handler (i.e. previously added) in the list
            and not isinstance(
                self.__handlers_by_route[handler.route][-1],
                DispatchWebsocketHandler
            )
        ):
            raise ValueError(
                f"cannot insert dispatch handler {handler} for route"
                f" {handler.route}, since previously non-dispatch handler"
                f" {self.__handlers_by_route[handler.route][-1]}"
                " has been already inserted"
            )

        self.__handlers_by_route[handler.route].append(handler)

    def register_all(
        self
    ) -> None:
        """
        Registers entrypoints to the websocket handlers.

        After calling of this method no more adds are allowed.
        """
        # Check wildcard route consists of only dispatch handlers
        if not all([
            isinstance(handler, DispatchWebsocketHandler)
            for handler in self.__handlers_by_route["*"]
        ]):
            raise ValueError(
                "wildcard handlers have non-dispatch based handler"
            )

        # For every route register the entry Connection middleware.
        for route, handlers in self.__handlers_by_route.items():
            # Skip wildcard routes since they cannot contain final generic
            # handler
            if route == "*":
                continue

            # Non-wildcard route handlers shouldn't contain dispatch handlers
            if not all([
                not isinstance(handler, DispatchWebsocketHandler)
                for handler in handlers
            ]):
                raise ValueError(
                    f"non-wildcard route {route} handlers shouldn't"
                    " contain dispatch handlers"
                )

            # List of final handlers to be registered should consist of
            # wildcard handlers first, and only then of other generic ones.
            final_handlers: list[WebsocketHandler] = \
                self.__handlers_by_route["*"] + handlers
            self.__handler_register(route)(functools.partial(
                self.__handle_entry,
                _fw_handlers=final_handlers,
                _fw_original_route=route
            ))
        self.__is_registered = True

    async def __handle_entry(
        self,
        websocket: Websocket,
        *,
        _fw_handlers: list[WebsocketHandler],
        _fw_original_route: str
    ) -> None:
        # Execute all handlers consequently, but delegate such execution inside
        # the registered middleware
        first_handler: WebsocketHandler = _fw_handlers[0]

        # Collect request kwargs from url
        url_vars: url.UrlVars = url.get_vars(
            websocket.url,
            abstract_route=_fw_original_route
        )

        # For middleware pass special NextCallHandler with data of all handler
        # functions ahead, except first one which is executed first.
        if isinstance(first_handler, DispatchWebsocketHandler):
            await first_handler.fn(
                websocket,
                NextCallHandler(_fw_handlers[1:], url_vars=url_vars)
            )
        # For all other generic cases, we might just call with only websocket
        # passed. But this situation rarely possible since we have added
        # BuiltinMiddleware (at least one), so here we will raise an error.
        else:
            raise MalfunctionError(
                "expected middleware as the first handler (due to builtin"
                " middlewares adding by default), but got handler"
                f" {first_handler} instead"
            )
