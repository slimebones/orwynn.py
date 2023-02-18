from enum import Enum
from typing import Union

import httpx
from fastapi import Request as FastAPIRequest
from fastapi import Response as FastAPIResponse
from fastapi.responses import HTMLResponse as FastAPI_HTMLResponse
from fastapi.responses import JSONResponse as FastAPI_JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from orwynn import validation
from orwynn.web.context.ContextStorage import ContextStorage
from orwynn.web.CORS import CORS
from orwynn.web.Protocol import Protocol
from orwynn.web.websocket.Websocket import Websocket

from .UnsupportedHTTPMethodError import UnsupportedHTTPMethodError


class HTTPMethod(Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"
    OPTIONS = "options"


Response = FastAPIResponse
JsonResponse = FastAPI_JSONResponse
HtmlResponse = FastAPI_HTMLResponse
Request = FastAPIRequest
TestResponse = httpx.Response
HttpException = StarletteHTTPException

# A request of any supported protocol
GenericRequest = Union[
    Request,
    # The Websocket object is a representation of the request
    Websocket
]
GenericResponse = Union[
    Response,
    # The Websocket protocol doesn't return any response in direct form from a
    # controller - it sends it over special channel instead.
    None
]


def join_routes(*routes: str) -> str:
    """Joins all given routes and normalize final result."""
    validation.validate_each(routes, str, expected_sequence_type=tuple)

    result: str = ""

    for route in routes:
        if route.count("/") > 2:
            raise ValueError(
                f"unconsistent use of slashes in route {route}"
            )
        elif route == "" or route == "/":
            continue
        elif route[0] != "/":
            result += "/" + route
        else:
            result += route
        result.removesuffix("/")

    if result == "":
        result = "/"

    return result
