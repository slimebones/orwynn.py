# A request of any supported protocol
from typing import Union

from orwynn.web.http.requests import HttpRequest
from orwynn.web.http.responses import HttpResponse
from orwynn.web.websocket.Websocket import Websocket

GenericRequest = Union[
    HttpRequest,
    # The Websocket object is a representation of the request
    Websocket
]
GenericResponse = Union[
    HttpResponse,
    # The Websocket protocol doesn't return any response in direct form from a
    # controller - it sends it over special channel instead.
    None
]
