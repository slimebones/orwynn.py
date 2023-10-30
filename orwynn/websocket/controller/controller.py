from typing import Callable, ClassVar, Literal

from orwynn.base.controller.controller import Controller
from orwynn.utils import validation
from orwynn.websocket.controller.eventhandlermethod import (
    WebsocketEventHandlerMethod,
)


class WebsocketController(Controller):
    """Operates on websocket protocol.

    Subclasses should define class attribute Route signifies route under
    which all operations is made.

    To define subroute operation, define method started with "on_", rest part
    will be transformed into subroute. Note that snake_case names are
    transformed to kebab-case.

    You can define a special method called "main" - it will be assigned under
    controller's namespace itself (see Example for details).

    Note that final route for each websocket controller method consists of
    three things: MODULE_Route + CONTROLLER_Route + METHOD_Route.

    Class-Attributes:
        Route:
            A subroute of Module's route (where controller attached) which
            controller will answer to. This attribute is required to be
            defined in subclasses explicitly or an error will be raised.
            It is allowed to be "/" to handle Module's root route requests.
        Version (optional):
            An API version the controller supports. Defaults to the latest one.

    Example:
    ```python
    from orwynn import WebsocketController

    class MyWSController(WebsocketController):
        Route = "/chat"

        def main(...):  # -> "/chat"
            ...

        def on_connect(...):  # -> "/chat/connect"
            ...

        def on_personal_message(...)  # -> "/chat/personal-message
            ...
    ```
    """
    Route: ClassVar[str | None] = None
    Version: ClassVar[int | set[int] | Literal["*"] | None] = None

    @classmethod
    def get_handler_subroutes(cls) -> list[str]:
        """Returns subroutes for each defined handler method."""
        subroutes: list[str] = []
        for k in cls.__dict__:
            if k[:3] == "on_" or k == "main":
                subroutes.append(
                    "/" if k == "main" else k.replace("on_", "/")
                )
        return subroutes

    @property
    def event_handlers(self) -> list[WebsocketEventHandlerMethod]:
        """
        Returns all self bound event handlers started with "on_".

        Note that implicitly inherited methods are not included in search. If
        you want to inherit the parent's functionality for a handler,
        use super() with a redefinition of the method.
        """
        events: list[WebsocketEventHandlerMethod] = []

        for k, v in self.__class__.__dict__.items():
            if k[:3] == "on_" or k == "main":
                try:
                    validation.validate(v, Callable)
                except validation.ValidationError as err:
                    raise ValueError(
                        "every websocket controller object starting from"
                        f" \"on_\" or \"main\" should be Callable, but for"
                        f" name {k} got {v} instead"
                    ) from err

                event_name: str
                event_name = "main" if k == "main" else k[3:]

                if event_name == "":
                    raise ValueError(
                        f"malformed websocket controller method {v} name -"
                        f" {event_name}"
                    )

                events.append(WebsocketEventHandlerMethod(
                    name=event_name,
                    # It's important to use "getattr()" here instead of
                    # "v" since last is obtained from class and is not bound to
                    # an instance.
                    fn=getattr(self, k)
                ))

        if events == []:
            raise ValueError(
                "no event handlers are defined for websocket"
                f" controller {self}"
            )
        return events
