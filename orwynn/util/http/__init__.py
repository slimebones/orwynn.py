from enum import Enum
from fastapi import Response as FastApiResponse
from fastapi import Request as FastApiRequest
import httpx


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
