from enum import Enum
from fastapi import Response as FastApiResponse
from fastapi import Request as FastApiRequest


class HTTPMethod(Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"
    OPTIONS = "options"


class Response(FastApiResponse):
    pass


class Request(FastApiRequest):
    pass
