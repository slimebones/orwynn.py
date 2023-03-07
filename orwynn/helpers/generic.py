# A request of any supported protocol
from enum import Enum
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from orwynn.http import HttpRequest, HttpResponse
    from orwynn.websocket import Websocket


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


class RequestMethod(Enum):
    """
    All possible request methods.
    """
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"
    OPTIONS = "options"
    WEBSOCKET = "websocket"
