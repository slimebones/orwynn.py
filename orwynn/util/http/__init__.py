from enum import Enum

import httpx
from fastapi import Request as FastAPIRequest
from fastapi import Response as FastAPIResponse
from fastapi.responses import JSONResponse as FastAPI_JSONResponse


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
