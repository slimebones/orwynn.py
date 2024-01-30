# A request of any supported protocol
from typing import TYPE_CHECKING, Union

from orwynn.url import URLMethod, URLScheme

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


REQUEST_METHOD_BY_PROTOCOL: dict[URLScheme, list[URLMethod]] = {
    URLScheme.HTTP: [
        URLMethod.Get,
        URLMethod.Post,
        URLMethod.Put,
        URLMethod.Delete,
        URLMethod.Patch,
        URLMethod.Options,
    ],
    URLScheme.Websocket: [
        URLMethod.Websocket
    ]
}
