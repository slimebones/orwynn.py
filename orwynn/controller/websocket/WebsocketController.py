from typing import Any, Callable, ClassVar
from orwynn import validation

from orwynn.controller.Controller import Controller
from orwynn.controller.websocket.WebsocketEventHandler import WebsocketEventHandler


class WebsocketController(Controller):
    """Operates on websocket protocol.

    Subclasses should define class attribute ROUTE signifies route under
    which all operations is made.

    To define subroute operation, define method started with "on_", rest part
    will be transformed into subroute. Note that snake_case names are
    transformed to kebab-case.

    You can define a special method called "main" - it will be assigned under
    controller's namespace itself.

    Note that final route for each websocket controller method consists of
    three things: MODULE_ROUTE + CONTROLLER_ROUTE + METHOD_ROUTE.

    Example:
    ```python
    from orwynn import WebsocketController

    class MyWSController(WebsocketController):
        ROUTE = "/chat"

        def on_connect(...):  # -> "/chat/connect"
            ...

        def on_personal_message(...)  # -> "/chat/personal-message
            ...
    ```
    """
    ROUTE: ClassVar[str | None] = None

    @property
    def event_handlers(self) -> list[WebsocketEventHandler]:
        """Returns all self bound event handlers started with "on_".
        """
        events: list[WebsocketEventHandler] = []

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
                if k == "main":
                    event_name = "main"
                else:
                    event_name = k[3:]

                if event_name == "":
                    raise ValueError(
                        f"malformed websocket controller method {v} name -"
                        f" {event_name}"
                    )

                events.append(WebsocketEventHandler(
                    name=event_name,
                    fn=getattr(self, k)
                ))

        if events == []:
            raise ValueError(
                "no event handlers are defined for websocket"
                f" controller {self}"
            )
        return events
