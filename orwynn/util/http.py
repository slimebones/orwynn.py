from fastapi import Response as FastApiResponse
from fastapi import Request as FastApiRequest


class Response(FastApiResponse):
    pass


class Request(FastApiRequest):
    pass
