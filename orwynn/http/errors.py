from starlette.exceptions import HTTPException as StarletteHTTPException

from orwynn.base.error import Error

HttpException = StarletteHTTPException


class UnsupportedHttpMethodError(Error):
    pass


class EndpointNotFoundError(Error):
    pass
