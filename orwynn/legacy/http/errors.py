from starlette.exceptions import HTTPException as StarletteHTTPException

HttpException = StarletteHTTPException


class UnsupportedHttpMethodError(Exception):
    pass


class EndpointNotFoundError(Exception):
    pass
