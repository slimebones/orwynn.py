from enum import Enum

import httpx
from fastapi import Request as FastAPIRequest
from fastapi import Response as FastAPIResponse
from fastapi.responses import JSONResponse as FastAPI_JSONResponse
from orwynn.util.web._CORS import CORS

from orwynn.util import validation


class HTTPMethod(Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"
    OPTIONS = "options"


Response = FastAPIResponse
JSONResponse = FastAPI_JSONResponse
Request = FastAPIRequest
TestResponse = httpx.Response


def join_routes(*routes: str) -> str:
    """Joins all given routes and normalize final result."""
    validation.validate_each(routes, str, expected_obj_type=tuple)

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

    return result
