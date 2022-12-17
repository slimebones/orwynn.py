from enum import Enum

import httpx
from fastapi import Request as FastApiRequest
from fastapi import Response as FastApiResponse


class HTTPMethod(Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"
    OPTIONS = "options"


TestResponse = FastApiResponse
Request = FastApiRequest
TestResponse = httpx.Response
