# A request of any supported protocol
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from orwynn.websocket import Websocket
    from orwynn.http import HttpRequest, HttpResponse


GenericRequest = Union[
    "HttpRequest",
    # The Websocket object is a representation of the request
    "Websocket"
]
GenericResponse = Union[
    "HttpResponse",
    # The Websocket protocol doesn't return any response in direct form from a
    # controller - it sends it over special channel instead.
    None
]
